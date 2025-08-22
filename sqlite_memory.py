import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph

# Create connection manually
conn = sqlite3.connect("talha.db", check_same_thread=False)
memory = SqliteSaver(conn)

def chatnode(state: State):
    return {"messages": [gemini.invoke(state["messages"])]}

# Rest of your code remains the same
graph = StateGraph(State).add_node(chatnode).set_entry_point("chatnode").compile(checkpointer=memory)
config = {"configurable": {"thread_id": "2"}}

while True:
    user_message = input("Enter your message: ")
    print("User:", user_message)
    
    if user_message.lower() in ['q', 'quit', 'bye', 'exit']:
        break
    
    # Convert string to HumanMessage
    response = graph.invoke(
        {"messages": [HumanMessage(content=user_message)]}, 
        config
    )
    
    print("AI:", response['messages'][-1].content)
