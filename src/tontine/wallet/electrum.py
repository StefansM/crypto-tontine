import dataclasses
import json
import pathlib
import subprocess
from typing import Any, List

from tontine.wallet.base import Balance, Wallet


class ElectrumWallet(Wallet):
    def __init__(self, wallet_path: pathlib.Path, testnet: bool = True, electrum_cli: str = "electrum"):
        self.wallet_path = wallet_path
        self.testnet = testnet
        self._electrum_cli = electrum_cli

    @property
    def _cli(self):
        args = [self._electrum_cli, "-w", str(self.wallet_path)]
        if self.testnet:
            args.append("--testnet")

        return args

    def _exec(self, *args) -> Any:
        cmd = self._cli + [str(a) for a in args]
        p = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE)
        return p.stdout

    def list_unspent(self) -> List[Balance]:
        result = json.loads(self._exec("listunspent"))
        return [
            Balance(
                address=unspent["address"],
                amount=float(unspent["value"]),
                # TODO: Is this true?
                spendable=True,
            )
            for unspent in result
        ]

    def dump_wallet(self, file: pathlib.Path):
        seed = self._exec("getseed")
        with file.open("w") as seed_out:
            seed_out.write(seed)

    def load_wallet(self, file: pathlib.Path):
        with file.open("r") as seed_in:
            seed = seed_in.read()
        self._exec("restore", seed)

    def receiving_address(self) -> str:
        address = self._exec("getunusedaddress").strip()
        if address == "None":
            address = self._exec("createnewaddress").strip()

        return address
