from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig

from agent import Agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from IPython.display import Image

_ = load_dotenv()
from langgraph.checkpoint.sqlite import SqliteSaver

tool = TavilySearchResults(max_results=4)  # increased number of results
print(tool.name)

prompt = """You are a smart research assistant. Use the search engine to look up information. \
You are allowed to make multiple calls (either together or in sequence). \
Only look up information when you are sure of what you want. \
If you need to look up some information before asking a follow up question, you are allowed to do that!
"""

model = ChatOpenAI(model="gpt-4o-mini-2024-07-18")  # reduce inference cost

with SqliteSaver.from_conn_string(":memory:") as checkpointer:
    abot = Agent(model, [tool], checkpointer, system=prompt)

    Image(abot.graph.get_graph().draw_ascii())

    messages = [HumanMessage(content="What is the weather in SF?")]

    thread = RunnableConfig(
        configurable={"thread_id": "1"}
    )  # Used to keep track of different thread inside the persistent checkpoint

    for event in abot.graph.stream({"messages": messages}, thread):
        for v in event.values():
            print(v)

    while abot.graph.get_state(thread).next:
        print("\n", abot.graph.get_state(thread), "\n")
        # abot.graph.get_state_history(thread) #  print state history
        # abot.graph.invoke(None, {thread, threadh_ts}) #  invoke from a specific state snapshot in history (Time Travel)
        # abot.graph.stream(None, {thread, threadh_ts}) #  invoke from a specific state snapshot in history (Time Travel)
        # You can modify a state and graph.update_state to update the state
        _input = input("proceed?")
        if _input != "y":
            print("aborting")
            break
        for event in abot.graph.stream(None, thread):
            for v in event.values():
                print(v)

