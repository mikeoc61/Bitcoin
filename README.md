# Bitcoin Peer Monitor

A terminal-based tool for monitoring connected peers on a local Bitcoin Core node.  
It queries `bitcoin-cli getpeerinfo` every 15 seconds and displays a formatted table  
with peer data including connection time, services, version, traffic stats, and ping.

## 📋 Features

- Live display of connected Bitcoin node peers
- Highlights peers missing `NODE_NETWORK` capability
- Uses `rich` for colorful terminal tables
- Refreshes automatically every 15 seconds

## 🛠 Requirements

- Python 3.7+
- [`rich`](https://github.com/Textualize/rich) (install via pip)
- `bitcoin-cli` must be in your system's `PATH` and configured to connect to your local Bitcoin Core node

## 📦 Installation

```bash
git clone https://github.com/mikeoc61/bitcoin_peer_monitor.git
cd bitcoin_peer_monitor
pip install rich

## 🚀 Usage

Make sure your Bitcoin Core node is running and `bitcoin-cli` is accessible. Then run:
``` bash
python peers_monitor.py

Use `Ctrl+C` to exit.

## 📄 License

This project is licensed under the MIT License. See `LICENSE` for details.

## 👤 Author

[Michael OConnor] 

Feel free to contribute or open issues!