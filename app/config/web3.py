from typing import List, Dict, Any
import os
import json

from cdp import Cdp, Wallet


class Web3:
    def __init__(self) -> None:
        api_key_name = os.getenv("COINBASE_CDP_API_KEY_NAME")
        api_key_private_key = os.getenv("COINBASE_CDP_SECRET")
        wallet_id = os.getenv("COINBASE_CDP_WALLET_ID")

        if not api_key_name or not api_key_private_key:
            raise ValueError("Missing API key name or private key")

        self.cdp = Cdp.configure(api_key_name, api_key_private_key)

        if os.path.exists(".seed.json") and wallet_id:
            print("Loading existing wallet")
            self.wallet = Wallet.fetch(wallet_id)
            self.wallet.load_seed(".seed.json")
        else:
            print("Creating new wallet")
            self.wallet = Wallet.create(network_id="base-mainnet")
            data = self.wallet.export_data()

            print(data.to_dict())
            self.wallet.save_seed(".seed.json", encrypt=True)

    @property
    def address(self):
        return self.wallet.default_address.address_id

    def balances(self, currency=None):
        return self.wallet.balance(currency) if currency else self.wallet.balances()

    def invoke_contract(
        self,
        contract_address: str,
        abi: List[Dict[str, Any]],
        method: str,
        args: Dict[str, Any],
    ):
        return self.wallet.invoke_contract(contract_address, abi, method, args)


# abi = [
#     {
#         "inputs": [
#             {"internalType": "address", "name": "to", "type": "address"},
#             {"internalType": "uint256", "name": "value", "type": "uint256"}
#         ],
#         "name": "transfer",
#         "outputs": [{"internalType": "uint256", "name": '', "type": "uint256"}],
#         "stateMutability": "nonpayable",
#         "type": "function"
#     }
# ]
#
# invocation = wallet.invoke_contract(
#     contract_address="0xYourContract",
#     abi=abi,
#     method="transfer",
#     args={"to": "0xRecipient", "value": "1000"}
# ).wait()
