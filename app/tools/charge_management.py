import os
from langchain_core.tools import BaseTool
from typing import Type

from pydantic import BaseModel, Field
import requests
import json


class CreateChargeInput(BaseModel):
    product_id: str = Field(description="Product Id for the item")
    amount: str = Field(description="Max Price for the item")


class CreateChargeTool(BaseTool):
    name: str = "create_charge"
    description: str = "Create a charge in Coinbase Commerce for a specified item"
    args_schema: Type[BaseModel] = CreateChargeInput

    def _run(self, product_id: str, amount: str):
        """
        Create a Coinbase Commerce charge

        :param product_id: The product ID of the item
        :param amount: The price amount as a string
        :return: The charge ID if successful, None otherwise
        """
        # Prepare the payload
        payload = {
            "checkout_id": product_id,
            "local_price": {"amount": amount, "currency": "usd"},
            "pricing_type": "fixed_price",
        }

        # Headers (you'll need to replace 'YOUR_API_KEY' with your actual Coinbase Commerce API key)
        headers = {
            "Content-Type": "application/json",
            "X-CC-Api-Key": os.getenv("COINBASE_COMMERCE_API_KEY"),
            "X-CC-Version": "2018-03-22",
        }

        try:
            # Make the POST request to create the charge
            response = requests.post(
                "https://api.commerce.coinbase.com/charges",
                data=json.dumps(payload),
                headers=headers,
            )
            response.raise_for_status()
            response_data = response.json()
            charge_id = response_data.get("data", {}).get("id")

            # Make the PUT request for hydrating the charge
            response = requests.put(
                f"https://api.commerce.coinbase.com/charges/{charge_id}/hydrate"
            )
            response.raise_for_status()
            response_data = response.json()

            print(response_data)

            return charge_id

        except requests.RequestException as e:
            print(f"Error creating Coinbase charge: {e}")
            return None

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported")
