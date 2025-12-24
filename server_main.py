# server_main.py
from cryptography.fernet import Fernet
import json
import threading
from server1 import Server
import sqlite3
import os

KEY_FILE = "fernet.key"

registered_users = {}  # email -> user_data
connected_users = {}   # email -> client_socket
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


def create_database():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT, email TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()


def add_user_to_db(username, email, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    encrypted_password = fernet.encrypt(password.encode('utf-8')).decode('utf-8')
    c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
              (username, email, encrypted_password))
    conn.commit()
    conn.close()


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
        encrypted_password_str = result[0]
        encrypted_password_bytes = encrypted_password_str.encode('utf-8')
        return fernet.decrypt(encrypted_password_bytes).decode('utf-8')

    return None


def handle_client(server: Server, client_socket):
    global registered_users, connected_users
    print("New client connected.")

    while True:
        data = server.receive_data(client_socket)
        if not data:
            print("Client disconnected.")
            break

        try:
            msg = json.loads(data.decode("utf-8"))
        except Exception as e:
            print("Failed to parse JSON:", e)
            break

        action = msg.get("action")
        payload = msg.get("data", {}) or {}
        user_email = payload.get("email")

        if action == "register":
            username = (payload.get("username") or "").strip()
            password = payload.get("password") or ""

            with lock:
                if not user_email:
                    response = {"status": "error", "message": "Email missing."}
                elif user_email in registered_users:
                    response = {"status": "error", "message": "Email already registered."}
                else:
                    try:
                        add_user_to_db(username, user_email, password)  # ✅ בלי f
                        response = {"status": "success", "message": "Registration successful.", "Username": username}
                    except sqlite3.IntegrityError:
                        response = {"status": "error", "message": "Email already registered."}

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
                    password = get_password_from_db(user_email)  # ✅ משתמש ב-fernet הגלובלי
                    if password == payload.get("password"):
                        response = {
                            "status": "success",
                            "message": "Login successful.",
                            "Username": registered_users[user_email].get("username")  # (נשאר כמו אצלך)
                        }
                        connected_users[user_email] = client_socket
                    else:
                        response = {"status": "error", "message": "Incorrect password."}

            client_socket.send(json.dumps(response).encode('utf-8'))

        elif action == "logout":
            print("LOGOUT")

        else:
            response = {"status": "error", "message": "Unknown action."}
            client_socket.send(json.dumps(response).encode('utf-8'))

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
