import pathlib
import subprocess
from typing import List

import gnupg


class Keyring:
    def __init__(self, location: pathlib.Path):
        self.location = location

    @property
    def gpg(self):
        return ["gpg", "--no-default-keyring", "--keyring", str(self.location)]

    def import_key(self, pubkey_file: pathlib.Path):
        subprocess.run(self.gpg + ["--import", str(pubkey_file)], check=True)

    def list_keys(self):
        rval = subprocess.run(
            self.gpg + ["--list-keys", "--with-colons"],
            stdout=subprocess.PIPE, check=True, text=True
        )
        return rval.stdout

    def encrypt_file(self, file_to_encrypt: pathlib.Path, key_fingerprints: List[str]):
        pass


if __name__ == "__main__":
    kr = Keyring(pathlib.Path("/home/stefans/Dropbox/projects/crypto-tontine/tontine-keys.gpg"))
    kr.import_key(pathlib.Path("keys/stefans.pub"))
    kr.import_key(pathlib.Path("keys/veli.pub"))

    print(kr.list_keys())

