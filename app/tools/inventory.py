from langchain_core.tools import BaseTool
from typing import Optional, Type

from pydantic import BaseModel, Field


class SearchInventoryInput(BaseModel):
    item: str = Field(description="Item name")
    max_price: Optional[str] = Field(None, description="Max Price for the item")
    deadline: Optional[str] = Field(
        None, description="Shipping deadline to receive the item"
    )


class SearchInventoryTool(BaseTool):
    name: str = "search_inventory"
    description: str = (
        "Search the inventory for an existing item based on a price and delivery timeframe"
    )
    args_schema: Type[BaseModel] = SearchInventoryInput

    def _run(
        self, item: str, max_price: Optional[int] = None, deadline: Optional[str] = None
    ):
        print(
            f"Searching inventory for {item} with max_price {max_price} and deadline {deadline}"
        )

        # Your actual inventory search logic here
        return f"Searching inventory for {item} with max_price {max_price} and deadline {deadline}"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported")
