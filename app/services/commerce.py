import os
import requests

from state.item import Item


class CommerceService:
    def __init__(self) -> None:
        pass

    def create_charge_and_hydrate(self, item: Item, sender):
        api_url = "https://api.commerce.coinbase.com"
        print(f"CALL {api_url}")
        api_key = os.getenv("COINBASE_COMMERCE_API_KEY")
        charge_name = item.name
        charge_description = item.description
        pricing_type = "fixed_price"
        amount = item.price
        currency = "USD"

        # Headers and payload
        headers = {"Content-Type": "application/json", "X-CC-Api-Key": api_key}
        data = {
            "name": charge_name,
            "description": charge_description,
            "pricing_type": pricing_type,
            "local_price": {"amount": amount, "currency": currency},
        }

        try:
            # Sending the POST request
            response = requests.post(f"{api_url}/charges", headers=headers, json=data)
            # Output the response
            print("Response Charge JSON:", response.json())
            charge_id = response.json()["data"]["id"]
            print("Charge ID:", charge_id)

            response = requests.put(
                f"{api_url}/charges/{charge_id}/hydrate",
                headers=headers,
                json={"chain_id": 8453, "sender": sender},
            )

            print("Response Hydrate JSON:", response.json())
            print("Web3 Data", response.json()["data"]["web3_data"])
        except requests.RequestException as e:
            print(f"Error creating Coinbase charge: {e}")
            return None
