from typing import List, Dict
from uuid import uuid4
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.messages.tool import ToolMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from flask import Flask, request, jsonify

from app.agent import Agent
from app.state.state import AgentState
from app.tools.inventory import SearchInventoryTool

_ = load_dotenv()

app = Flask(__name__)

SESSION_STATES = {}

model = ChatOpenAI(model="gpt-4o-mini-2024-07-18")
tools: List[BaseTool] = [SearchInventoryTool()]

agent = Agent(model, tools)


@app.route("/agent", methods=["POST"])
def agent_route():
    """
    This endpoint is called repeatedly by the client with user input.
    JSON Example:
    {
      "session_id": "...",        # optional, if not provided we create a new session
      "user_input": "iPhone 14"   # or "1", or "y", etc. based on the conversation
    }
    """
    data = request.get_json() or {}
    session_id = data.get("session_id")
    user_input = data.get("user_input", "")

    # If no session_id, create a new conversation session
    if not session_id or session_id not in SESSION_STATES:
        session_id = str(uuid4())
        SESSION_STATES[session_id] = {"messages": []}

    state = SESSION_STATES[session_id]

    # If user_input is present, treat it as a new HumanMessage
    if user_input.strip():
        state["messages"].append(HumanMessage(content=user_input))

    # ---- Now run the next "step" in the graph ----
    # The graph is compiled as a generator. We'll advance it by a single step,
    # capturing the output. If we are at the finish node, we won't proceed further.
    response_messages = []
    try:
        # The .stream(...) returns a generator that yields node transitions
        # We'll just do a single iteration to move one step forward.
        step_gen = agent.graph.stream(state)
        event = next(step_gen, None)

        if event is None:
            # Means we might already be at the end or no further steps are left
            response_messages.append(
                {"role": "system", "content": "Thank you. Goodbye."}
            )
        else:
            # event is typically a dict of {node_name: result_dict}
            # We'll accumulate the node's output messages
            for node_result in event.values():
                print("node_result: ", node_result)
                # node_result might be a list or dict with "messages"
                # Flatten them into a single list to return
                if isinstance(node_result, dict) and "messages" in node_result:
                    extracted = node_result["messages"]
                    print("extracted: ", extracted)
                    # extracted can be a list of str/dict or LLM Message objects
                    # unify them into a simpler JSON-friendly shape:
                    for msg in extracted:
                        if isinstance(msg, (AIMessage, ToolMessage)):
                            response_messages.append(
                                {"role": "assistant", "content": str(msg.content)}
                            )
                        elif isinstance(msg, dict):
                            # we inserted logs as dicts
                            response_messages.append(msg)
                        else:
                            response_messages.append(
                                {"role": "assistant", "content": str(msg)}
                            )
                else:
                    print("pass")
                    # Also handle scenario: node_result might directly have the info
                    # or updates like "best_matches", "selected_item" etc.
                    pass

    except StopIteration:
        # Means the graph may have finished all steps in a single iteration
        response_messages.append(
            {"role": "system", "content": "Conversation has ended."}
        )
    except Exception as e:
        response_messages.append({"role": "system", "content": f"Error: {str(e)}"})

    # Persist updated state
    SESSION_STATES[session_id] = state

    return jsonify({"session_id": session_id, "messages": response_messages})


if __name__ == "__main__":
    # Run Flask in debug mode (or not)
    app.run(debug=True)
