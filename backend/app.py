

from flask import Flask, jsonify
import sqlite3 #saves everything in one file (aegis.db)
from datetime import datetime

app = Flask(__name__)
DB_FILE = "aegis.db"

def init_db(): #opens that file ebsures table called logs exists and has three columns id the habit named and timestamp
    banana = sqlite3.connect("aegis.db") 
    banana.execute("""CREATE TABLE IF NOT EXISTS logs (id
    INTEGER PRIMARY KEY AUTOINCREMENT, habit TEXT NOT NULL, timestamp TEXT NOT NULL)""")
    banana.commit()
    banana.close()

def get_db():
    return sqlite3.connect(DB_FILE)


@app.route("/")
def home():
    return jsonify({"status": "Aegis backend is live"})

@app.route("/log/<habit>")
def log_habit(habit):
    db = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor = db.cursor()
    cursor.execute("INSERT INTO logs (habit, timestamp) VALUES (?, ?)", (habit, now))
    db.commit()
    log_id = cursor.lastrowid
    db.close()

    return jsonify({
        "success": True,
        "logged": habit,
        "id": log_id,
        "timestamp": now
    })


@app.route("/logs")
def view_logs():
    db = get_db()
    rows = db.execute("SELECT id, habit, timestamp FROM logs ORDER BY id DESC").fetchall()
    db.close()
    return jsonify([{'id': r[0], "habit": r[1], "timestamp": r[2]} for r in rows])

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)


