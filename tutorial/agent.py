from typing import Annotated, List, TypedDict
from uuid import uuid4
from langchain_core.messages import SystemMessage, ToolMessage, AnyMessage
import operator

from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph


# Look for messages with the same ID and if it sees you're isnerting one with the same ID, it will replace it
# Likely used when there's some user input
def reduce_messages(
    left: list[AnyMessage], right: list[AnyMessage]
) -> list[AnyMessage]:
    # assign ids to messages that don't have them
    for message in right:
        if not message.id:
            message.id = str(uuid4())
    # merge the new messages with the existing messages
    merged = left.copy()
    for message in right:
        for i, existing in enumerate(merged):
            # replace any existing messages with the same id
            if existing.id == message.id:
                merged[i] = message
                break
        else:
            # append any new messages to the end
            merged.append(message)
    return merged


class AgentState(TypedDict):
    messages: Annotated[List[SystemMessage | ToolMessage], reduce_messages]


class Agent:
    def __init__(
        self, model: ChatOpenAI, tools: List[BaseTool], checkpointer, system=""
    ):  # <1>
        self.system = system
        graph = StateGraph(AgentState)
        graph.add_node("llm", self.call_openai)
        graph.add_node("action", self.take_action)
        graph.add_conditional_edges(
            "llm", self.exists_action, {True: "action", False: END}
        )
        graph.add_edge("action", "llm")
        graph.set_entry_point("llm")
        self.graph = graph.compile(
            checkpointer=checkpointer,
            interrupt_before=[
                "action"
            ],  # Add an interrupt before the action node (i.e: we can add manual approval before running a tool)
        )  # turn into a Langchain runnable
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)

    def call_openai(self, state: AgentState):
        messages = state["messages"]
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        message = self.model.invoke(messages)
        return {"messages": [message]}

    def take_action(self, state: AgentState):
        tool_calls = state["messages"][-1].tool_calls
        results = []
        for t in tool_calls:
            if not t["name"] in self.tools:  # check for bad tool name from LLM
                print("\n ....bad tool name....")
                result = "bad tool name, retry"  # instruct LLM to retry if bad
            else:
                print(f"--- BEGIN Action ---")
                print(f"   {t}")
                result = self.tools[t["name"]].invoke(t["args"])
                print(f"   Tool response: {result}")
                print(f"--- END Action ---")

            results.append(
                ToolMessage(tool_call_id=t["id"], name=t["name"], content=str(result))
            )
        return {"messages": results}

    def exists_action(self, state: AgentState):
        result = state["messages"][-1]
        return len(result.tool_calls) > 0
