from eulith_web3.erc20 import TokenSymbol
from eulith_web3.eulith_web3 import EulithWeb3
from eulith_web3.exceptions import EulithUnsafeRequestException
from eulith_web3.gmx import GMXClient
from eulith_web3.signing import LocalSigner, construct_signing_middleware
from common_config import *


def test_unsafe_tx_error_increase_order():
    acct = LocalSigner("0x4d5db4107d237df6a3d58ee5f70ae63d73d7658d4026f2eefd2f204c81682cb7")
    ew3 = EulithWeb3(eulith_url=EULITH_URL,
                     eulith_token=EULITH_TOKEN,
                     signing_middle_ware=construct_signing_middleware(acct))

    gc = GMXClient(ew3)

    weth = ew3.v0.get_erc_token(TokenSymbol.WETH)

    ew3.v0.start_atomic_transaction(acct.address)
    try:
        gc.create_increase_order(weth, weth, True, 10.0, 10.0, 1000)
        assert False
    except EulithUnsafeRequestException as e:
        assert True
    except:
        assert False

    try:
        gc.create_decrease_order(weth, weth, 10.0, 10.0, True, 1000)
        assert False
    except EulithUnsafeRequestException as e:
        assert True
    except:
        assert False
