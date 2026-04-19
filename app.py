from flask import Flask, render_template, request, redirect, session
import sqlite3, random, string, datetime, qrcode, os

app = Flask(__name__)
app.secret_key = "secret123"

ADMIN_USER = "naren"
ADMIN_PASS = "250807"

# Generate WiFi password
def generate_password():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(8))

WIFI_PASSWORD = generate_password()

# Initialize DB
def init_db():
    conn = sqlite3.connect("hotspot.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        mac TEXT,
        status TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mac TEXT,
        time TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# DB helper
def db_query(query, params=(), one=False):
    conn = sqlite3.connect("hotspot.db", check_same_thread=False)
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    data = cur.fetchall()
    conn.close()
    return (data[0] if data else None) if one else data

# Log access
def log_access(mac):
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db_query("INSERT INTO logs(mac, time) VALUES (?, ?)", (mac, time))

# Create static folder
if not os.path.exists("static"):
    os.makedirs("static")

# Generate QR
try:
    qr = qrcode.make("https://macacess-2.onrender.com")
    qr.save("static/qr.png")
except:
    pass

# Routes
@app.route("/", methods=["GET", "POST"])
def index():
    msg = ""
    if request.method == "POST":
        name = request.form["name"]
        mac = request.form["mac"]

        existing = db_query("SELECT * FROM requests WHERE mac=?", (mac,), one=True)
        if not existing:
            db_query("INSERT INTO requests(name, mac, status) VALUES (?, ?, 'pending')", (name, mac))
            msg = "Request Sent ✅"
        else:
            msg = "Already Requested ⚠️"

    return render_template("index.html", message=msg)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        if request.form["username"] == ADMIN_USER and request.form["password"] == ADMIN_PASS:
            session["admin"] = True
            return redirect("/admin")
        else:
            error = "Invalid Username or Password"

    return render_template("login.html", error=error)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("admin"):
        return redirect("/login")

    if request.method == "POST":
        req_id = request.form["id"]
        action = request.form["action"]

        if action == "delete":
            db_query("DELETE FROM requests WHERE id=?", (req_id,))
        else:
            db_query("UPDATE requests SET status=? WHERE id=?", (action, req_id))

    requests = db_query("SELECT * FROM requests")
    logs = db_query("SELECT * FROM logs ORDER BY id DESC")

    return render_template("admin.html", requests=requests, logs=logs, password=WIFI_PASSWORD)

@app.route("/password", methods=["POST"])
def password():
    mac = request.form["mac"]
    user = db_query("SELECT * FROM requests WHERE mac=? AND status='approved'", (mac,), one=True)

    if user:
        log_access(mac)
        return render_template("password.html", password=WIFI_PASSWORD)
    else:
        return "Access Denied ❌"

if __name__ == "__main__":
    app.run(debug=True)