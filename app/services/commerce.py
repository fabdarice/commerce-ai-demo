import os
import requests

from app.data.web3_data import TransferIntent
from state.item import Item

api_url = "https://api.commerce.coinbase.com/charges"


class CommerceService:
    def __init__(self) -> None:
        self.api_key = os.getenv("COINBASE_COMMERCE_API_KEY")
        pass

    def create_charge(self, item: Item) -> str:
        print(f"call {api_url}")

        headers = {"Content-Type": "application/json", "X-CC-Api-Key": self.api_key}
        data = {
            "name": item.name,
            "description": item.description,
            "pricing_type": "fixed_price",
            "local_price": {"amount": item.price, "currency": "usd"},
        }

        try:
            # Sending the POST request
            response = requests.post(api_url, headers=headers, json=data)
            # Output the response
            print("Response Charge JSON:", response.json())
            charge_id = response.json()["data"]["id"]
            print("Charge ID:", charge_id)

            return charge_id
        except requests.RequestException as e:
            print(f"Error creating Coinbase charge: {e}")
            raise e

    def transact_onchain(self, charge_id: str, sender: str) -> TransferIntent:
        print(f"call {api_url}/{charge_id}/hydrate")
        headers = {"Content-Type": "application/json", "X-CC-Api-Key": self.api_key}
        data = {"chain_id": 8453, "sender": sender}

        try:
            response = requests.put(
                f"{api_url}/{charge_id}/hydrate",
                headers=headers,
                json=data,
            )

            print("Response Hydrate JSON:", response.json())
            print("Web3 Data", response.json()["data"]["web3_data"])
            web3_data = response.json()["data"]["web3_data"]
            return TransferIntent.extract(web3_data)
        except requests.RequestException as e:
            print(f"Error creating Coinbase charge: {e}")
            raise e
