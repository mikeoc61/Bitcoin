import json
from datetime import datetime
import subprocess

# Define the services as constants
SERVICES = {
    0x01: "NODE_NETWORK",       # Basic block and transaction relay
    0x02: "NODE_GETUTXOS",      # Supports getutxos RPC
    0x04: "NODE_BLOOM",         # Supports bloom filters (lightweight clients)
    0x08: "NODE_WITNESS",       # Supports SegWit
    0x10: "NODE_XTHIN",         # Supports XThin protocol
    0x40000000: "NODE_NETWORK_LIMITED"  # Limited node (only headers, no full blocks)
}

# Function to translate the services bitmask into a human-readable list
def translate_services(services_bitmask):
    supported_services = []
    for bit, service_name in SERVICES.items():
        if services_bitmask & bit:  # Check if the bit is set
            supported_services.append(service_name)
    return supported_services

# Function to execute bitcoin-cli and get peer information
def get_peer_info():
    # Execute the bitcoin-cli command to get peer information
    result = subprocess.run(['bitcoin-cli', 'getpeerinfo'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error executing bitcoin-cli: {result.stderr.decode()}")
        return []
    return json.loads(result.stdout.decode())

# Function to format peer information for display
def format_peer_info(peers):
    # Prepare data for tabular display
    table_data = []
    for peer in peers:
        # Translate the services bitmask to human-readable services
        services = translate_services(peer['services'])

        # Append the peer data to the table
        table_data.append([
            peer['id'],
            peer['addr'],
            datetime.utcfromtimestamp(peer['conntime']).strftime('%Y-%m-%d %H:%M:%S'),
            ', '.join(services),  # Join the list of services into a comma-separated string
            peer['subver'],
            peer['version'],
            f"{peer['bytessent'] / 1_048_576:.2f} MB",
            f"{peer['bytesrecv'] / 1_048_576:.2f} MB",
            peer.get('pingtime', 'N/A'),
            'Inbound' if peer['inbound'] else 'Outbound',
            peer['synced_headers'],
            peer['synced_blocks'],
            peer.get('banscore', 'N/A'),
            'Yes' if peer['relaytxes'] else 'No'
        ])
    return table_data

# Function to print the table in a human-readable format
def print_table(table_data):
    # Print header
    headers = ["ID", "Address", "Connection Time", "Services", "Subver", "Version", "Bytes Sent", "Bytes Recvd", "Ping", "Type", "Synced Headers", "Synced Blocks", "Ban Score", "Relay TXes"]
    print(f"{' | '.join(headers)}")
    print("-" * 150)  # Line to separate header from data

    # Print each row of data
    for row in table_data:
        print(f"{' | '.join(map(str, row))}")

# Main function to fetch, format, and display peer info
def main():
    peers = get_peer_info()
    if peers:
        table_data = format_peer_info(peers)
        print_table(table_data)

# Run the main function
if __name__ == "__main__":
    main()
