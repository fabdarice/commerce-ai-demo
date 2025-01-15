from typing import Dict
import os
import json
from langchain_core.tools import BaseTool
from typing import Optional, Type, Dict, Any

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
        "Retrieves the current inventory data to help find matching items. "
        "Returns the full inventory for the LLM to analyze."
    )
    args_schema: Type[BaseModel] = SearchInventoryInput

    def _format_search_criteria(
        self, item: str, max_price: Optional[str], deadline: Optional[str]
    ) -> Dict[str, Any]:
        criteria = {
            "search_criteria": {
                "item_name": item,
                "max_price": max_price if max_price else "Not specified",
                "deadline": deadline if deadline else "Not specified",
            }
        }
        return criteria

    def _run(
        self, item: str, max_price: Optional[str] = None, deadline: Optional[str] = None
    ) -> str:
        try:
            with open(
                os.path.join(os.getcwd(), "app/data/item_inventory.json"), "r"
            ) as file:
                inventory = {"inventory": json.load(file)}
                search_criteria = self._format_search_criteria(
                    item, max_price, deadline
                )

                result = {
                    **inventory,
                    **search_criteria,
                }
                return json.dumps(result)
        except Exception as e:
            return f"Error accessing inventory: {str(e)}"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported")
