import subprocess
import json
import curses
from datetime import datetime, timedelta
from tabulate import tabulate

# Define service flags as constants
NODE_NETWORK = 1 << 0
NODE_WITNESS = 1 << 3
NODE_COMPACT_FILTERS = 1 << 6
NODE_NETWORK_LIMITED = 1 << 10

# Call bitcoincli to get current status of all peer connections
def get_peer_info():
    try:
        result = subprocess.run(
            ["bitcoin-cli", "getpeerinfo"],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error fetching peer info: {e}")
        return []

# Function to decode services
def decode_services(services_hex):
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

# Function to convert "Connected Since" to duration
def connection_duration(connected_since):
    # Convert timestamp to datetime
    connected_time = datetime.fromtimestamp(connected_since)
    # Get current time
    current_time = datetime.now()
    # Calculate duration
    duration = current_time - connected_time
    # Format as hrs:mins:sec
    hours, remainder = divmod(duration.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

# Ban suspicious peer from connecting
def ban_peer(peer_ip_port):
    """
    Bans a peer by IP address. The input is expected to be in the format IP:port.
    Only the IP address is used for banning.
    """
    try:
        # Extract the IP address from the IP:port string
        ip = peer_ip_port.split(":")[0]

        # Use the 'setban' command to add a ban for the given IP
        result = subprocess.run(
            ["bitcoin-cli", "setban", ip, "add"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"Successfully banned peer {ip}")
        else:
            print(f"Failed to ban peer {ip}. Error: {result.stderr.strip()}")
    except Exception as e:
        print(f"An error occurred while trying to ban peer {peer_ip_port}: {e}")

# Analyze peers and take action
def analyze_peers(peers):
    for peer in peers:
        ip = peer['addr']
        banscore = peer.get('banscore', 0)
        services = decode_services(peer.get('services', '0'))

        # Example criteria for banning
        if banscore > 100:
            print(f"Banning peer {ip} with banscore {banscore}")
            ban_peer(ip)
        elif 'N_N' not in services:
            print(f"Warning: peer {ip} is missing NODE_NETWORK service")
#            ban_peer(ip)
        # Add more criteria as needed
#    return services

def format_pingtime(pingtime):
    # Format pingtime to show only the integer portion and three decimal places
    if pingtime == "N/A":
        return pingtime
    try:
        # Try to format the pingtime as a float and display it with 3 decimal places
        return f"{float(pingtime):.3f}"
    except ValueError:
        # If it's not a valid number, return 'N/A'
        return "N/A"

# Prepare data for tabular display
def format_peer_data(peer):
    return [
        peer['id'],
        peer['addr'],
        connection_duration(peer.get('conntime', 0)),  # Get connection duration
        decode_services(peer.get('services', '0')),    # Get services supported
        peer['subver'],
        peer['version'],
        f"{peer['bytessent'] / 1_048_576:.2f} MB",
        f"{peer['bytesrecv'] / 1_048_576:.2f} MB",
        format_pingtime(peer.get('pingtime', 'N/A')),
        'Inbound' if peer['inbound'] else 'Outbound',
        peer['synced_headers'],
        peer['synced_blocks'],
        peer.get('banscore', 'N/A'),
        'Yes' if peer['relaytxes'] else 'No'
        ]

def format_peer_info(peers):
    table_data = [format_peer_data(peer) for peer in peers]
    return table_data

def display_peer_table(peers):
    # Define table headers
    headers = [
        "ID", "Address", "Connected For", "Services", "Version",
        "Protocol", "Bytes Out", "Bytes In", "Ping Time",
        "Direction", "Synced Headers", "Synced Blocks", "Ban Score", "Relays TX"
    ]

    # Define column alignment (right-justify the Pingtime column)
    align = ["center", "left", "center", "left", "center",
             "center", "right", "right", "right",
             "center", "center", "center", "center", "center"]

    # Check if there are peers to display
    if not peers:
        print("No peers connected.")
        return

    # Generate and print the table
    print(tabulate(peers, headers=headers, tablefmt="pretty", colalign=align))

def display_real_time(stdscr):
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(True)  # Make getch() non-blocking
    refresh_rate = 5  # Refresh every N

    # Define table headers
    headers = [
       "ID", "Address", "Connected For", "Services", "Version",
       "Protocol", "Bytes Out", "Bytes In", "Ping Time",
       "Direction", "Synced Headers", "Synced Blocks", "Ban Score", "Relays TX"
    ]

    # Define column alignment (right-justify the Pingtime column)
    align = ["center", "left", "center", "left", "center",
       "center", "right", "right", "right",
       "center", "center", "center", "center", "center"
    ]

    while True:
        # Clear the screen
        stdscr.clear()

        try:
            # Fetch peer info
            peers = get_peer_info()
            table_data = format_peer_info(peers)

            table = tabulate(table_data, headers=headers, tablefmt="pretty", colalign=align)

            # Display the table
            stdscr.addstr(0, 0, "Bitcoin Peer Monitor (Press 'q' to quit)", curses.A_BOLD)
            stdscr.addstr(2, 0, table)

        except Exception as e:
            stdscr.addstr(0, 0, f"Error: {e}", curses.A_BOLD)

        # Refresh the screen
        stdscr.refresh()

        # Wait for the refresh interval or a key press
        for _ in range(refresh_rate * 10):
            key = stdscr.getch()
            if key == ord('q'):
                return  # Exit the program
            curses.napms(100)  # Sleep for 100ms

if __name__ == "__main__":
    # peers = get_peer_info()
    # analyze_peers(peers)
    # table_data = format_peer_info(peers)
    # print("Found {} Peers".format(len(peers)))
    # display_peer_table(table_data)
    curses.wrapper(display_real_time)