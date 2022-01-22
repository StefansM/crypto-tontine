import subprocess as sp
import os

DEFAULT_WALLET_NAME = "tontine_wallet"


def generate_wallet(wallet_name=DEFAULT_WALLET_NAME):
    """Generates and returns an Electrum bitcoin wallet."""
    return sp.check_output(["electrum", "--testnet", "create", "-w", os.path.join(os.getcwd(), DEFAULT_WALLET_NAME)])
