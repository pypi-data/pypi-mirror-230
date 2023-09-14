from dataclasses import dataclass
from typing import TypedDict

from eth_account.messages import encode_structured_data
from eth_utils import keccak


@dataclass
class AceImmediateTx:
    chain_id: int
    nonce: int
    max_priority_fee_per_gas: int
    max_fee_per_gas: int
    gas_limit: int
    data: bytes

    @classmethod
    def from_json(cls, data: dict) -> "AceImmediateTx":
        return cls(
            chain_id=data["chain_id"],
            nonce=int(data["nonce"], base=16),
            max_priority_fee_per_gas=int(data["max_priority_fee_per_gas"], base=16),
            max_fee_per_gas=int(data["max_fee_per_gas"], base=16),
            gas_limit=int(data["gas_limit"], base=16),
            data=bytes.fromhex(data["data"][2:]),
        )

    def to_json(self) -> dict:
        return dict(
            chain_id=self.chain_id,
            nonce=hex(self.nonce),
            max_priority_fee_per_gas=hex(self.max_priority_fee_per_gas),
            max_fee_per_gas=hex(self.max_fee_per_gas),
            gas_limit=hex(self.gas_limit),
            data="0x" + self.data.hex()
        )


class AcePingResponse(TypedDict):
    ping_time_millis: int
    auth_address: str
    ui_address: str


def get_ace_immediate_tx_typed_data(message: AceImmediateTx) -> dict:
    # Should match the EIP-712 definition in src/ace/immediate_tx.rs
    types = {
        "EIP712Domain": [
            {"name": "name", "type": "string"},
            {"name": "version", "type": "string"},
        ],
        "AceImmediateTx": [
            {"name": "chainId", "type": "int64"},
            {"name": "nonce", "type": "uint256"},
            {"name": "maxPriorityFeePerGas", "type": "uint256"},
            {"name": "maxFeePerGas", "type": "uint256"},
            {"name": "gasLimit", "type": "uint256"},
            {"name": "data", "type": "bytes"},
        ],
    }

    payload = {
        "types": types,
        "primaryType": "AceImmediateTx",
        "domain": {"name": "EulithAceImmediateTx", "version": "1"},
        "message": {
            "chainId": message.chain_id,
            "nonce": message.nonce,
            "maxPriorityFeePerGas": message.max_priority_fee_per_gas,
            "maxFeePerGas": message.max_fee_per_gas,
            "gasLimit": message.gas_limit,
            "data": message.data,
        },
    }

    return payload


def get_ace_immediate_tx_hash(ace_immediate_tx: AceImmediateTx) -> bytes:
    signable_message = encode_structured_data(get_ace_immediate_tx_typed_data(ace_immediate_tx))
    return keccak(b"\x19\x01" + signable_message.header + signable_message.body)
