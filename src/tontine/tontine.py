import dataclasses
import pathlib
import sys
import tempfile
from typing import Optional, Tuple

import click

import tontine.keys
import tontine.wallet.doge


@dataclasses.dataclass
class AppContext:
    wallet: Optional[tontine.wallet.doge.DogeWallet] = None


@click.group()
@click.pass_context
def main(ctx):
    """
    Create and exercise cryptographically-secured cryptocurrency tontines.

    To set up a new tontine, use the "setup" subcommand. To collect from an existing tontine, use the "exercise"
    subcommand.

    A tontine is an investment vehicle that pays out to the surviving investors. In this case, we encrypt a
    cryptocurrency wallet with investors' public keys, so that it can only be accessed when all investors surrender
    their private keys. In a real tontine, private keys would be entrusted with a third party who could be trusted  to
    distribute them upon the investor's death.
    """
    ctx.ensure_object(AppContext)


@main.group()
def setup():
    """
    Prepare funds and distribute a tontine.

    Select a wallet type to proceed.

    The 'setup' phase of a tontine consists of the following phases:

    \b
    1. Generate a receiving address for a wallet.
    2. Wait until the wallet has received all funds.
    3. Encrypt the wallet using investor public keys.
    """
    pass


@setup.group()
@click.pass_context
@click.option("--testnet/--no-testnet", default=True,
              help="Choose testnet or mainnet.")
@click.option("--doge-cli", type=str, default="dogecoin-cli",
              help="dogecoin-cli location, in case dogecoin-cli is not on $PATH.")
def doge(ctx, **kwargs):
    """
    Use DogeCoin as the cryptocurrency wallet.
    """
    wallet = tontine.wallet.doge.DogeWallet(**kwargs)
    ctx.obj.wallet = wallet


@doge.command()
@click.pass_context
def address(ctx):
    """
    Generate a new address to which investors can send money.
    """
    print(f"Send coins to: {ctx.obj.wallet.receiving_address()}")


@doge.command()
@click.pass_context
@click.option("--require", "-r", type=float,
              help="Return a non-zero exit status if there are not at least this many coins available to spend.")
def check(ctx, require: Optional[float]):
    """
    Check the balance of the wallet.
    """
    balance = ctx.obj.wallet.list_unspent()
    total_spendable = sum([b.amount for b in balance if b.spendable])
    print(f"Total spendable: {total_spendable}")

    print()
    print("Individual balances:")
    for b in balance:
        fields = [
            b.address,
            "(spendable)" if b.spendable else "(not spendable)",
            str(b.amount)
        ]
        print("\t".join(fields))

    if require is not None:
        if total_spendable < require:
            print(f"Total spendable amount {total_spendable} less than required amount {require}.", file=sys.stderr)
            sys.exit(1)


@doge.command()
@click.pass_context
@click.argument("public_keys", type=click.Path(exists=True, dir_okay=False), nargs=-1)
@click.option("--gpg", type=str, default="gpg",
              help="Optional path to gpg executable.")
def encrypt(ctx, public_keys: Tuple[str], gpg: str):
    """
    Encrypt wallet with all public keys, and write the results to standard output.
    """
    if len(public_keys) < 2:
        raise click.ClickException("At least 2 public keys required.")

    with tempfile.NamedTemporaryFile() as wallet_dump, \
            tempfile.TemporaryDirectory() as keyring, \
            tempfile.NamedTemporaryFile("r+") as ciphertext:

        wallet_path = pathlib.Path(wallet_dump.name)
        keyring_path = pathlib.Path(keyring)
        ciphertext_path = pathlib.Path(ciphertext.name)

        keyring = tontine.keys.Keyring(keyring_path, gpg)
        for key in public_keys:
            keyring.import_key(pathlib.Path(key))

        key_fingerprints = [k.fingerprint for k in keyring.list_public_keys()]

        ctx.obj.wallet.dump_wallet(wallet_path)
        keyring.chain_encrypt(wallet_path, key_fingerprints, ciphertext_path)

        ciphertext.seek(0)
        print(ciphertext.read())


if __name__ == "__main__":
    main()
