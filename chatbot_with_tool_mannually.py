import os  

import sys
from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv 
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage 
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel


#========= Configure llm model =========#
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = init_chat_model(model = "gemini-2.5-flash-lite", model_provider="google_genai", api_key=api_key)

#========= Defines tools =========#
@tool 
def add(a:int, b:int)->int:
    """ This is an addition function that adds 2 numbers together """
    return a+b

@tool
def sub(a:int, b:int)->int:
    """ This function return the substraction result """
    return a-b

@tool
def multiply(a: int, b: int):
    """Multiplication function"""
    return a * b

#========= Configure llm for tool calls =========#
tools = [add,sub,multiply]
llm = model.bind_tools(tools)

#========= Define AgentState and Nodes =========#
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def chatnode(state: AgentState):
    system_prompt = SystemMessage(
        content="You are my AI assistant, please answer my query to the best of your ability."
    )
    response = llm.invoke([system_prompt] + state['messages'])
    return {"messages": [response]}

def check_condition(state: AgentState):
    messages =  state["messages"]
    last_message = messages[-1]

    if not last_message.tool_calls:return "end"
    else: return "continue"

tool_node =  ToolNode(tools=tools)

#========= Define graph and add nodes and edges =========#

graph = StateGraph(AgentState)

graph.add_node("chatnode", chatnode)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chatnode")
graph.add_conditional_edges("chatnode", check_condition, {
    "continue":"tools",
    "end":END
})
graph.add_edge("tools", "chatnode")

app = graph.compile()  

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

inputs = {"messages": [("user", "Add 40 + 2 and then multiply the result by 6. Also tell me a joke please.")]}
print_stream(app.stream(inputs, stream_mode="values"))