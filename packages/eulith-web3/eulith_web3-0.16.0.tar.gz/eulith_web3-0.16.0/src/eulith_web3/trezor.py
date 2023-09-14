from typing import Optional

from eth_keys.datatypes import Signature
from trezorlib import ethereum
from trezorlib.client import get_default_client
from trezorlib.exceptions import TrezorException
from trezorlib.tools import parse_path
from web3.types import TxParams

from eulith_web3.signer import Signer


def bytes_to_str_in_eip712(data):
    """
    Recursively converts all bytes fields to hex strings in a dictionary.
    """
    if isinstance(data, dict):
        # If the data is a dictionary, iterate over it
        return {k: bytes_to_str_in_eip712(v) for k, v in data.items()}
    elif isinstance(data, bytes):
        # If the data is a bytes object, convert it to a hex string
        return data.hex()
    elif isinstance(data, list):
        # If the data is a list, iterate over it
        return [bytes_to_str_in_eip712(v) for v in data]
    else:
        # If the data is none of the above types, leave it as it is
        return data


class TrezorSigner(Signer):
    """
    Signs EIP712 and transaction data with a Trezor.
    Note this requires a manual interaction with the connected device. This is NOT an automated signer
    """
    def __init__(self, derivation_path: Optional[str] = "44'/60'/0'/0/0"):
        self.client = get_default_client()
        self.derivation_path = parse_path(derivation_path)
        self.cached_address = str(ethereum.get_address(self.client, self.derivation_path, False, None))

    @property
    def address(self) -> str:
        return self.cached_address

    def sign_typed_data(self, eip712_data: dict, message_hash: bytes) -> Signature:
        formatted_d = bytes_to_str_in_eip712(eip712_data)

        signature = ethereum.sign_typed_data(
            self.client,
            self.derivation_path,
            formatted_d)

        signature_bytes = signature.signature.hex()

        returned_v = signature_bytes[-2:]
        formatted_v = '0' + hex(int(returned_v, 16) - 27)[2:]

        formatted_bytes = signature_bytes[:-2] + formatted_v
        return Signature(bytes.fromhex(formatted_bytes))

    def sign_transaction(self, tx: TxParams, message_hash: bytes) -> Signature:
        tx_dict = tx.as_dict()
        value = tx_dict.get('value')
        data = tx_dict.get('data')
        to = tx_dict.get('to')

        if isinstance(value, int):
            parsed_value = value
        else:
            parsed_value = int(value, 16)

        if isinstance(data, bytes):
            parsed_data = data
        else:
            parsed_data = bytes.fromhex(data)

        if isinstance(to, str):
            parsed_to = to
        else:
            parsed_to = to.hex()

        gas_price = tx_dict.get('gasPrice')
        max_per_gas = tx_dict.get('maxFeePerGas')
        max_priority_per_gas = tx_dict.get('maxPriorityFeePerGas')

        if gas_price:
            signature = ethereum.sign_tx(
                self.client,
                self.derivation_path,
                nonce=tx_dict.get('nonce', 0),
                gas_price=tx_dict.get('gasPrice'),
                gas_limit=tx_dict.get('gas'),
                to=parsed_to,
                value=parsed_value,
                data=parsed_data,
                chain_id=tx_dict.get('chainId'))
        elif max_per_gas and max_priority_per_gas:
            signature = ethereum.sign_tx_eip1559(
                self.client,
                self.derivation_path,
                nonce=tx_dict.get('nonce', 0),
                max_gas_fee=max_per_gas,
                max_priority_fee=max_priority_per_gas,
                gas_limit=tx_dict.get('gas'),
                to=parsed_to,
                value=parsed_value,
                data=parsed_data,
                chain_id=tx_dict.get('chainId'))
        else:
            raise TrezorException('you must pass either gasPrice '
                                  'OR maxFeePerGas AND maxPriorityFeePerGas '
                                  'in your txParams to sign the tx with Trezor')

        v, r, s = signature
        if v > 1:
            v -= 27

        return Signature(vrs=(v, int.from_bytes(r, byteorder='big'), int.from_bytes(s, byteorder='big')))
