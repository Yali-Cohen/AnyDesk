import socketserver, json, sqlite3, time, hashlib, secrets

DB_PATH = "server.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        created_at INTEGER NOT NULL)""")
    conn.commit()
    conn.close()

def h(password, salt):
    x = hashlib.sha256()
    x.update((salt + password).encode("utf-8"))
    return x.hexdigest()

def register_user(username, email, password):
    if not username or not email or not password:
        return False, "נא למלא את כל השדות."
    if "@" not in email or "." not in email:
        return False, "כתובת אימייל לא תקינה."
    if len(password) < 6:
        return False, "סיסמה קצרה מדי."
    conn = sqlite3.connect(DB_PATH)
    try:
        salt = secrets.token_hex(16)
        pwd = h(password, salt)
        now = int(time.time())
        conn.execute("INSERT INTO users(username,email,password_hash,salt,created_at) VALUES(?,?,?,?,?)",
                     (username.strip(), email.strip().lower(), pwd, salt, now))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return False, "שם משתמש או אימייל כבר קיימים."
    conn.close()
    return True, "הפרטים שלך נשלחו בהצלחה."

def login_user(user_or_email, password):
    if not user_or_email or not password:
        return False, "נא למלא שם משתמש/אימייל וסיסמה."
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    v = user_or_email.strip()
    cur.execute("SELECT password_hash,salt FROM users WHERE username=? OR email=?", (v, v.lower()))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False, "שם משתמש/אימייל לא קיימים."
    return (h(password, row[1]) == row[0], "התחברת בהצלחה." if h(password, row[1]) == row[0] else "סיסמה שגויה.")

class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        f = self.request.makefile("rwb")
        line = f.readline()
        if not line:
            return
        try:
            msg = json.loads(line.decode("utf-8"))
        except:
            f.write(b'{"ok":false,"msg":"Bad JSON"}\n'); f.flush(); return
        cmd = msg.get("cmd"); data = msg.get("data", {})
        if cmd == "REGISTER":
            ok, m = register_user(data.get("username",""), data.get("email",""), data.get("password",""))
        elif cmd == "LOGIN":
            ok, m = login_user(data.get("user_or_email",""), data.get("password",""))
        else:
            ok, m = False, "Unknown command"
        f.write((json.dumps({"ok": ok, "msg": m}, ensure_ascii=False) + "\n").encode("utf-8"))
        f.flush()

class Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

if __name__ == "__main__":
    init_db()
    with Server(("127.0.0.1", 5000), Handler) as s:
        print("listening on 127.0.0.1:5000")
        s.serve_forever()
