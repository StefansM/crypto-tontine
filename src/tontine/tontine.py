import dataclasses
import pathlib
import sys
import tempfile
from typing import Optional, Tuple

import click

import tontine.keys
import tontine.wallet.doge
import tontine.wallet.electrum


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


@click.group()
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


@click.group()
def exercise():
    """
    Exercise (cash out) a tontine.

    Chain decrypt the tontine using the private keys of all investors.
    """
    pass


@main.group()
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


@main.group()
@click.pass_context
@click.option("--testnet/--no-testnet", default=True,
              help="Choose testnet or mainnet.")
@click.option("--electrum-cli", type=str, default="electrum",
              help="electrum executable lcoation, inc case electrum is not on $PATH.")
@click.argument("wallet_path", type=click.Path(path_type=pathlib.Path))
def electrum(ctx, **kwargs):
    """
    Use Electrum as the cryptocurrency wallet.

    \b
    WALLET_PATH: Path to the electrum wallet.
    """
    wallet = tontine.wallet.electrum.ElectrumWallet(**kwargs)
    ctx.obj.wallet = wallet


@setup.command()
@click.pass_context
def address(ctx):
    """
    Generate a new address to which investors can send money.
    """
    print(f"Send coins to: {ctx.obj.wallet.receiving_address()}")


@setup.command()
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


@setup.command()
@click.pass_context
@click.argument("public_keys", type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path), nargs=-1)
@click.option("--gpg", type=str, default="gpg",
              help="Optional path to gpg executable.")
def encrypt(ctx, public_keys: Tuple[pathlib.Path], gpg: str):
    """
    Encrypt wallet and write the results to standard output.
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
            keyring.import_key(key)

        key_fingerprints = [k.fingerprint for k in keyring.list_public_keys()]

        ctx.obj.wallet.dump_wallet(wallet_path)
        keyring.chain_encrypt(wallet_path, key_fingerprints, ciphertext_path)

        ciphertext.seek(0)
        print(ciphertext.read())


@exercise.command()
@click.pass_context
@click.argument("ciphertext", type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path))
@click.argument("private_keys", type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path), nargs=-1)
@click.option("--gpg", type=str, default="gpg",
              help="Optional path to gpg executable.")
def decrypt(ctx, ciphertext: pathlib.Path, private_keys: Tuple[pathlib.Path], gpg: str):
    """
    Chain-decrypt a wallet using the private keys of each investor.

    \b
    CIPHERTEXT: File containing the encrypted wallet.
    PRIVATE_KEYS: Private key files (minimum 2).
    """
    if len(private_keys) < 2:
        raise click.ClickException("At least 2 public keys required.")

    with tempfile.TemporaryDirectory() as keyring, \
            tempfile.NamedTemporaryFile("w") as cleartext_file:
        keyring_path = pathlib.Path(keyring)

        keyring = tontine.keys.Keyring(keyring_path, gpg)
        for key in private_keys:
            keyring.import_key(key)

        cleartext = keyring.chain_decrypt(ciphertext).strip()
        cleartext_file.write(cleartext)
        cleartext_file.flush()

        ctx.obj.wallet.load_wallet(pathlib.Path(cleartext_file.name))


# The commands below the two main phases "setup" and "exercise" have wallet-specific implementations but share a common
# interface. The interface we expose looks like this:
#
# tontine [wallet] [main command] [subcommand]
#
# For example:
#
#    * tontine doge setup address
#    * tontine electrum setup check
#
# This is implemented by defining wallet-specific subcommand ("doge" or "electrum" in the examples above) that handle
# setting up specific wallets. Subcommands are then added to each wallet command that only use the Wallet interface, so
# can be applied to any Wallet.
#
# Because commands can belong to multiple groups in this model, we need to use a verbose Click API and explicitly
# add commands to groups, rather than using the `@x.command` decorator.
wallet_cmds = [doge, electrum]
wallet_subcmds = [setup, exercise]

for wallet_cmd in wallet_cmds:
    for wallet_subcmd in wallet_subcmds:
        wallet_cmd.add_command(wallet_subcmd)


if __name__ == "__main__":
    main()
