# Jarar Coin (JARAR)

Jarar Coin is an experimental cryptocurrency based on Bitcoin Core.

- Proof of work: SHA-256 (same as Bitcoin)
- Block time: 10 minutes, difficulty adjusts every 144 blocks
- Block reward: 50 JARAR, halving every 400,000 blocks
- Maximum supply: 40,000,000 JARAR
- Addresses: `jr1...` (bech32) and `J...` (legacy)
- Default P2P port: 24333
- Programs: `jarard`, `jarar-cli`, `jarar-tx`, `jarar-util`, `jarar-wallet`
- Data directory `~/.jarar`, config file `jarar.conf`

This software is under development and has not been audited. It is not
ready for real funds.

Jarar Coin is a fork of Bitcoin Core and is released under the MIT license
(see the COPYING file).

## Build

See INSTALL.md and doc/build-unix.md. On Linux:

    cmake -B build -DENABLE_IPC=OFF
    cmake --build build -j2
