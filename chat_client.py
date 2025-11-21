import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox, Listbox

class ChatClient:
    """
    A GUI-based Chat Client using Tkinter and Sockets.
    Handles connections, public/private messaging, and user listing.
    """
    def __init__(self):
        """
        Initialize the Chat Client, prompt for nickname, and start the main loop.
        """
        self.HOST = '127.0.0.1'
        self.PORT = 6666
        self.client_socket = None
        self.running = True
        self.private_windows = {} 

        self.root = tk.Tk()
        self.root.withdraw()

        self.nickname = simpledialog.askstring("Nickname", "Choose a nickname:", parent=self.root)
        if not self.nickname:
            self.root.destroy()
            return

        self.root.deiconify()
        self.root.title(f"Chat Client - {self.nickname}")
        self.root.geometry("700x500")

        self.setup_gui()

        if not self.connect_to_server():
            return 

        self.root.protocol("WM_DELETE_WINDOW", self.stop)
        self.root.mainloop()

    def setup_gui(self):
        """
        Sets up the main GUI components: Chat area, Input field, and User list.
        """
        left_frame = tk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.chat_area = scrolledtext.ScrolledText(left_frame, state='disabled')
        self.chat_area.pack(fill=tk.BOTH, expand=True)

        self.msg_entry = tk.Entry(left_frame, font=("Arial", 12))
        self.msg_entry.pack(fill=tk.X, pady=5)
        self.msg_entry.bind("<Return>", self.send_public_message)

        tk.Button(left_frame, text="Send Public", command=self.send_public_message).pack(fill=tk.X)

        right_frame = tk.Frame(self.root, width=200)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        tk.Label(right_frame, text="Online Users").pack()
        self.user_listbox = Listbox(right_frame)
        self.user_listbox.pack(fill=tk.BOTH, expand=True)
        self.user_listbox.bind('<Double-1>', self.on_double_click_user)

    def connect_to_server(self):
        """
        Establishes the TCP connection to the server and starts the receiver thread.
        
        Returns:
            bool: True if connection successful, False otherwise.
        """
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.HOST, self.PORT))
            
            thread = threading.Thread(target=self.receive_messages)
            thread.daemon = True
            thread.start()
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {e}")
            self.root.destroy()
            return False

    def receive_messages(self):
        """
        Background thread loop to receive data from the server.
        Handles TCP stream buffering and line splitting.
        """
        buffer = ""
        while self.running:
            try:
                # Receive data
                data = self.client_socket.recv(1024).decode('utf-8')
                if not data: break
                
                # Add to buffer and split line by line
                buffer += data
                messages = buffer.split('\n')
                
                # The last part might be incomplete, keep it in buffer
                buffer = messages[-1] 
                
                # Process completed messages
                for message in messages[:-1]:
                    self.process_message(message)
            except:
                break

    def process_message(self, message):
        """
        Helper function to process a single protocol message.
        
        Args:
            message (str): The received message string.
        """
        if message == 'NICK':
            self.client_socket.send(self.nickname.encode('utf-8'))
        
        elif message.startswith('LIST:'):
            users_str = message[5:]
            users = users_str.split(',')
            self.update_user_list(users)

        elif message.startswith('[Private]'):
            parts = message.split(' ', 2)
            sender = parts[1].replace(':', '')
            content = parts[2]
            self.handle_private_message(sender, content, is_incoming=True)

        elif message.startswith('[To]'):
            parts = message.split(' ', 2)
            target = parts[1].replace(':', '')
            content = parts[2]
            self.handle_private_message(target, content, is_incoming=False)
        
        elif message == 'REFUSE':
            messagebox.showerror("Error", "Nickname cannot start with '*'.")
            self.stop()

        else:
            self.display_public_message(message)

    def update_user_list(self, users):
        """
        Updates the listbox with the current online users.
        
        Args:
            users (list): List of usernames.
        """
        self.user_listbox.delete(0, tk.END)
        for user in users:
            if user and user != self.nickname:
                self.user_listbox.insert(tk.END, user)

    def on_double_click_user(self, event):
        """
        Event handler for double-clicking a user in the list to open a private chat.
        """
        selection = self.user_listbox.curselection()
        if selection:
            target_user = self.user_listbox.get(selection[0])
            self.open_private_window(target_user)

    def open_private_window(self, target_user):
        """
        Creates a new Toplevel window for private messaging with a specific user.
        
        Args:
            target_user (str): The nickname of the target user.
        """
        if target_user in self.private_windows:
            self.private_windows[target_user].lift()
            return

        window = tk.Toplevel(self.root)
        window.title(f"Private: {target_user}")
        window.geometry("400x300")

        chat_area = scrolledtext.ScrolledText(window, state='disabled', height=10)
        chat_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        entry_field = tk.Entry(window)
        entry_field.pack(fill=tk.X, padx=5, pady=5)

        def send_pm(event=None):
            msg = entry_field.get()
            if msg:
                protocol_msg = f"/msg {target_user} {msg}"
                try:
                    self.client_socket.send(protocol_msg.encode('utf-8'))
                    entry_field.delete(0, tk.END)
                except: pass
        
        entry_field.bind("<Return>", send_pm)
        tk.Button(window, text="Send", command=send_pm).pack(pady=5)

        window.chat_area = chat_area 
        self.private_windows[target_user] = window

        def on_close():
            del self.private_windows[target_user]
            window.destroy()
        
        window.protocol("WM_DELETE_WINDOW", on_close)

    def handle_private_message(self, user, content, is_incoming):
        """
        Routes a private message to the correct dedicated window.
        
        Args:
            user (str): The other user involved in the chat.
            content (str): The message text.
            is_incoming (bool): True if receiving, False if sending confirmation.
        """
        if user not in self.private_windows:
            self.open_private_window(user)
        
        window = self.private_windows[user]
        area = window.chat_area
        
        timestamp = "Now"
        prefix = f"{user}" if is_incoming else "Me"
        area.config(state='normal')
        area.insert(tk.END, f"[{timestamp}] {prefix}: {content}\n")
        area.config(state='disabled')
        area.yview(tk.END)

    def send_public_message(self, event=None):
        """
        Sends the message from the main entry field to the public chat.
        """
        msg = self.msg_entry.get()
        if msg:
            try:
                self.client_socket.send(msg.encode('utf-8'))
                self.msg_entry.delete(0, tk.END)
            except:
                self.stop()

    def display_public_message(self, message):
        """
        Appends a message to the main public chat area.
        """
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + '\n')
        self.chat_area.yview(tk.END)
        self.chat_area.config(state='disabled')

    def stop(self):
        """
        Closes the socket and destroys the GUI window.
        """
        self.running = False
        try:
            self.client_socket.close()
        except: pass
        self.root.destroy()

if __name__ == "__main__":
    ChatClient()