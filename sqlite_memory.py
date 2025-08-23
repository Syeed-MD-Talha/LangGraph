import os 
import sqlite3
import atexit

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

# Register cleanup function to ensure proper connection closure
def cleanup():
    try:
        # Checkpoint WAL to merge changes back to main database
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        conn.close()
        print("\nDatabase connection closed properly.")
    except Exception as e:
        print(f"\nError during cleanup: {e}")

# Register cleanup to run when program exits
atexit.register(cleanup)

def chatnode(state: MessagesState):
    return {"messages": [llm.invoke(state["messages"])]}

# Rest of your code remains the same
graph = StateGraph(MessagesState).add_node(chatnode).set_entry_point("chatnode").compile(checkpointer=memory)
config = {"configurable": {"thread_id": "2"}}

try:
    while True:
        user_message = input("Enter your message: ")
        print("User:", user_message)
        
        if user_message.lower() in ['q', 'quit', 'bye', 'exit']:
            cleanup()  # Explicit cleanup on normal exit
            break
        
        # Convert string to HumanMessage
        response = graph.invoke(
            {"messages": [HumanMessage(content=user_message)]}, 
            config
        )
        
        print("AI:", response['messages'][-1].content)

except KeyboardInterrupt:
    print("\n\nProgram interrupted by user.")
    cleanup()  # Cleanup on Ctrl+C
except Exception as e:
    print(f"\nAn error occurred: {e}")
    cleanup()  # Cleanup on any other exception
finally:
    print("Goodbye!")
