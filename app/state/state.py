from typing import List, Optional, TypedDict

from langgraph.graph import add_messages
from langgraph.graph.message import Annotated
from app.state.item import Item


class AgentState(TypedDict):
    item_requested: Optional[Item]
    inventory: Optional[List[Item]]
    messages: Annotated[list, add_messages]
