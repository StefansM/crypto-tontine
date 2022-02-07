import dataclasses
import json
import pathlib
import subprocess
from typing import Any, List

from tontine.wallet.base import Balance, Wallet


class DogeWallet(Wallet):
    def __init__(self, testnet: bool = True, doge_cli: str = "dogecoin-cli"):
        self.testnet = testnet
        self._doge_cli = doge_cli

    @property
    def doge_cli(self):
        args = [self._doge_cli]
        if self.testnet:
            args.append("-testnet")

        return args

    def _exec(self, *args) -> Any:
        cmd = self.doge_cli + [str(a) for a in args]
        p = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE)
        return p.stdout

    def list_unspent(self) -> List[Balance]:
        keys = [f.name for f in dataclasses.fields(Balance)]

        result = json.loads(self._exec("listunspent", 0))
        return [
            Balance(**{k: unspent[k] for k in keys})
            for unspent in result
        ]

    def dump_wallet(self, file: pathlib.Path):
        self._exec("dumpwallet", file)

    def load_wallet(self, file: pathlib.Path):
        self._exec("importwallet", file)

    def receiving_address(self) -> str:
        return self._exec("getnewaddress").strip()
