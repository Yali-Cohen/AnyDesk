# server_main.py
import random
from cryptography.fernet import Fernet
import json
import threading
from server1 import Server
import sqlite3
import os

KEY_FILE = "fernet.key"

registered_users = {}  # email -> user_data
connected_users = {}   # email -> client_socket
connected_by_address = {}  # address -> client_socket

lock = threading.Lock()
def load_or_create_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key
encryption_key = load_or_create_key()

fernet = Fernet(encryption_key)
def generate_anydesk_address():
    key = random.randint(100000000, 999999999)
    print("Generated AnyDesk Address:", key)
    return str(key)
    
def create_database():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT,
                 email TEXT PRIMARY KEY,
                 password TEXT,
                 address TEXT UNIQUE)
                 ''')
    conn.commit()
    conn.close()
def add_user_to_db(username, email, password:str):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    encrypted_password = fernet.encrypt(password.encode())
    address = generate_anydesk_address()
    c.execute("INSERT INTO users (username, email, password, address) VALUES (?, ?, ?, ?)",
              (username, email, encrypted_password, address))
    conn.commit()
    conn.close()
    return address
def get_username_from_db(email):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE email=?", (email,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None
def get_user_info_from_db(email: str):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT username, address FROM users WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()
    return row 
def is_user_in_db(email):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    user = c.fetchone()
    conn.close()
    return user is not None
def get_password_from_db(email):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE email=?", (email,))
    result = c.fetchone()
    conn.close()

    if result:
        encrypted_password_bytes = result[0] 
        return fernet.decrypt(encrypted_password_bytes)
    return None
def handle_client(server: Server, client_socket):
    global registered_users, connected_users
    print("New client connected.")

    while True:
        data = server.receive_data(client_socket)
        if not data:
            print("Client disconnected.")
            if client_socket in connected_users.values():
                with lock:
                    for email, sock in list(connected_users.items()):
                        if sock == client_socket:
                            info = get_user_info_from_db(email)
                            address = info[1] if info else None
                            connected_users.pop(email, None)
                            if address:
                                connected_by_address.pop(address, None)
                            print(f"User {email} disconnected and removed from connected users.")
                            break
            break

        try:
            msg = json.loads(data.decode("utf-8"))
        except Exception as e:
            print("Failed to parse JSON:", e)
            break

        action = msg.get("action")
        payload = msg.get("data", {})
        user_email = payload.get("email")

        if action == "register":
            username = payload.get("username")
            password = payload.get("password")
            with lock:
                if not user_email:
                    response = {"status": "error", "message": "Email missing."}
                elif is_user_in_db(user_email):
                    response = {"status": "error", "message": "Email already registered."}
                else:
                    address = add_user_to_db(username, user_email, password)  # מחזיר address
                    registered_users[user_email] = payload
                    response = {"status": "success",
                                "message": "Registration successful.",
                                "Username": payload.get("username")
                                , "Address": address
                                }
            client_socket.send(json.dumps(response).encode('utf-8'))

        elif action == "login":
            with lock:
                if not user_email:
                    response = {"status": "error", "message": "Email missing."}
                elif not is_user_in_db(user_email):
                    response = {"status": "error", "message": "Email not registered."}
                elif user_email in connected_users:
                    response = {"status": "error", "message": "User already logged in."}
                else:
                    password_decrypted = get_password_from_db(user_email).decode()
                    password = payload.get("password")
                    if password == password_decrypted:
                        username_db, address = get_user_info_from_db(user_email)

                        response = {
                            "status": "success",
                            "message": "Login successful.",
                            "Username": username_db,
                            "Address": address
                        }
                        connected_users[user_email] = client_socket
                        connected_by_address[address] = client_socket
                    else:
                        response = {"status": "error", "message": "Incorrect password."}

                        
            client_socket.send(json.dumps(response).encode('utf-8'))

        elif action == "logout":
            with lock:
                if not user_email:
                    response = {"status": "error", "message": "Email missing."}
                else:
                    info = get_user_info_from_db(user_email)
                    address = info[1] if info else None
                    connected_users.pop(user_email, None)
                    if address:
                        connected_by_address.pop(address, None)
                        

                    response = {"status": "success", "message": "Logged out."}

            client_socket.send(json.dumps(response).encode('utf-8'))
        elif action == "connect_request":
            target_address = payload.get("target_address")
            with lock:
                target_socket = connected_by_address.get(target_address)
                if target_socket:
                    request_info = {
                        "action": "incoming_connection",
                        "data": {
                            "from_email": user_email,
                            "from_username": get_username_from_db(user_email)
                        }
                    }
                    target_socket.send(json.dumps(request_info).encode('utf-8'))
                    response = {"status": "success", "message": "Connection request sent."}
                else:
                    response = {"status": "error", "message": "Target address not found or user not connected."}
            client_socket.send(json.dumps(response).encode('utf-8'))
            
        elif action == "incoming_response":
            pass
        else:
            response = {"status": "error", "message": "Unknown action."}
            client_socket.send(json.dumps(response).encode('utf-8'))
        
        print(connected_by_address)
        print(f"Handled action: {action} for {user_email} data: {payload}")


def main():
    server = Server()
    print("Server listening on 0.0.0.0:9090...")
    create_database()

    while True:
        client_socket = server.accept_connection()
        t = threading.Thread(target=handle_client, args=(server, client_socket), daemon=True)
        t.start()


if __name__ == "__main__":
    main()
