import abc
import dataclasses
import pathlib
from typing import List


@dataclasses.dataclass
class Balance:
    address: str
    amount: float
    spendable: bool
    txid: str


class Wallet(abc.ABC):
    @abc.abstractmethod
    def list_unspent(self) -> List[Balance]:
        pass

    @abc.abstractmethod
    def dump_wallet(self, file: pathlib.Path):
        pass

    @abc.abstractmethod
    def load_wallet(self, file: pathlib.Path):
        pass

    @abc.abstractmethod
    def receiving_address(self) -> str:
        pass
