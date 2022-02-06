import dataclasses
import pathlib
import subprocess
from typing import Dict, List, Optional


@dataclasses.dataclass
class Key:
    name: Optional[str]
    fingerprint: str
    subkeys: Dict[str, str]


class Keyring:
    def __init__(self, location: pathlib.Path, gpg_exe: str = "gpg"):
        """
        Initialise a new keyring object.

        A Keyring object is a limited interface to the `gpg` executable. It provides the methods required to
        sequentially encrypt or decrypt a file.

        This interface always passes `--homedir` to `gpg`, so it won't touch existing keys on a system.

        Args:
            location: Location of the GPG home directory used for storing keypairs.
            gpg_exe: GPG executable location.
        """
        self.location = location
        self._gpg_exe = gpg_exe

        if self.location.exists():
            if not self.location.is_dir():
                raise FileExistsError("location must either not exist or be a directory!")
        else:
            self.location.mkdir(parents=True)
            self.location.chmod(0o700)

    @property
    def gpg(self):
        return [self._gpg_exe, "--homedir", str(self.location)]

    def import_key(self, key_file: pathlib.Path) -> None:
        """
        Import public or private keys into the keyring.

        Args:
            key_file: Location of the key file (public or private) to import.
        """
        subprocess.run(self.gpg + ["--import", str(key_file)], check=True)

    def list_public_keys(self) -> List[Key]:
        """Get list of all public keys in keyring."""
        rval = subprocess.run(
            self.gpg + ["--list-keys", "--with-colons"],
            stdout=subprocess.PIPE, check=True, text=True
        )
        return self._parse_list_keys_stdout(rval.stdout)

    def list_secret_keys(self) -> List[Key]:
        """Get list of all public keys in keyring."""
        rval = subprocess.run(
            self.gpg + ["--list-secret-keys", "--with-colons"],
            stdout=subprocess.PIPE, check=True, text=True
        )
        return self._parse_list_keys_stdout(rval.stdout)

    def chain_decrypt(self, file_to_decrypt: pathlib.Path) -> str:
        """
        Repeatedly decrypt file until a cleartext message is returned.

        Raises a `ValueError` if the file could not be decrypted.

        Args:
            file_to_decrypt: Path of the file to decrypt.

        Returns:
            The cleartext of the decrypted file.
        """
        # This shouldn't be used for large files because it reads the contents of the file into memory after each
        # decryption attempt.

        # If it takes more tries to decrypt the file than we have secret keys, we abort.
        secret_keys = self.list_secret_keys()

        # Decrypt once and save results into memory
        p = subprocess.run(
            self.gpg + ["--decrypt", "--output", "-", str(file_to_decrypt)],
            stdout=subprocess.PIPE,
            text=True,
            check=True,
        )
        decrypted = p.stdout

        message_header = "-----BEGIN PGP MESSAGE----"

        num_attempts = 1
        while num_attempts < len(secret_keys) and message_header in decrypted:
            num_attempts += 1

            p = subprocess.run(
                self.gpg + ["--decrypt", "--output", "-", "-"],
                text=True,
                check=True,
                stdout=subprocess.PIPE,
                input=decrypted,
            )
            decrypted = p.stdout

        if message_header in decrypted:
            raise ValueError(f"Unable to decrypt message after {num_attempts} tries.")

        return decrypted

    def chain_encrypt(self, file_to_encrypt: pathlib.Path, key_fingerprints: List[str], outfile: pathlib.Path):
        """
        Repeatedly encrypt a file using the public keys given by `key_fingerprints`.

        Args:
            file_to_encrypt: Cleartext file to encrypt.
            key_fingerprints: List of public key fingerprints.
            outfile: Ciphertext file location..
        """
        if len(key_fingerprints) <= 1:
            raise ValueError(f"At least two keys must be used for encryption. Received {key_fingerprints}.")

        extra_args = ["--encrypt", "--armor", "--trust-model", "always", "--yes"]
        executables = []
        with file_to_encrypt.open("rb") as enc_in:
            p = subprocess.Popen(
                self.gpg + extra_args + ["--recipient", key_fingerprints[0], "--output", "-", str(file_to_encrypt)],
                stdout=subprocess.PIPE,
                stdin=enc_in
            )
            executables.append(p)

            for recipient in key_fingerprints[1:-1]:
                p = subprocess.Popen(
                    self.gpg + extra_args + ["--recipient", recipient, "--output", "-", "-"],
                    stdout=subprocess.PIPE,
                    stdin=executables[-1].stdout,
                )
                executables.append(p)

            p = subprocess.Popen(
                self.gpg + extra_args + ["--recipient", key_fingerprints[-1], "--output", str(outfile), "-"],
                stdin=executables[-1].stdout,
            )
            executables.append(p)

        for e in executables[:-1]:
            e.stdout.close()

        executables[-1].communicate()
        executables[-1].wait()

    @staticmethod
    def _parse_list_keys_stdout(stdout: str) -> List[Key]:
        """
        Parses colon-delimited gpg output. File format details: https://github.com/CSNW/gnupg/blob/master/doc/DETAILS
        """
        keys = []

        lines = stdout.split("\n")

        # State flag indicating whether we're parsing a main key or a subkey.
        is_subkey = False

        # Map of subkey ID to fingerprint.
        subkeys: Dict[str, str] = {}

        # Temporary variables to hold state while parsing.
        name: Optional[str] = None
        fingerprint: Optional[str] = None
        subkey_id: Optional[str] = None

        for ln in lines:
            cpts = ln.split(":")

            # Start of a new public / secret key
            if cpts[0] == "pub" or cpts[0] == "sec":
                is_subkey = False

                # Parsing of the previous key is complete
                if fingerprint is not None:
                    keys.append(Key(name, fingerprint, subkeys))
                    fingerprint = None
                    name = None
                    subkeys = {}

            # Set state flag so we can parse subkeys.
            elif cpts[0] == "sub" or cpts[0] == "ssb":
                is_subkey = True
                subkey_id = cpts[4]

            # Fingerprint and key name
            elif cpts[0] == "fpr":
                if not is_subkey:
                    fingerprint = cpts[9]
                else:
                    subkeys[subkey_id] = cpts[9]

            elif cpts[0] == "uid":
                name = cpts[9]

        keys.append(Key(name, fingerprint, subkeys))

        return keys
