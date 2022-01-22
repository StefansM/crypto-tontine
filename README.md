# Crypto-Tontine

*Status*: Just a design document for now.

## Overview

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

## Return addresses for testnet coins

* Dogecoin: `nbMFaHF9pjNoohS4fD1jefKBgDnETK9uPu`
* BTC: `tb1ql7w62elx9ucw4pj5lgw4l028hmuw80sndtntxt`
