import pathlib
import textwrap
from typing import List, Tuple

import pytest as pytest

import tontine.keys

ALICE_FINGERPRINT = "C7D3805DEDD0F631EF37B87A8937FB1D402EC5FF"
BOB_FINGERPRINT = "A5E3E2590B7CC156696EA012B587FE5AD4A554F8"

ALL_KEYS = [
    tontine.keys.Key("Alice", ALICE_FINGERPRINT, {"84896B9B40DA3CDD": "2CC900AB6E8F3B27EC2D472C84896B9B40DA3CDD"}),
    tontine.keys.Key("Bob", BOB_FINGERPRINT, {"CAC3078A103042DE": "AF0307A6F087D3B9D7F40418CAC3078A103042DE"}),
]

# Sample cleartext to encrypt
SAMPLE_TEXT = "Hello world!"


def keypair(name: str) -> Tuple[pathlib.Path, pathlib.Path]:
    """
    Returns locations of sample key files packaged with these tests.

    Args:
        name: Base name of the key file ("alice" or "bob").

    Returns: Tuple of paths to the public, private key.
    """
    basedir = pathlib.Path(__file__).parent / "data"
    return basedir / f"{name}.pub", basedir / name


@pytest.fixture
def keyring(tmp_path: pathlib.Path) -> tontine.keys.Keyring:
    return tontine.keys.Keyring(tmp_path / "keyring.keys")


def encrypt(sample_text: str, tmp_path: pathlib.Path, keyring: tontine.keys.Keyring, fingerprints: List[str]) -> pathlib.Path:
    """Chain-encrypt a file and return ciphertext location."""

    cleartext_file = tmp_path / "cleartext.txt"
    ciphertext_file = tmp_path / "ciphertext.txt"

    with cleartext_file.open("w") as cleartext_out:
        cleartext_out.write(sample_text)

    keyring.chain_encrypt(cleartext_file, fingerprints, ciphertext_file)

    return ciphertext_file


@pytest.fixture
def ciphertext_file(tmp_path: pathlib.Path, keyring: tontine.keys.Keyring) -> pathlib.Path:
    """Encrypt `SAMPLE_TEXT` into a file using Alice and Bob's pubtontine.keys."""

    # Import public keys
    keyring.import_key(keypair("alice")[0])
    keyring.import_key(keypair("bob")[0])

    # Encrypt sample text
    return encrypt(SAMPLE_TEXT, tmp_path, keyring, [ALICE_FINGERPRINT, BOB_FINGERPRINT])


def test_parse_list_of_public_keys(keyring: tontine.keys.Keyring):
    """Parse list of Keys from gpg --list-keys stdout."""

    stdout = textwrap.dedent("""\
        tru::1:1644147360:1707217913:3:1:5
        pub:-:3072:1:8937FB1D402EC5FF:1644145816:::-:::scESC::::::23::0:
        fpr:::::::::C7D3805DEDD0F631EF37B87A8937FB1D402EC5FF:
        uid:-::::1644145816::B417ED99B95CE21448B7D789C50009E4F088E3A7::Alice::::::::::0:
        sub:-:3072:1:84896B9B40DA3CDD:1644145816::::::e::::::23:
        fpr:::::::::2CC900AB6E8F3B27EC2D472C84896B9B40DA3CDD:
        pub:u:3072:1:B587FE5AD4A554F8:1644145913:1707217913::-:::scESC::::::23::0:
        fpr:::::::::A5E3E2590B7CC156696EA012B587FE5AD4A554F8:
        uid:u::::1644145913::7312FCD4916197EC38DE4E5C563F1F58C0EE5E59::Bob::::::::::0:
        sub:u:3072:1:CAC3078A103042DE:1644145913::::::e::::::23:
        fpr:::::::::AF0307A6F087D3B9D7F40418CAC3078A103042DE:
    """)

    assert keyring._parse_list_keys_stdout(stdout) == ALL_KEYS


def test_parse_list_of_secret_keys(keyring: tontine.keys.Keyring):
    """Parse list of Keys from gpg --list-secret-keys stdout."""

    stdout = textwrap.dedent("""\
        sec:-:3072:1:8937FB1D402EC5FF:1644145816:::-:::scESC:::+:::23::0:
        fpr:::::::::C7D3805DEDD0F631EF37B87A8937FB1D402EC5FF:
        grp:::::::::58864444AC3F0AD6A4669D45C8B9DF2E3FF318EA:
        uid:-::::1644145816::B417ED99B95CE21448B7D789C50009E4F088E3A7::Alice::::::::::0:
        ssb:-:3072:1:84896B9B40DA3CDD:1644145816::::::e:::+:::23:
        fpr:::::::::2CC900AB6E8F3B27EC2D472C84896B9B40DA3CDD:
        grp:::::::::5E5E8EDE9A03A9E953E0377BD936D599C1F60356:
        sec:u:3072:1:B587FE5AD4A554F8:1644145913:1707217913::-:::scESC:::+:::23::0:
        fpr:::::::::A5E3E2590B7CC156696EA012B587FE5AD4A554F8:
        grp:::::::::8EC058909FBAC64A9313DA0235614A2502663AE7:
        uid:u::::1644145913::7312FCD4916197EC38DE4E5C563F1F58C0EE5E59::Bob::::::::::0:
        ssb:u:3072:1:CAC3078A103042DE:1644145913::::::e:::+:::23:
        fpr:::::::::AF0307A6F087D3B9D7F40418CAC3078A103042DE:
        grp:::::::::9717E493DE2DB664DF176DEBE6B27E23C8FC8064:
    """)

    assert keyring._parse_list_keys_stdout(stdout) == ALL_KEYS


def test_import_and_list(keyring: tontine.keys.Keyring):
    """Test that keys can be imported into a keyring and then listed."""
    keyring.import_key(keypair("alice")[0])
    keyring.import_key(keypair("bob")[0])

    assert keyring.list_public_keys() == ALL_KEYS


def test_round_trip_valid_key(ciphertext_file: pathlib.Path, keyring: tontine.keys.Keyring):
    """File encrypted with both public keys can be decrypted."""

    # Import secret keys
    keyring.import_key(keypair("alice")[1])
    keyring.import_key(keypair("bob")[1])

    # Decrypt sample text
    cleartext = keyring.chain_decrypt(ciphertext_file)

    assert cleartext == SAMPLE_TEXT


def test_cannot_decrypt_without_all_keys(ciphertext_file: pathlib.Path, keyring: tontine.keys.Keyring):
    """File encrypted with both public keys cannot be decrypted with a single key."""

    # Import single secret key
    keyring.import_key(keypair("alice")[1])

    with pytest.raises(Exception):
        keyring.chain_decrypt(ciphertext_file)
