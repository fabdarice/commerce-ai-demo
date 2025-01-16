import os

from cdp import *

api_key_name = os.getenv('COINBASE_CDP_API_KEY_NAME')
api_key_private_key = os.getenv('COINBASE_CDP_SECRET')


Cdp.configure(api_key_name, api_key_private_key)
mainnet_wallet = Wallet.create(network_id="base-mainnet")
address = wallet.default_address
# new_address = wallet.create_address()
wallet_data = wallet.export_data()
wallet.save_seed("my_seed.json", encrypt=True)
imported_wallet = Wallet.import_data(wallet_data)
fetched_wallet = Wallet.fetch(wallet_id)
fetched_wallet.load_seed("my_seed.json")

historical_balances = address.historical_balances("usdc")
transactions = address.transactions()

abi = [
    {
        "inputs": [
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"internalType": "uint256", "name": '', "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

invocation = wallet.invoke_contract(
    contract_address="0xYourContract",
    abi=abi,
    method="transfer",
    args={"to": "0xRecipient", "value": "1000"}
).wait()
Get all balances for a wallet.

```python
wallet.balances() -> Dict[str, Decimal]
```

Example:
```python
balances = wallet.balances()
```

