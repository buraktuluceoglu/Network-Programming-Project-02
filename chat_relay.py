import socket
import threading

# --- CONFIGURATION ---
# The address where the Relay Server will listen
RELAY_HOST = '127.0.0.1'
RELAY_PORT = 6667 

# The address of the MAIN SERVER to forward data to
TARGET_HOST = '127.0.0.1'
TARGET_PORT = 6666

def forward_stream(source, destination):
    """
    Handles one-way data forwarding from a source socket to a destination socket.
    This function creates a transparent bridge for traffic.
    
    Args:
        source (socket): The socket receiving data.
        destination (socket): The socket where data is forwarded.
    """
    while True:
        try:
            data = source.recv(1024)
            if not data:
                break
            destination.send(data)
        except:
            break
    
    # If connection drops, try to close both sides cleanly
    try:
        source.close()
    except:
        pass
    try:
        destination.close()
    except:
        pass

def handle_relay_client(client_socket):
    """
    Handles the connection logic for a single client connecting via the Relay.
    It establishes a bridge to the Main Server and modifies the nickname.
    
    Args:
        client_socket (socket): The socket object for the connected client.
    """
    # 1. Connect to the Main Server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server_socket.connect((TARGET_HOST, TARGET_PORT))
        
        # --- HANDSHAKE AND NICKNAME MODIFICATION ---
        
        # A. Receive 'NICK' request from Main Server and forward to Client
        server_request = server_socket.recv(1024) # Expecting 'NICK'
        client_socket.send(server_request)
        
        # B. Receive the original nickname from the Client
        original_nick = client_socket.recv(1024).decode('utf-8')
        
        # C. Relay prepends '*' to the nickname
        modified_nick = "*" + original_nick
        print(f"Relay Active: Connecting {original_nick.strip()} as {modified_nick.strip()}")
        
        # D. Send the modified nickname to the Main Server
        server_socket.send(modified_nick.encode('utf-8'))
        
        # --- START BIDIRECTIONAL COMMUNICATION (Threading) ---
        # Thread 1: Client -> Server
        t1 = threading.Thread(target=forward_stream, args=(client_socket, server_socket))
        # Thread 2: Server -> Client
        t2 = threading.Thread(target=forward_stream, args=(server_socket, client_socket))
        
        t1.start()
        t2.start()
        
    except Exception as e:
        print(f"Relay Error: {e}")
        client_socket.close()
        server_socket.close()

def start_relay():
    """
    Initializes the Relay Server, binds to the specified port, 
    and listens for incoming client connections.
    """
    relay = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    relay.bind((RELAY_HOST, RELAY_PORT))
    relay.listen()
    
    print(f"Relay Server running on {RELAY_HOST}:{RELAY_PORT}")
    print(f"Forwarding to Main Server at {TARGET_HOST}:{TARGET_PORT}")
    
    while True:
        client, addr = relay.accept()
        print(f"Incoming connection to Relay: {addr}")
        
        thread = threading.Thread(target=handle_relay_client, args=(client,))
        thread.start()

if __name__ == "__main__":
    start_relay()