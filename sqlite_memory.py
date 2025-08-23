import os 
import sqlite3

from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, MessagesState
from langchain.chat_models import init_chat_model

# load dotenv 
load_dotenv()

# declare llm 
llm = init_chat_model(model="gemini-2.5-flash-lite", model_provider="google_genai", api_key=os.getenv("GEMINI_API_KEY"))

# Create connection manually
conn = sqlite3.connect("talha.db", check_same_thread=False)
memory = SqliteSaver(conn)

def chatnode(state: MessagesState):
    return {"messages": [llm.invoke(state["messages"])]}

# Rest of your code remains the same
graph = StateGraph(MessagesState).add_node(chatnode).set_entry_point("chatnode").compile(checkpointer=memory)
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
