import os
from electrum.simple_config import SimpleConfig
from electrum import constants
from electrum.wallet import create_new_wallet
from electrum.wallet import Wallet, WalletStorage
from electrum.wallet_db import WalletDB

DEFAULT_WALLET_NAME = "tontine_wallet"
CONFIG = SimpleConfig({"testnet": True})
constants.set_testnet()


def generate_wallet(wallet_name=DEFAULT_WALLET_NAME):
    path = os.path.join(os.getcwd(), wallet_name)
    wallet = create_new_wallet(path=path, config=CONFIG)
    return wallet

def generate_address_for_investor(wallet):
    pass



if __name__ == "__main__":
    os.remove(DEFAULT_WALLET_NAME)
    wallet_data = generate_wallet()
    storage = WalletStorage(DEFAULT_WALLET_NAME)
    db = WalletDB(storage.read(), manual_upgrades=False)
    wallet = Wallet(db=db, storage=storage, config=CONFIG)
    print(len(wallet.get_addresses()))
    wallet.create_new_address(for_change=False)
    print(len(wallet.get_addresses()))