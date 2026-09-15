from flask import Flask, jsonify, render_template
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_FILE = "aegis.db"


def get_db():
    db = sqlite3.connect(DB_FILE)
    
    db.execute("""CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        habit TEXT NOT NULL,
        value REAL,
        unit TEXT,
        timestamp TEXT NOT NULL
    )""")
    
    db.execute("""CREATE TABLE IF NOT EXISTS settings (
        habit TEXT PRIMARY KEY,
        default_value REAL,
        unit TEXT
    )""")
    
    db.execute("""
        INSERT OR IGNORE INTO settings(habit, default_value, unit)
        VALUES ('water', 245, 'ml')
    """)
    
    db.execute("""CREATE TABLE IF NOT EXISTS active_sessions (
        habit TEXT PRIMARY KEY,
        start_time TEXT NOT NULL
    )""")
    
    db.commit()
    return db


@app.route("/")
def home():
    return jsonify({"status": "Aegis backend is live"})


@app.route("/log/water")
def log_water():
    db = get_db()
    setting = db.execute("SELECT default_value, unit FROM settings WHERE habit = 'water'").fetchone()
    if setting is None:
        db.close()
        return jsonify({"error": "No water setting found"}), 400
        
    value, unit = setting
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.execute("INSERT INTO logs (habit, value, unit, timestamp) VALUES (?, ?, ?, ?)", ("water", value, unit, now))
    db.commit()
    db.close()
    return jsonify({"habit": "water", "value": value, "unit": unit, "timestamp": now})


@app.route("/logs/water")
def view_water_logs():
    db = get_db()
    rows = db.execute("SELECT value, unit, timestamp FROM logs WHERE habit = 'water' ORDER BY id DESC").fetchall()
    db.close()
    return jsonify([{"value": r[0], "unit": r[1], "timestamp": r[2]} for r in rows])


@app.route("/log/water/undo")
def undo_water():
    db = get_db()
    db.execute("DELETE FROM logs WHERE id = (SELECT id FROM logs WHERE habit = 'water' ORDER BY id DESC LIMIT 1)")
    db.commit()
    db.close()
    return jsonify({"status": "success", "message": "Last water entry is deleted"})


@app.route("/summary/water")
def water_summary():
    db = get_db()
    today = datetime.now().strftime("%Y-%m-%d")

    result = db.execute("SELECT SUM(value) FROM logs WHERE habit = 'water' AND timestamp LIKE ?", (f"{today}%",)).fetchone()
    db.close()

    total_water = result[0] if result[0] is not None else 0
    goal = 2500
    percentage = round((total_water / goal) * 100)
    
    return jsonify({
        'today_date': today,
        "total_ml": total_water,
        "goal_ml": goal,
        "percentage": percentage
    })


@app.route("/hydration")
def hydration_screen():
    return render_template("hydration.html")


@app.route("/log/sleep/toggle")
def toggle_sleep():
    db = get_db()

    session = db.execute("SELECT start_time FROM active_sessions WHERE habit = 'sleep'").fetchone()
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")

    if session is None:
        db.execute("INSERT INTO active_sessions (habit, start_time) VALUES ('sleep', ?)", (now_str,))
        db.commit()
        db.close()
        return jsonify({
            "status": "sleeping",
            "message": "Sleep session is started",
            "start_time": now_str
        })
        
    else:
        start_time = datetime.strptime(session[0], "%Y-%m-%d %H:%M:%S")
        dura_hours = round((now - start_time).total_seconds() / 3600, 2)

        db.execute("INSERT INTO logs (habit, value, unit, timestamp) VALUES ('sleep', ?, 'hours', ?)", (dura_hours, now_str))
        db.execute("DELETE FROM active_sessions WHERE habit = 'sleep'")
        db.commit()
        db.close()

        return jsonify({
            "status": "awake",
            "message": "Sleep session is ended",
            "duration_hours": dura_hours,
            "end_time": now_str
        })


@app.route("/summary/sleep")
def sleep_summary():
    db = get_db()
    today = datetime.now().strftime("%Y-%m-%d")

    session = db.execute("SELECT start_time FROM active_sessions WHERE habit = 'sleep'").fetchone()
    is_sleeping = session is not None

    result = db.execute("SELECT SUM(value) FROM logs WHERE habit = 'sleep' AND timestamp LIKE ?", (f"{today}%",)).fetchone()
    db.close()

    total_hours = result[0] if result[0] is not None else 0
    goal = 8.0
    percentage = round((total_hours / goal) * 100)

    return jsonify({
        "is_sleeping": is_sleeping,
        "today_hours": total_hours,
        "goal_hours": goal,
        "percentage": percentage
    })


@app.route("/logs")
def view_logs():
    db = get_db()
    rows = db.execute("SELECT id, habit, timestamp FROM logs ORDER BY id DESC").fetchall()
    db.close()
    return jsonify([{'id': r[0], "habit": r[1], "timestamp": r[2]} for r in rows])


@app.route("/view")
def view_page():
    banana = get_db()
    rows = banana.execute("SELECT habit, timestamp FROM logs ORDER BY id DESC").fetchall()
    banana.close()
    return render_template("logs.html", logs=rows)


if __name__ == "__main__":
    get_db()
    app.run(host="0.0.0.0", port=5000, debug=True)