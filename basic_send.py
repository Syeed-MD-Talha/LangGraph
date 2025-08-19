from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from typing import TypedDict, List, Literal, Annotated 
import operator


class BasicState(TypedDict):
    message: str 
    result: str


def router(state: BasicState):
    """ Router that decides which processor to send to """
    message = state['message']

    if 'urgent' in message:
        return Send("urgent_processor", state)
    elif "normal" in message:
        return Send("normal_processor", state)
    else:
        return Send("default_processor", state)
    
def urgent_processor(state: BasicState):
    return {"result": f"🚨 URGENT: {state['message']}"}

def normal_processor(state: BasicState):
    return {"result": f"📝 Normal: {state['message']}"}

def default_processor(state: BasicState):
    return {"result": f"💭 Default: {state['message']}"}



workflow = StateGraph(BasicState)

workflow.add_node(router)
workflow.add_node(urgent_processor)
workflow.add_node(normal_processor)
workflow.add_node(default_processor)


workflow.add_edge(START, "router")
workflow.add_edge("urgent_processor", END)
workflow.add_edge("normal_processor", END)
workflow.add_edge("default_processor", END)

app = workflow.compile()

app


result = app.invoke({"message":"This is very normal message"})
result
