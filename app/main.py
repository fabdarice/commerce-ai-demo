from typing import List
from uuid import uuid4
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.messages.tool import ToolMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from flask import Flask, request, jsonify
from flask_cors import CORS

from app.agent import Agent
from app.state.state import AgentState
from app.tools.inventory import SearchInventoryTool

_ = load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/agent": {"origins": "*"}}, supports_credentials=True)

SESSION_STATES = {}

model = ChatOpenAI(model="gpt-4o-mini-2024-07-18")
tools: List[BaseTool] = [SearchInventoryTool()]

agent = Agent(model, tools)


@app.route("/agent", methods=["POST", "OPTIONS"])
def agent_route():
    """
    This endpoint is called repeatedly by the client with user input.
    JSON Example:
    {
      "session_id": "...",        # optional, if not provided we create a new session
      "user_input": "iPhone 14"   # or "1", or "y", etc. based on the conversation
    }
    """
    if request.method == "OPTIONS":
        # Preflight request handled by flask-cors
        return jsonify({"status": "OK"}), 200
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
    response_messages = []
    try:
        step_gen = agent.graph.stream(state)
        event = next(step_gen, None)

        if event is None:
            # Means we might already be at the end or no further steps are left
            response_messages.append(
                {"role": "system", "content": "Thank you. Goodbye."}
            )
        else:
            # event is typically a dict of {node_name: result_dict}
            for node_result in event.values():
                if isinstance(node_result, dict) and "messages" in node_result:
                    extracted = node_result["messages"]
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

    except StopIteration:
        response_messages.append(
            {"role": "system", "content": "Conversation has ended."}
        )
    except Exception as e:
        response_messages.append({"role": "system", "content": f"Error: {str(e)}"})

    # Persist updated state
    SESSION_STATES[session_id] = state

    return jsonify({"session_id": session_id, "messages": response_messages})


if __name__ == "__main__":
    app.run(debug=True)
