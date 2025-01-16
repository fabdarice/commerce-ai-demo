from typing import List, Optional, TypedDict

from langgraph.graph import add_messages
from langgraph.graph.message import Annotated
from app.state.item import Item


class AgentState(TypedDict):
    best_matches: Optional[List[Item]]
    selected_item: Optional[Item]
    messages: Annotated[list, add_messages]
