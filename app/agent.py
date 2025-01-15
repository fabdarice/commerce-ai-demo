from typing import List

from langchain_core.tools import BaseTool
from langchain_openai.chat_models import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai.chat_models import ChatOpenAI

from app.prompts.customer_request_prompt import CUSTOMER_REQUEST_PROMPT
from app.prompts.get_best_match_prompt import GET_BEST_MATCH_PROMPT
from app.state.state import AgentState


class Agent:
    def __init__(self, model: ChatOpenAI, tools: List[BaseTool], system_msg=""):
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools=tools, tool_choice="auto")
        self.system_msg = system_msg

    def init_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("purchase_request_node", self.customer_request)
        graph.add_node("extract_item_node", self.extract_item)
        graph.add_node("get_best_match_node", self.get_best_match)
        graph.add_conditional_edges(
            "purchase_request_node",
            self.is_extract_item,
            {True: "extract_item_node", False: "purchase_request_node"},
        )
        graph.add_edge("extract_item_node", "get_best_match_node")
        graph.set_entry_point("purchase_request_node")
        graph.set_finish_point("get_best_match_node")
        self.graph = graph.compile(
            # interrupt_before=[
            #     "action"
            # ],  # Add an interrupt before the action node (i.e: we can add manual approval before running a tool)
        )

    def customer_request(self, state: AgentState):
        if state["messages"]:
            print(state["messages"][-1].content)
        else:
            greeting = "Hello! What are you looking to purchase today?"
            print(greeting)  # Display the greeting to the user

        messages = [
            SystemMessage(content=CUSTOMER_REQUEST_PROMPT),
            HumanMessage(content=input()),
        ]

        try:
            result = self.model.invoke(messages)
            return {"messages": [result]}
        except Exception as e:
            print(f"Error in calling tool: {e}")
            raise

    def extract_item(self, state: AgentState):
        print("----- Extract Item -------")
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

    def get_best_match(self, state: AgentState):
        print("--------------- GET BEST MATCH FROM INVENTORY-------------")
        # Ensure the last message is a ToolMessage and extract its content
        last_message = state["messages"][-1]
        if isinstance(last_message, ToolMessage):
            content = last_message.content
        else:
            raise ValueError("Expected the last message to be a ToolMessage")

        messages = [
            SystemMessage(content=GET_BEST_MATCH_PROMPT),
            HumanMessage(content=content),
        ]

        try:
            result = self.model.invoke(messages)
            print(f"GET BEST MATCH Result: {result}")
            return {"messages": [result]}
        except Exception as e:
            print(f"Error in calling LLM: {e}")
            raise

    def is_extract_item(self, state: AgentState):
        print("--- ITEM REQUESTED ACTION ---")
        last_message = state["messages"][-1]

        if isinstance(last_message, AIMessage):
            print("AIMessage tool_calls:", last_message.tool_calls)
            print("AIMessage additional_kwargs:", last_message.additional_kwargs)

        # More robust check for tool calls
        has_tool_calls = (
            isinstance(last_message, AIMessage)
            and hasattr(last_message, "tool_calls")
            and len(last_message.tool_calls) > 0
        )
        return has_tool_calls
