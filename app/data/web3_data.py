from dataclasses import dataclass
from typing import Dict, Any, Tuple
from datetime import datetime, timezone


@dataclass
class CallData:
    deadline: int
    fee_amount: int
    id: str
    operator: str
    prefix: str
    recipient: str
    recipient_amount: int
    recipient_currency: str
    refund_destination: str
    signature: str


@dataclass
class Metadata:
    chain_id: int
    contract_address: str
    sender: str


@dataclass
class TransferIntent:
    call_data: CallData
    metadata: Metadata

    @staticmethod
    def extract(payload: Dict[str, Any]) -> "TransferIntent":
        transfer_intent_data = payload.get("transfer_intent", {})
        call_data = transfer_intent_data.get("call_data", {})
        metadata = transfer_intent_data.get("metadata", {})
        # Convert deadline to epoch seconds
        deadline_epoch = int(
            datetime.fromisoformat(call_data["deadline"].replace("Z", ""))
            .replace(tzinfo=timezone.utc)
            .timestamp()
        )

        call_data_obj = CallData(
            deadline=deadline_epoch,
            fee_amount=int(call_data["fee_amount"]),
            id=call_data["id"],
            operator=call_data["operator"],
            prefix=call_data["prefix"],
            recipient=call_data["recipient"],
            recipient_amount=int(call_data["recipient_amount"]),
            recipient_currency=call_data["recipient_currency"],
            refund_destination=call_data["refund_destination"],
            signature=call_data["signature"],
        )

        metadata_obj = Metadata(
            chain_id=metadata["chain_id"],
            contract_address=metadata["contract_address"],
            sender=metadata["sender"],
        )

        return TransferIntent(call_data=call_data_obj, metadata=metadata_obj)

    @property
    def to_onchain_params(self) -> dict:
        """
        Converts the TransferIntent into a tuple structure that matches the subsidizedTransferToken ABI.
        """
        return {
            "_intent": [
                str(self.call_data.recipient_amount),
                str(self.call_data.deadline),
                self.call_data.recipient,
                self.call_data.recipient_currency,
                self.call_data.refund_destination,
                str(self.call_data.fee_amount),
                self.call_data.id,  # Convert hex string to bytes
                self.call_data.operator,
                self.call_data.signature,
                self.call_data.prefix,  # Convert string to bytes
            ]
        }
