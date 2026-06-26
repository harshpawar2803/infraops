from flask import Flask, render_template, jsonify, request, send_file
import psutil
import socket
import os
import subprocess
import sqlite3
import csv
import platform
import datetime

app = Flask(__name__)


DATA_DIR = os.getenv("DATA_DIR", "/opt/infraops")
os.makedirs(DATA_DIR, exist_ok=True)

DB = os.path.join(DATA_DIR, "monitor.db")

def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reports(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            cpu REAL,
            memory REAL,
            disk REAL,
            loadavg TEXT
        )
    """)
    con.commit()
    con.close()


def run_cmd(cmd):
    try:
        return subprocess.getoutput(cmd)
    except Exception as e:
        return str(e)


def get_status(value):
    if value < 60:
        return "green"
    elif value < 80:
        return "yellow"
    else:
        return "red"


def get_server_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/stats")
def stats():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    loadavg = os.getloadavg()

    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO reports(time,cpu,memory,disk,loadavg) VALUES(?,?,?,?,?)",
        (
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            cpu,
            memory,
            disk,
            str(loadavg),
        ),
    )
    con.commit()
    con.close()

    return jsonify({
    "hostname": socket.gethostname(),

    # System Information
    "os": run_cmd("grep PRETTY_NAME /etc/os-release | cut -d= -f2 | tr -d '\"'"),
    "os_version": run_cmd("cat /etc/redhat-release"),
    "kernel": run_cmd("uname -r"),
    "architecture": platform.machine(),
    "python_version": platform.python_version(),

    # Network
    "ip": get_server_ip(),

    # System Status
    "uptime": run_cmd("uptime -p"),
    "boot_time": datetime.datetime.fromtimestamp(
        psutil.boot_time()
    ).strftime("%Y-%m-%d %H:%M:%S"),

    # CPU
    "cpu": cpu,
    "cpu_count": psutil.cpu_count(logical=True),
    "cpu_frequency": round(psutil.cpu_freq().current, 2) if psutil.cpu_freq() else 0,
    "cpu_color": get_status(cpu),

    # Memory
    "memory": memory,
    "total_memory": round(psutil.virtual_memory().total / (1024**3), 2),
    "available_memory": round(psutil.virtual_memory().available / (1024**3), 2),
    "memory_color": get_status(memory),

    # Disk
    "disk": disk,
    "disk_total": round(psutil.disk_usage("/").total / (1024**3), 2),
    "disk_free": round(psutil.disk_usage("/").free / (1024**3), 2),
    "disk_color": get_status(disk),

    # Load Average
    "loadavg": loadavg,

    # Users
    "users": run_cmd("who"),
    "ssh_users": run_cmd("who | grep -i pts || true"),

    # Services
    "services": {
        "sshd": run_cmd("systemctl is-active sshd 2>/dev/null"),
        "firewalld": run_cmd("systemctl is-active firewalld 2>/dev/null"),
        "crond": run_cmd("systemctl is-active crond 2>/dev/null")
    }
})


@app.route("/api/logs")
def logs():
    keyword = request.args.get("q", "")
    data = run_cmd("journalctl -n 150 --no-pager")

    if keyword:
        data = "\n".join(
            [line for line in data.splitlines() if keyword.lower() in line.lower()]
        )

    return jsonify({"logs": data})


@app.route("/api/auth")
def auth_logs():
    failed = run_cmd(
        "journalctl -u sshd --no-pager | "
        "grep -Ei 'Failed password|authentication failure|Invalid user|Connection closed by authenticating user|PAM.*authentication failure' | "
        "tail -30 || true"
    )

    success = run_cmd(
        "journalctl -u sshd --no-pager | "
        "grep -Ei 'Accepted password|Accepted publickey|session opened for user' | "
        "tail -30 || true"
    )

    telnet = run_cmd(
        "journalctl --no-pager | "
        "grep -Ei 'telnet|xinetd' | "
        "tail -30 || true"
    )

    if not failed.strip():
        failed = "No failed password logs found yet."

    if not success.strip():
        success = "No successful SSH login logs found yet."

    if not telnet.strip():
        telnet = "No telnet logs found."

    return jsonify({
        "failed": failed,
        "success": success,
        "telnet": telnet
    })


@app.route("/export")
def export():
    file = os.path.join(DATA_DIR, "infraops_report.csv")

    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT * FROM reports")
    rows = cur.fetchall()
    con.close()

    with open(file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Time", "CPU", "Memory", "Disk", "Load Average"])
        writer.writerows(rows)

    return send_file(file, as_attachment=True)


if __name__ == "__main__":
    init_db()
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
