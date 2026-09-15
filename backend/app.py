from flask import Flask, jsonify, render_template, request
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
DB_FILE = "aegis.db"


def get_db():
    db = sqlite3.connect(DB_FILE)
    
    db.execute("""CREATE TABLE IF NOT EXISTS logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        habit TEXT NOT NULL,
        value REAL, 
        unit TEXT,
        timestamp TEXT NOT NULL)
        """)
    
    db.execute("""CREATE TABLE IF NOT EXISTS settings(
        habit TEXT PRIMARY KEY,
        default_value REAL,
        unit TEXT)
        """)

    
    db.execute("""
        CREATE TABLE IF NOT EXISTS active_sessions(
        habit TEXT PRIMARY KEY,
        start_time TEXT NOT NULL)
        """)
    
    db.commit()
    return db

def format_hrs_min(decimal_hours):
    total_minutes = int(round(decimal_hours * 60))
    hrs = total_minutes // 60
    mins = total_minutes % 60
    return f"{hrs}h {mins}m"


@app.route("/")
def home():
    return jsonify({"status": "Aegis backend is live"})


@app.route("/log/water", methods=["GET", "POST"])
def log_water():


    db = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.execute("INSERT INTO logs (habit, value, unit, timestamp) VALUES ('water', '245', 'ml', ?)", (now,),)
    db.commit()
    db.close()

    return jsonify({"habit": "water", "value": "245", "unit": "ml", "timestamp": now})



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
    total_water = int(result[0]) if result[0] is not None else 0

    avg_result = db.execute(""" SELECT AVG(daily_sum) FROM (SELECT SUM(value) as daily_sum FROM logs WHERE habit = 'water' GROUP BY strftime('%Y-%m-%d', timestamp)) """).fetchone()
    avg_water = int(avg_result[0]) if avg_result and avg_result[0] is not None else 0



    setting = db.execute("SELECT default_value FROM settings WHERE habit = 'water' ").fetchone()
    default_dose = int(setting[0]) if setting else 245

    db.close()

    goal = 2500
    percentage = min(100.0, round((total_water / goal) * 100, 1))

    return jsonify({
        "today_date" : today,
        "total_ml" : total_water,
        "goal_ml" : goal,
        "percentage" : percentage,
        "average_ml" : avg_water,
        "default_dose" : default_dose
    })  


@app.route("/hydration")
def hydration_screen():
    db = get_db()
    setting = db.execute("SELECT default_value FROM settings WHERE habit = 'water'").fetchone()
    default_dose = int(setting[0]) if setting else 245
    db.close()

    return render_template("hydration.html", default_dose=default_dose)



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
    total_hours = result[0] if result[0] is not None else 0.0

    if total_hours >=7.0:
        quality = "Good"
    elif total_hours > 0:
        quality = 'Fair'
    else:
        quality = "--"

    avg_result = db.execute("""
        SELECT avg(daily_sum) FROM (
            SELECT SUM(value) as daily_sum
            FROM logs
            WHERE habit = 'sleep'
            GROUP BY strftime('%Y-%m-%d', timestamp)
        )
    """).fetchone()
    avg_hours = avg_result[0] if avg_result and avg_result[0] is not None else 0.0

    last_log = db.execute("SELECT timestamp, value FROM logs WHERE habit = 'sleep' ORDER BY id DESC LIMIT 1").fetchone()
    time_range = "--:-- - --:--"
    if last_log:
        end_dt = datetime.strptime(last_log[0], "%Y-%m-%d %H:%M:%S")
        duration = last_log[1]
        start_dt = end_dt - timedelta(hours=duration)
        time_range = f"{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}"                           
    db.close()
                                                                                                                
    return jsonify({
        "is_sleeping": is_sleeping,
        "total_slept": format_hrs_min(total_hours),
        "quality": quality,
        "average": format_hrs_min(avg_hours),
        "time_range": time_range
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


@app.route("/sleep")
def sleep_screen():
    return render_template("sleep.html")  


if __name__ == "__main__":
    get_db()
    app.run(host="0.0.0.0", port=5000, debug=True)


    


