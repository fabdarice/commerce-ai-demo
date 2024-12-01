from dotenv import load_dotenv
from langchain_core import messages
from langchain_openai import ChatOpenAI

from app.agent import Agent
from app.state.state import AgentState

_ = load_dotenv()


model = ChatOpenAI(model="gpt-4o-mini-2024-07-18")

agent = Agent(model, [])
agent.init_graph()


initial_state: AgentState = {"messages": []}

for event in agent.graph.stream(initial_state):
    for v in event.values():
        print(v)
