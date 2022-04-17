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

## Return addresses for testnet coins

* Dogecoin: `nbMFaHF9pjNoohS4fD1jefKBgDnETK9uPu`
* BTC: `tb1ql7w62elx9ucw4pj5lgw4l028hmuw80sndtntxt`
