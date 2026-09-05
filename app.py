import sqlite3
import datetime as dt
from flask import Flask, render_template, redirect, url_for
from flask import request
app = Flask(__name__)

@app.route("/")
def home():
    conn = sqlite3.connect("habits.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM habits")
    habits = cursor.fetchall()

    today = dt.date.today()
    dateList = []
    gridData = []

    for i in range(14):
        dateList.append(today - dt.timedelta(i))
    dateList.reverse()

    cursor.execute('SELECT ID FROM habits WHERE Name = "Water"')
    water_id = cursor.fetchone()[0]


    cursor.execute('SELECT SUM(value) FROM logs WHERE Habit_ID = ? AND Date = ?', (water_id, today))
    water_total = cursor.fetchone()[0]
    if water_total is None: water_total = 0
    water_total = int(water_total)

    # Generic checkbox-habit status — replaces the old separate
    # workout_done / multivitamin_done checks. Works for any number
    # of checkbox-type habits, not just these two by name.
    cursor.execute('SELECT * FROM habits WHERE Type = "Checkbox"')
    checkbox_habits = cursor.fetchall()

    habits_status = []
    for habit in checkbox_habits:
        cursor.execute('SELECT * FROM logs WHERE Habit_ID = ? AND Date = ?', (habit[0], today))
        log_row = cursor.fetchone()
        if log_row is None:
            habit_done = False
        else:
            habit_done = True
        habits_status.append((habit[0], habit[1], habit_done))

    # Consistency grid — still uses workout_id/multivitamin_id/water_id
    # directly, since this scoring is specific to those three habits for now.
    max_possible = len(checkbox_habits) + 1  # +1 for water

    for day in dateList:
        dayTotal = 0
        cursor.execute('SELECT SUM(value) FROM logs WHERE Habit_ID = ? AND Date = ?', (water_id, day))
        day_water_total = cursor.fetchone()[0]
        if day_water_total is None: day_water_total = 0

        for habit in checkbox_habits:
            cursor.execute('SELECT * FROM logs WHERE Habit_ID = ? AND Date = ?', (habit[0], day))
            log_row = cursor.fetchone()
            if log_row is not None:
                dayTotal += 1

        if day_water_total == 8:
            dayTotal += 1

        day_percentage = (dayTotal / max_possible) * 100

        # Interpolate from gray (65,64,64) to green (76,175,122) based on percentage
        r = int(30 + (60 - 30) * (day_percentage / 100))
        g = int(30 + (200 - 30) * (day_percentage / 100))
        b = int(30 + (90 - 30) * (day_percentage / 100))    
        day_color = f"rgb({r}, {g}, {b})"

        gridData.append((day, day_color))
        
       

    cursor.execute('SELECT GOAL FROM habits WHERE Name = "Water" ')
    goal_value = int(cursor.fetchone()[0])
    percentage = min((water_total / goal_value) * 100, 100)
    blue_value = int(255 - (percentage * 1.5))

    conn.close()

    return render_template(
        "index.html",
        habits=habits,
        water_total=water_total,
        percentage=percentage,
        blue_value=blue_value,
        habits_status=habits_status,
        gridData=gridData
    )

@app.route("/log/water/add", methods=["POST"])
def add_water():
   
    # Step 1: open a fresh connection — every route needs its own,
    # you can't reuse the one from home() since that request already finished.
    conn = sqlite3.connect("habits.db")
    cursor = conn.cursor()
 # get today's date, same as before
    today = dt.date.today()
    # Step 2: find water's ID, same as you did in home()
    cursor.execute('SELECT ID FROM habits WHERE Name = "Water"')
    water_id = cursor.fetchone()[0]

    cursor.execute('SELECT SUM(value) FROM logs WHERE Habit_ID = ? AND Date = ?', (water_id, today))
    water_total = cursor.fetchone()[0]
    cursor.execute('SELECT GOAL FROM habits WHERE Name = "Water" ')
    goal_value = int(cursor.fetchone()[0])

   

    # Step 4: insert a new row into logs — this is the actual "save" moment.
    # value = 1 means "one cup was logged."
    if water_total == goal_value: 
        pass
    else: 
        cursor.execute("INSERT INTO logs (Habit_ID, Date, value) VALUES (?, ?, ?)", (water_id, today, 1))

    # Step 5: commit — this writes the change to the actual .db file.
    # Without this line, the insert would be thrown away when the connection closes.
    conn.commit()
    conn.close()

    # Step 6: send the browser back to the homepage.
    # url_for("home") looks up the URL for the function named "home" —
    # safer than hardcoding "/" since it still works if the route ever changes.
    return redirect(url_for("home"))


@app.route("/log/water/subtract", methods=["POST"])
def subtract_water():
    conn = sqlite3.connect('habits.db')
    cursor = conn.cursor()

    cursor.execute('SELECT ID FROM habits WHERE Name = "Water"')
    water_id = cursor.fetchone()[0]

    today = dt.date.today()

    cursor.execute('SELECT SUM(value) FROM logs WHERE Habit_ID = ? AND Date = ?', (water_id, today))
    water_total = cursor.fetchone()[0]
    cursor.execute('SELECT GOAL FROM habits WHERE Name = "Water" ')
    goal_value = int(cursor.fetchone()[0])
        # Step 4: insert a new row into logs — this is the actual "save" moment.
        # value = 1 means "one cup was logged."
    if water_total < 1:
        pass
    else: 
        cursor.execute("INSERT INTO logs (Habit_ID, Date, value) VALUES (?, ?, ?)", (water_id, today, -1))

    conn.commit()
    conn.close()

    return redirect(url_for("home"))



@app.route('/habit/add', methods=['POST'])
def add_habit():

    conn = sqlite3.connect("habits.db")
    cursor = conn.cursor()

    habit_name = request.form["habit_name"]
    cursor.execute("SELECT COUNT(*) FROM habits")
    habit_count = cursor.fetchone()[0]
    if habit_count < 5:
        cursor.execute("INSERT INTO habits (Name, Type, Goal) VALUES (?, ?, ?)", (habit_name, "Checkbox", None))

    conn.commit()
    conn.close()

    return redirect(url_for("home"))

@app.route('/habit/delete/<int:habit_id>', methods=['POST'])
def delete_habit(habit_id):
    conn = sqlite3.connect('habits.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM logs WHERE Habit_ID = ?', (habit_id,))
    cursor.execute('DELETE FROM habits WHERE ID = ?', (habit_id,))

    conn.commit()
    conn.close()

    return redirect(url_for('home'))


@app.route('/habit/toggle/<int:habit_id>', methods=["POST"])
def toggle_habit(habit_id):
    conn = sqlite3.connect('habits.db')
    cursor = conn.cursor()

    today = dt.date.today()

    cursor.execute('SELECT * FROM logs WHERE Habit_ID = ? AND Date = ?', (habit_id,today))
    habit_row = cursor.fetchone()

    if habit_row is None: habit_done = False
    else: habit_done = True
    
    if habit_done:
        cursor.execute('DELETE FROM logs WHERE Habit_ID = ? AND Date = ?', (habit_id,today))
    else: 
        cursor.execute("INSERT INTO logs (Habit_ID, Date, value) VALUES (?, ?, ?)", (habit_id, today, 1))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for("home"))



if __name__ == "__main__":
    app.run(debug=True)