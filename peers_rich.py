import subprocess
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from time import sleep
import sys
import termios
import tty
import threading

# Define service flags as constants
NODE_NETWORK = 1 << 0
NODE_WITNESS = 1 << 3
NODE_COMPACT_FILTERS = 1 << 6
NODE_NETWORK_LIMITED = 1 << 10

console = Console()

def get_peer_info():
    """Fetch peer information using bitcoin-cli."""
    result = subprocess.run(
        ["bitcoin-cli", "getpeerinfo"],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def decode_services(services_hex):
    """Decode service flags from hex to human-readable format."""
    services_int = int(services_hex, 16)
    services_list = []
    if services_int & NODE_NETWORK:
        services_list.append("N_N")
    if services_int & NODE_WITNESS:
        services_list.append("N_W")
    if services_int & NODE_COMPACT_FILTERS:
        services_list.append("N_C_F")
    if services_int & NODE_NETWORK_LIMITED:
        services_list.append("N_N_L")
    return ", ".join(services_list)

def connection_duration(connected_since):
    """Convert connection timestamp to duration (hh:mm:ss)."""
    connected_time = datetime.fromtimestamp(connected_since)
    current_time = datetime.now()
    duration = current_time - connected_time
    hours, remainder = divmod(duration.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

def format_pingtime(pingtime):
    """Format ping time to three decimal places."""
    if pingtime == "N/A":
        return pingtime
    try:
        return f"{float(pingtime):.3f}"
    except ValueError:
        return "N/A"

def build_peer_table(peers):
    """Build a table of peer data."""
    table = Table(title="Bitcoin Peer Monitor")

    # Define table headers
    headers = [
        "ID", "Address", "Connected For", "Services", "Version",
        "Protocol", "Bytes Out", "Bytes In", "Ping Time",
        "Direction", "Synced Headers", "Synced Blocks", "Ban Score", "Relays TX"
    ]

    # Control table value alignment based on header
    right_align = ["ID", "Bytes In", "Bytes Out"]

    # Add headers to the table
    for header in headers:
        if header in right_align:
            table.add_column(header, justify="right")
        else:
            table.add_column(header, justify="center")

    # Populate the table with peer data
    for peer in peers:
        services = decode_services(peer.get('services', '0'))
        is_missing_node_network = "N_N" not in services

        row = [
            str(peer['id']),
            peer['addr'],
            connection_duration(peer.get('conntime', 0)),
            services,
            peer['subver'],
            str(peer['version']),
            f"{peer['bytessent'] / 1_048_576:.2f} MB",
            f"{peer['bytesrecv'] / 1_048_576:.2f} MB",
            format_pingtime(peer.get('pingtime', 'N/A')),
            'Inbound' if peer['inbound'] else 'Outbound',
            str(peer['synced_headers']),
            str(peer['synced_blocks']),
            str(peer.get('banscore', 'N/A')),
            'Yes' if peer['relaytxes'] else 'No'
        ]

        # Highlight rows missing NODE_NETWORK service
        if is_missing_node_network:
            table.add_row(*row, style="yellow")
        else:
            table.add_row(*row)

    return table

if __name__ == "__main__":
    with console.screen() as screen:
        try:
            while True:
                peers = get_peer_info()
                table = build_peer_table(peers)
                screen.update(table)
                sleep(5)  # Refresh every 5 seconds
        except KeyboardInterrupt:
            console.print("[bold red]Exiting...[/bold red]")