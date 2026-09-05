import sqlite3
import datetime as dt
from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

DB_NAME = "habits.db"
GRID_DAYS = 14
MAX_HABITS = 5


def get_connection():
    """Open a connection to the database and return it with a cursor."""
    conn = sqlite3.connect(DB_NAME)
    return conn, conn.cursor()


def get_water_info(cursor):
    """Return water's habit ID and daily goal."""
    cursor.execute('SELECT ID, Goal FROM habits WHERE Name = "Water"')
    row = cursor.fetchone()
    return row[0], int(row[1])


def is_done(cursor, habit_id, day):
    """True if a log row exists for this habit on this date."""
    cursor.execute(
        'SELECT 1 FROM logs WHERE Habit_ID = ? AND Date = ?',
        (habit_id, day)
    )
    return cursor.fetchone() is not None


def water_total_for(cursor, water_id, day):
    """Total cups logged for a given date (0 if none)."""
    cursor.execute(
        'SELECT SUM(value) FROM logs WHERE Habit_ID = ? AND Date = ?',
        (water_id, day)
    )
    total = cursor.fetchone()[0]
    return int(total) if total is not None else 0


@app.route("/")
def home():
    conn, cursor = get_connection()
    today = dt.date.today()

    water_id, water_goal = get_water_info(cursor)
    water_total = water_total_for(cursor, water_id, today)

    # All checkbox-type habits, with today's completion status.
    cursor.execute('SELECT ID, Name FROM habits WHERE Type = "Checkbox"')
    checkbox_habits = cursor.fetchall()

    habits_status = [
        (habit_id, name, is_done(cursor, habit_id, today))
        for habit_id, name in checkbox_habits
    ]

    # Consistency grid: last GRID_DAYS days, oldest first.
    date_list = [today - dt.timedelta(i) for i in range(GRID_DAYS)]
    date_list.reverse()

    max_possible = len(checkbox_habits) + 1  # +1 for water
    grid_data = []

    for day in date_list:
        day_total = sum(
            1 for habit_id, _ in checkbox_habits
            if is_done(cursor, habit_id, day)
        )
        if water_total_for(cursor, water_id, day) >= water_goal:
            day_total += 1

        # Blend from near-black to bright green based on completion.
        ratio = day_total / max_possible
        r = int(30 + (60 - 30) * ratio)
        g = int(30 + (200 - 30) * ratio)
        b = int(30 + (90 - 30) * ratio)
        grid_data.append((day, f"rgb({r}, {g}, {b})"))

    water_percentage = min((water_total / water_goal) * 100, 100)
    blue_value = int(255 - (water_percentage * 1.5))

    conn.close()

    return render_template(
        "index.html",
        water_total=water_total,
        water_goal=water_goal,
        percentage=water_percentage,
        blue_value=blue_value,
        habits_status=habits_status,
        gridData=grid_data
    )


@app.route("/log/water/add", methods=["POST"])
def add_water():
    conn, cursor = get_connection()
    today = dt.date.today()

    water_id, water_goal = get_water_info(cursor)
    if water_total_for(cursor, water_id, today) < water_goal:
        cursor.execute(
            "INSERT INTO logs (Habit_ID, Date, value) VALUES (?, ?, ?)",
            (water_id, today, 1)
        )

    conn.commit()
    conn.close()
    return redirect(url_for("home"))


@app.route("/log/water/subtract", methods=["POST"])
def subtract_water():
    conn, cursor = get_connection()
    today = dt.date.today()

    water_id, _ = get_water_info(cursor)
    if water_total_for(cursor, water_id, today) > 0:
        cursor.execute(
            "INSERT INTO logs (Habit_ID, Date, value) VALUES (?, ?, ?)",
            (water_id, today, -1)
        )

    conn.commit()
    conn.close()
    return redirect(url_for("home"))


@app.route("/habit/add", methods=["POST"])
def add_habit():
    conn, cursor = get_connection()
    habit_name = request.form["habit_name"].strip()

    cursor.execute("SELECT COUNT(*) FROM habits")
    habit_count = cursor.fetchone()[0]

    if habit_name and habit_count < MAX_HABITS:
        cursor.execute(
            "INSERT INTO habits (Name, Type, Goal) VALUES (?, ?, ?)",
            (habit_name, "Checkbox", None)
        )

    conn.commit()
    conn.close()
    return redirect(url_for("home"))


@app.route("/habit/delete/<int:habit_id>", methods=["POST"])
def delete_habit(habit_id):
    conn, cursor = get_connection()

    cursor.execute("DELETE FROM logs WHERE Habit_ID = ?", (habit_id,))
    cursor.execute("DELETE FROM habits WHERE ID = ?", (habit_id,))

    conn.commit()
    conn.close()
    return redirect(url_for("home"))


@app.route("/habit/toggle/<int:habit_id>", methods=["POST"])
def toggle_habit(habit_id):
    conn, cursor = get_connection()
    today = dt.date.today()

    if is_done(cursor, habit_id, today):
        cursor.execute(
            "DELETE FROM logs WHERE Habit_ID = ? AND Date = ?",
            (habit_id, today)
        )
    else:
        cursor.execute(
            "INSERT INTO logs (Habit_ID, Date, value) VALUES (?, ?, ?)",
            (habit_id, today, 1)
        )

    conn.commit()
    conn.close()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)