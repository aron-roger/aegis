

from flask import Flask, jsonify
import sqlite3 #saves everything in one file (aegis.db)
from datetime import datetime

app = Flask(__name__)
DB_FILE = "aegis.db"

def init_db(): #opens that file ebsures table called logs exists and has three columns id the habit named and timestamp
    banana = sqlite3.connect("aegis.db") 
    banana.execute("""CREATE TABLE IF NOT EXISTS logs (id
    return conn INTEGER PRIMARY KEY AUTOINCREMENT, habit TEXT NOT NULL, timestamp TEXT NOT NULL)""")
    banana.commit()
    banana.close()

def get_db():
    return sqlite3.connect(DB_FILE)


@app.route("/)")
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

    return jsonify()


@app.route("/logs")
def view_logs():
    banana = get_db()
    rows = banana.execute("SELECT habit, timestamp FROM logs ORDER BY id DESC").fetchall()
    banana.close()
    return jsonify([{'habit': r[0], 'timestamp': r[1]} for r in rows])

if __name__ == "__main__":
    app.run(debug=True)


