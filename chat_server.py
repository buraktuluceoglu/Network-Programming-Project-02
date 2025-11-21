import socket
import threading
import random
import datetime
import sys

# --- CONFIGURATION ---
HOST = '127.0.0.1'
PORT = 6666

clients = []
nicknames = []

def write_log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    try:
        with open("chat_log.txt", "a", encoding="utf-8") as f:
            f.write(log_entry)
    except: pass
    print(log_entry.strip())

def broadcast(message):

    if not message.endswith('\n'):
        message += '\n'
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except: pass

def broadcast_user_list():
    users_str = "LIST:" + ",".join(nicknames)
    broadcast(users_str)

def handle_client(client):
    while True:
        try:
            # Receive and clean message
            message = client.recv(1024).decode('utf-8').strip()
            if not message: break
            
            if client in clients:
                index = clients.index(client)
                sender_nick = nicknames[index]
            else: break
            
            current_time = datetime.datetime.now().strftime("%H:%M")

            if message.startswith('/msg'):
                parts = message.split(' ', 2)
                if len(parts) >= 3:
                    target_name = parts[1]
                    content = parts[2]
                    
                    if target_name in nicknames:
                        target_index = nicknames.index(target_name)
                        target_client = clients[target_index]
                        
                        pm_to_target = f"[Private] {sender_nick}: {content}\n"
                        target_client.send(pm_to_target.encode('utf-8'))
                        
                        pm_to_sender = f"[To] {target_name}: {content}\n"
                        client.send(pm_to_sender.encode('utf-8'))
                        
                        write_log(f"PRIVATE: {sender_nick} -> {target_name}: {content}")
                    else:
                        client.send(f"[System]: User '{target_name}' not found.\n".encode('utf-8'))
            else:
                formatted_message = f"[{current_time}] {sender_nick}: {message}"
                broadcast(formatted_message)
                write_log(f"PUBLIC: {sender_nick}: {message}")

        except:
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                nicknames.remove(nickname)
                
                broadcast(f"{nickname} left the chat!")
                broadcast_user_list()
                write_log(f"DISCONNECT: {nickname}")
                break

def shutdown_server(server):
    """Shuts down the server and cleans up all connections."""
    print("\n\n--- SERVER SHUTTING DOWN (Graceful Shutdown) ---")
    
    # 1. Notify clients
    broadcast("[System]: Server is shutting down, connection will be closed.\n")
    
    # 2. Close all client sockets
    for client in clients:
        client.close()
    
    # 3. Close main server socket
    server.close()
    write_log("Server stopped manually via KeyboardInterrupt.")
    print("All connections closed. Port released.")
    sys.exit(0)

def receive():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((HOST, PORT))
        server.listen()
        write_log(f"Server started on {HOST}:{PORT}. Press Ctrl+C to stop.")
    except Exception as e:
        print(f"Error: {e}")
        return

    # --- TRY-EXCEPT BLOCK IN MAIN LOOP ---
    try:
        while True:
            client, address = server.accept()
            
            # Handshake
            client.send('NICK\n'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8').strip()

            if nickname.startswith('*'):
                client.send('REFUSE\n'.encode('utf-8'))
                client.close()
                continue

            original_nick = nickname
            while nickname in nicknames:
                suffix = random.randint(1, 999)
                nickname = f"{original_nick}{suffix}"
            
            nicknames.append(nickname)
            clients.append(client)

            write_log(f"Connected: {nickname}")
            broadcast(f"{nickname} joined the chat!")
            client.send(f"Connected as {nickname}\n".encode('utf-8'))
            
            broadcast_user_list()

            thread = threading.Thread(target=handle_client, args=(client,))
            thread.daemon = True # Thread dies when main program closes
            thread.start()

    except KeyboardInterrupt:
        # Executed when Ctrl+C is pressed
        shutdown_server(server)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        server.close()

if __name__ == "__main__":
    receive()