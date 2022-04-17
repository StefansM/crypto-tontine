# Crypto-Tontine

## Usage

Assuming that you have a dogecoin daemon up and running, and `dogecoin-cli` is in your `$PATH`:

```console
$ tontine doge setup address
Send coins to: nkbeuJ1MboTo7RxDFiQrTTyth8BN9HtTWF
```

Monitor the wallet using the `check` subcommand:

```console
$ tontine doge setup --doge-cli ~/Downloads/dogecoin-1.14.5/bin/dogecoin-cli check
Total spendable: 99.99548

Individual balances:
nfQcBPhfqZVdyGduHTNGETVV2MPD4m5bAR	(spendable)	1.0
ndtNjWxVxYSirQ1GXx1M9scdKLH3js4xSi	(spendable)	97.99548
nfQcBPhfqZVdyGduHTNGETVV2MPD4m5bAR	(spendable)	1.0
```

The `--require X` option can be passed to `check` and will cause the command to fail with a non-zero exit status if the
spendable balance is less than `X`. This option can be used to script a complete `setup` workflow.

Encrypt wallet using all investors' public keys:

```console
$ tontine doge setup encrypt *.pub
-----BEGIN PGP MESSAGE-----

hQGMA8rDB4oQMELeAQv/cbJlEichLMU/RGkeryHmQUL15utAyRZwySRSodPvvRQ4
...
```

To cash out (exercise) the tontine, use the `exercise` command, passing the ciphertext of the wallet and the secret keys
of each investor:

```console
$ tontine doge exercise encrypted-wallet.asc key1 key2
```

To use an electrum wallet, replace `doge` with `electrum` in the commands above, noting that `electrum` requires a
wallet file to be passed. Commands become, for example:

```cnosole
$ tontine electrum /path/to/wallet setup encrypt *.pub
```

## Generating a keypair

Investors must generate both a public and private key. Use GPG to generate a new keypair. The key must not require a
passphrase:

```console
$ gpg --full-generate-key
...
public and secret key created and signed.

pub   rsa3072 2022-02-06 [SC]
      C7D3805DEDD0F631EF37B87A8937FB1D402EC5FF
uid                      Alice
sub   rsa3072 2022-02-06 [E]
```

The key fingerprint (`C7D3...`) can be used to unambiguously refer to this keypair. Optionally verify that the key is
present in the keyring:

```console
$ gpg --locate-key C7D3805DEDD0F631EF37B87A8937FB1D402EC5FF
pub   rsa3072 2022-02-06 [SC]
      C7D3805DEDD0F631EF37B87A8937FB1D402EC5FF
uid           [ultimate] Alice
sub   rsa3072 2022-02-06 [E]
```

### Export public key to file

The tontine uses investor's public keys to sequentially encrypt a cryptocurrency wallet. Export a copy of your public
key from your keyring into `key.pub`:

```console
$ gpg --export --armor C7D3805DEDD0F631EF37B87A8937FB1D402EC5FF > key.pub
```

### Export secret key to file

All investor's secret keys will be required to decrypt the wallet. Secret keys must be given to a third party that can
be trusted to keep them secret and to distribute them to the remaining investors when the tontine expires. Export a
copy of your secret key into `key`:

```console
$  gpg --export-secret-keys --armor C7D3805DEDD0F631EF37B87A8937FB1D402EC5FF > key
```

## Building

Build the Python package using the Python [build](https://pypi.org/project/build/) package:

```console
$ python -mbuild
```

To build the docker image, which includes the dogecoin and electrum clients:

```console
$ ./scripts/get-docker-dependencies
$ docker build -t "tontine:$(sed 's/+/-/g' version.txt)" --build-arg "VERSION=$(<version.txt)" .
```

## Running in Docker

The easiest way to get a clean install that we can be reasonable sure won't leak secrets is to use Docker. Assuming
you've built a docker image using the commands in the previous section, start a session like this:

```console
$ docker run -it --rm \
    -v /mnt/storage/dogecoin:/mnt/doge \
    -v /mnt/storage/investor_keys:/mnt/keys \
    tontine:0.1.0 /bin/bash
```

The second `-v` option is used here to mount the investor's public or private keys into the docker container. The first
`-v` option is used to pass the dogecoin `datadir` into the container, which lets us use the script `bootstrap-doge` to
bootstrap the dogecoin blockchain from the host machine.

```console
tontine@27259b953cb3:/$ bootstrap-doge /mnt/doge/
Copying files from source directory.
'/mnt/doge/' -> '/home/tontine/.dogecoin'
...
Removing existing wallet files for a fresh wallet.
removed '/home/tontine/.dogecoin/wallet.dat'
removed '/home/tontine/.dogecoin/testnet3/wallet.dat'
```

Next, start the dogecoin and electrum daemons:

```console
tontine@27259b953cb3:/$ dogecoind -testnet -daemon
Dogecoin server starting
tontine@27259b953cb3:/$ electrum --testnet daemon -d
starting daemon (PID 39)
```

If you're using an electrum wallet, create one and load it into the daemon:

```console
tontine@27259b953cb3:/$ electrum --testnet -w $HOME/electrum_wallet create
{
    "msg": "Please keep your seed in a safe place; if you lose it, you will not be able to restore your wallet.",
    "path": "/home/tontine/electrum_wallet",
    "seed": "my super secret seed"
}
tontine@27259b953cb3:/$ electrum --testnet -w $HOME/electrum_wallet load_wallet
true
```

If you're using dogecoin, verify that the daemon is running and the wallet is empty:

```console
tontine@27259b953cb3:/$ dogecoin-cli -testnet listunspent
[
]
```

Now, you can use the `tontine` command to set up a new tontine:

```console
tontine@27259b953cb3:/$ tontine doge setup address
Send coins to: nrQt5RkkHeyG6Y9pVMPNcSFotuafXYDwmN
tontine@27259b953cb3:/$ tontine doge setup check
Total spendable: 10.0

Individual balances:
nrQt5RkkHeyG6Y9pVMPNcSFotuafXYDwmN	(spendable)	10.0
tontine@ad7bab0566f5:/$ tontine doge setup \
    encrypt /mnt/keys/{alice,bob}.pub \
    > /mnt/keys/encrypted_wallet.asc
```

The encrypted wallet is now available at the host path `/mnt/storage/investor_keys/encrypted_wallet.asc`.

To decrypt, exercise the tontine:

```console
tontine@ad7bab0566f5:/$ tontine doge \
    exercise /mnt/keys/encrypted_wallet.asc \
    /mnt/keys/{alice,bob} \
    > /mnt/keys/decrypted_wallet
```

The decrypted wallet is now available at the host path `/mnt/storage/investor_keys/decrypted_wallet`.

## Return addresses for testnet coins

* Dogecoin: `nbMFaHF9pjNoohS4fD1jefKBgDnETK9uPu`
* BTC: `tb1ql7w62elx9ucw4pj5lgw4l028hmuw80sndtntxt`
