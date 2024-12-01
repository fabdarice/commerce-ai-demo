from langchain_core.tools import Tool
from langchain_openai.chat_models import ChatOpenAI
from langgraph.graph import StateGraph, END

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai.chat_models import ChatOpenAI

from typing import List

from app.prompts.customer_request_prompt import CUSTOMER_REQUEST_PROMPT
from app.state.state import AgentState


class Agent:
    def __init__(self, model: ChatOpenAI, tools: List[Tool], system_msg=""):
        self.tools = {t.name: t for t in tools}
        self.model = model

        self.system_msg = system_msg

    def init_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("purchase_request", self.customer_request_node)
        graph.set_entry_point("purchase_request")
        graph.set_finish_point("purchase_request")
        self.graph = graph.compile()

    def customer_request_node(self, state: AgentState):
        print("Hello my friend. What would you like to buy today?")
        messages = [SystemMessage(content=CUSTOMER_REQUEST_PROMPT)] + state["messages"]
        user_input = input()
        messages += [HumanMessage(content=user_input)]
        result = self.model.invoke(messages)
        return {"messages": result}
