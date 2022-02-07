from unittest.mock import MagicMock

import pytest

import tontine.wallet.base
import tontine.wallet.doge


@pytest.fixture
def noexec_wallet() -> tontine.wallet.doge.DogeWallet:
    wallet = tontine.wallet.doge.DogeWallet(testnet=True)
    wallet._exec = MagicMock()
    return wallet


def test_testnet_arg_is_used():
    wallet = tontine.wallet.doge.DogeWallet(testnet=True)
    assert wallet.doge_cli == ["dogecoin-cli", "-testnet"]


def test_mainnet_used_when_testnet_is_false():
    wallet = tontine.wallet.doge.DogeWallet(testnet=False)
    assert wallet.doge_cli == ["dogecoin-cli"]


def test_listunspent_parsed_correctly(noexec_wallet: tontine.wallet.doge.DogeWallet):
    response = """
    [
        {
            "txid": "3d7612a83a603c3f407735ca8bba8aec9b94766b199bd7e85ff2d263b4db2dd5",
            "vout": 0,
            "address": "niJE2pgf9wb337gYCk4xFnBy9X5kSh8Qdi",
            "account": "Dogecoin test",
            "scriptPubKey": "76a9149ab766f819fb4c11ec010ba7482d9d103a3c8de888ac",
            "amount": 100.00000000,
            "confirmations": 21009,
            "spendable": true,
            "solvable": true
        }
    ]
    """

    noexec_wallet._exec.return_value = response
    expected = [
        tontine.wallet.base.Balance(
            address="niJE2pgf9wb337gYCk4xFnBy9X5kSh8Qdi",
            amount=100.0,
            spendable=True,
            txid="3d7612a83a603c3f407735ca8bba8aec9b94766b199bd7e85ff2d263b4db2dd5",
        )
    ]
    assert noexec_wallet.list_unspent() == expected
