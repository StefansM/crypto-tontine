from typing import List

import click


@click.group()
def tontine():
    pass


@tontine.command()
@click.argument("public_keys", type=click.Path(exists=True), nargs=-1, required=True)
def setup_tontine(public_keys: List[str]):
    pass


if __name__ == "__main__":
    tontine()
