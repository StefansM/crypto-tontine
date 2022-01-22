import pathlib
import subprocess
import tempfile
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
        return self._parse_list_keys_stdout(rval.stdout)

    def _parse_list_keys_stdout(self, stdout: str) -> List[str]:
        fingerprints = []
        is_subkey = False

        lines = stdout.split("\n")
        for ln in lines:
            if ln.startswith("pub:"):
                is_subkey = False
            elif ln.startswith("sub:"):
                is_subkey = True

            if not ln.startswith("fpr:"):
                continue

            if is_subkey:
                continue

            fields = ln.split(":")
            fingerprints.append(fields[9])

        return fingerprints

    def encrypt_file(self, file_to_encrypt: pathlib.Path, key_fingerprint: str, outfile: pathlib.Path):
        cmd = self.gpg + [
            "--encrypt", "--recipient", key_fingerprint,
            "--armor",
            "--trust-model", "always",
            "--output", str(outfile),
            str(file_to_encrypt),
        ]
        print(" ".join(cmd))

        rval = subprocess.run(
            cmd,
            check=True, stdout=subprocess.PIPE, text=True
        )
        return rval


if __name__ == "__main__":
    kr = Keyring(pathlib.Path("/home/stefans/Dropbox/projects/crypto-tontine/tontine-keys.gpg"))
    kr.import_key(pathlib.Path("keys/stefans.pub"))
    kr.import_key(pathlib.Path("keys/veli.pub"))

    fingerprints = kr.list_keys()
    if len(fingerprints) <= 1:
        raise ValueError(f"Only found one key in keyring: {fingerprints}")

    initial_file = pathlib.Path("README.md")
    output_template = initial_file.name + ".%d.asc"

    for i, fingerprint in enumerate(fingerprints):
        if i == 0:
            infile = initial_file
        else:
            infile = initial_file.parent / (output_template % (i - 1))

        outfile = infile.parent / (output_template % i)
        kr.encrypt_file(infile, fingerprint, outfile)

