# Multi-User Chat Application

A comprehensive, multi-threaded chat application developed as a **Network Programming Course Project**. It features a robust TCP server, a graphical client interface (GUI), private messaging with dedicated windows, and an optional relay server.

---

##  Project Overview
The goal of this project is to demonstrate socket programming concepts including **threading**, **synchronization**, and **GUI integration**. The system consists of three main components:

1.  **Chat Server:** Manages multiple client connections, handles message broadcasting, enforces nickname rules, and logs activity.
2.  **Chat Client:** A Tkinter-based GUI that allows users to join the chat, see online users, and send public/private messages.
3.  **Chat Relay:** An intermediary proxy server that modifies nicknames by appending a `*` prefix.

---

##  Key Features

###  Server Capabilities
* **Unique Nicknames:** Automatically appends random numbers to duplicate nicknames (e.g., `User` → `User452`).
* **Nickname Validation:** Blocks nicknames starting with `*` (reserved for relay users).
* **Activity Logging:** Records all public/private messages and connections to `chat_log.txt` with timestamps.
* **Graceful Shutdown:** Handles `Ctrl+C` (KeyboardInterrupt) to close all sockets and release the port safely.

###  Client Interface (GUI)
* **Real-time User List:** Displays currently connected users on the side panel.
* **Private Messaging:** * Double-click a user in the list to open a **separate, dedicated chat window**.
    * Incoming private messages automatically trigger a pop-up window.
* **Protocol Handling:** Implements a line-based protocol (`\n`) to prevent message concatenation (TCP stream stickiness).

###  Relay Server
* **Transparent Proxy:** Forwards data between client and server without modification to the payload.
* **Nickname Rewriting:** Intercepts the handshake and adds `*` to the nickname.

---

## Project Structure

```text
python-chat-system/
│
├── chat_server.py      # Main Server (Port 6666)
├── chat_client.py      # Client GUI Application
├── chat_relay.py       # Relay/Proxy Server (Port 6667)
├── chat_log.txt        # Auto-generated Log File
├── README.md           # Project Documentation
└── screenshots/        # Project Images
    ├── server_run.png
    ├── public_chat.png
    └── private_chat.png
```
## Requirements
No external pip packages are required. The project uses Python's standard library:

* Python 3.x
- socket, threading, sys (Networking & Concurrency)

- tkinter (GUI) 

- datetime, random (Utilities)

## Usage Guide
1. #### Standard Mode (Direct Connection)

Use this mode for normal chat functionality.

Start the Server:

- python3 chat_server.py
    
        Output: Server started on 127.0.0.1:6666

Start the Client(s): Open a new terminal for each user.

- python3 chat_client.py
    
        Enter a nickname when prompted.

Public Chat: Type in the main window.

Private Chat: Double-click a name in the "Online Users" list.

2. #### Relay Mode 

Use this to test the nickname rewriting feature.

Note: To test this, ensure the Server allows * nicknames by commenting out the blockage code in chat_server.py.

- Start Server: python3 chat_server.py

- Start Relay: python3 chat_relay.py (Listens on 6667).

Configure Client: Open chat_client.py and change self.PORT to 6667.

Run Client: python3 chat_client.py.

Result: Your nickname will appear as *Nickname in the chat.

## Screenshots

- Public Chat Interface
  
  <img width="795" height="524" alt="Ekran Resmi 2025-11-21 13 58 25" src="https://github.com/user-attachments/assets/d12f25da-88f8-4bf7-b02d-029c564e3780" />

Main window with chat history and user list.

- Private Messaging (Popup)
  
  <img width="796" height="525" alt="Ekran Resmi 2025-11-21 13 59 13" src="https://github.com/user-attachments/assets/dfd72420-8772-4050-b134-dadb859211f1" />

Dedicated window opened via double-click.

## Technical Details
- Protocol: The system uses a custom text-based protocol. Messages are delimited by newline characters (\n) to ensure distinct message parsing over the TCP stream.

- Concurrency: * Server: Spawns a new thread for every accepted client (handle_client).

- Client: Uses a daemon thread (receive_messages) to listen for incoming data without freezing the Tkinter GUI.

### Port Configuration:

- Server: 6666

- Relay: 6667
