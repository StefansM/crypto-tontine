# Crypto-Tontine

## Usage

Set up a new tontine:

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

## Generate a keypair

Investors must generate both a public and private key. Use GPG to generate a new keypair. The option `--homedir`
instructs GPG to place keyrings and data files inside the new home directory, leaving the default keyring untouched.
The key must not require a passphrase:

```console
$ gpg --homedir $PWD/test_keys --full-generate-key
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
$ gpg --homedir $PWD/test_keys --locate-key C7D3805DEDD0F631EF37B87A8937FB1D402EC5FF
pub   rsa3072 2022-02-06 [SC]
      C7D3805DEDD0F631EF37B87A8937FB1D402EC5FF
uid           [ultimate] Alice
sub   rsa3072 2022-02-06 [E]
```

### Export public key to file

The tontine uses investor's public keys to sequentially encrypt a cryptocurrency wallet. Export a copy of your public
key from your keyring into `key.pub`:

```console
$ gpg --homedir $PWD/test_keys --export --armor C7D3805DEDD0F631EF37B87A8937FB1D402EC5FF > key.pub
```

### Export secret key to file

All investor's secret keys will be required to decrypt the wallet. Secret keys must be given to a third party that can
be trusted to keep them secret and to distribute them to the remaining investors when the tontine expires. Export a
copy of your secret key into `key`:

```console
$  gpg --homedir $PWD/test_keys --export-secret-keys --armor C7D3805DEDD0F631EF37B87A8937FB1D402EC5FF > key
```

## Design

* Spin up a new wallet.
* Generate a receiving address.
* Receive public keys from investors.
* Receive money from investors.
* Encrypt receiving addresses private key with all public keys.
* Send ciphertext of address private key to all investors.
* Wipe self.

## Setup flow

1. Generate new wallet for receiving BTC from investors.
2. Generate address for each investor.
3. Investors send BTC to address.
4. Receive *public* GPG keys from investors.
   1. Stretch: receive from BTC transaction.
5. Tontine polls receiving addresses until all transactions are confirmed.
6. Sequentially encrypt wallet with public keys.
   1. Generate metadata file containing order of encryption.
7. Distribute ciphertext of wallet to all investors.

Input: Public keys.

Output: Ciphertext of wallet.

## Exercise flow

1. Receive the private keys of investors.
2. Receive the ciphertext of the wallet, includes in cleartext the order of encryption.
3. Sequentially decrypts the wallet.
4. Stretch: distribute funds to surviving investor.

Input: Private keys and wallet ciphertext.

Output: Wallet cleartext.

# Usage


## Return addresses for testnet coins

* Dogecoin: `nbMFaHF9pjNoohS4fD1jefKBgDnETK9uPu`
* BTC: `tb1ql7w62elx9ucw4pj5lgw4l028hmuw80sndtntxt`
