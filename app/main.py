from typing import List
from IPython.display import Image, display
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from app.agent import Agent
from app.tools.charge_management import CreateChargeTool
from app.tools.inventory import SearchInventoryTool

_ = load_dotenv()


model = ChatOpenAI(model="gpt-4o-mini-2024-07-18")
tools: List[BaseTool] = [SearchInventoryTool(), CreateChargeTool()]

agent = Agent(model, tools)
agent.init_graph()

#
# message_with_single_tool_call = AIMessage(
#     content="",
#     tool_calls=[
#         {
#             "name": "search_inventory",
#             "args": {
#                 "item": "Iphone Pro",
#                 "max_price": "500",
#                 "deadline": "7 days",
#             },
#             "id": "tool_call_id",
#             "type": "tool_call",
#         }
#     ],
# )
# tool_node = ToolNode(tools)

# tool_node.invoke({"messages": [message_with_single_tool_call]})

#
# display(Image(agent.graph.get_graph().draw_mermaid_png()))
#
initial_input = {"messages": []}

for event in agent.graph.stream(initial_input):
    for v in event.values():
        print(v)
