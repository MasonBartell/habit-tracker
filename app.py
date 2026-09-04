import sqlite3
import datetime as dt
from flask import Flask, render_template, redirect, url_for
from flask import request
app = Flask(__name__)

@app.route("/")
def home():
    # Open a connection to the database file, and get a cursor
    # to actually run SQL commands through that connection.
    conn = sqlite3.connect("habits.db")
    cursor = conn.cursor()

    
    # Get every row from the habits table.
    # fetchall() returns a list of tuples, one tuple per row,
    # in the order the columns were defined: (ID, Name, Type, Goal).
    cursor.execute("SELECT * FROM habits")
    habits = cursor.fetchall()

    # Get today's date as a Python date object, so we can filter
    # the logs table down to just today's entries.
    today = dt.date.today()
    dateList = []
    gridData = []

    for i in range(14):
        dateList.append(today - dt.timedelta(i))
    dateList.reverse() 
    # Look up Water's ID by name instead of hardcoding "3" —
    # this way it still works even if the habits table changes later.
    # fetchone() returns a single row (not a list), so [0] grabs
    # the first value out of that one-item tuple.
    cursor.execute('SELECT ID FROM habits WHERE Name = "Water"')
    water_id = cursor.fetchone()[0]

    cursor.execute('SELECT ID FROM habits Where Name = "Workout"')
    workout_id = cursor.fetchone()[0]

    cursor.execute('SELECT ID FROM habits Where Name = "Multivitamin"')
    multivitamin_id = cursor.fetchone()[0]

    cursor.execute('SELECT SUM(value) FROM logs WHERE Habit_ID = ? AND Date = ?', (water_id, today))
    water_total = int(cursor.fetchone()[0])
    if water_total is None: water_total = 0

    cursor.execute('SELECT * FROM logs WHERE Habit_ID = ? AND Date = ?', (workout_id, today))
    workout_row = cursor.fetchone()
    if workout_row is None: workout_done = False
    else: workout_done = True

    cursor.execute('SELECT * FROM logs WHERE Habit_ID = ? AND Date = ?', (multivitamin_id, today))
    multivitamin_row = cursor.fetchone()
    if multivitamin_row is None: multivitamin_done = False
    else: multivitamin_done = True

    
    for day in dateList:
        cursor.execute('SELECT SUM(value) FROM logs WHERE Habit_ID = ? AND Date = ?', (water_id, day))
        day_water_total = cursor.fetchone()[0]
        if day_water_total is None: day_water_total = 0

        cursor.execute('SELECT * FROM logs WHERE Habit_ID = ? AND Date = ?', (workout_id, day))
        workout_row = cursor.fetchone()
        if workout_row is None: day_workout_done = False
        else: day_workout_done = True

        cursor.execute('SELECT * FROM logs WHERE Habit_ID = ? AND Date = ?', (multivitamin_id, day))
        multivitamin_row = cursor.fetchone()
        if multivitamin_row is None: day_multivitamin_done = False
        else: day_multivitamin_done = True

        dayTotal = 0
        if day_water_total == 8:
            dayTotal += 1
        if day_workout_done:
            dayTotal += 1
        if day_multivitamin_done:
            dayTotal += 1
        gridData.append((day, dayTotal))


    cursor.execute('SELECT GOAL FROM habits WHERE Name = "Water" ')
    goal_value = int(cursor.fetchone()[0])
    percentage = min((water_total/goal_value) * 100,100)
    blue_value = int(255 - (percentage*1.5))
    
    


    # Only close the connection once every query is finished —
    # closing it earlier would make later queries crash.
    conn.close()

    # Pass both habits and water_total into the template so
    # the HTML file can actually use them.
    return render_template("index.html", habits=habits, water_total=water_total, percentage=percentage, blue_value=blue_value, workout_done=workout_done, multivitamin_done=multivitamin_done,gridData=gridData)

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

@app.route('/log/workout/toggle', methods=["POST"])
def toggle_workout():
    conn = sqlite3.connect("habits.db")
    cursor = conn.cursor()

    today = dt.date.today()

    cursor.execute('SELECT ID FROM habits Where Name = "Workout"')
    workout_id = cursor.fetchone()[0]

    cursor.execute('SELECT * FROM logs WHERE Habit_ID = ? AND Date = ?', (workout_id, today))
    workout_row = cursor.fetchone()
    if workout_row is None: workout_done = False
    else: workout_done = True

    if workout_done:
        cursor.execute('DELETE FROM logs WHERE Habit_ID = ? AND Date = ?', (workout_id,today))
    else: 
         cursor.execute("INSERT INTO logs (Habit_ID, Date, value) VALUES (?, ?, ?)", (workout_id, today, 1))

    conn.commit()
    conn.close()

    return redirect(url_for("home"))

@app.route('/log/multivitamin/toggle', methods=['POST'])
def toggle_multivitamin():

    conn = sqlite3.connect("habits.db")
    cursor = conn.cursor()
    
    today = dt.date.today()

    cursor.execute('SELECT ID FROM habits Where Name = "Multivitamin"')
    multivitamnin_id = cursor.fetchone()[0]

    cursor.execute('SELECT * FROM logs WHERE Habit_ID = ? AND Date = ?', (multivitamnin_id, today))
    multivitamin_row = cursor.fetchone()
    if multivitamin_row is None: multivitamin_done = False
    else: multivitamin_done = True
    
    if multivitamin_done:
        cursor.execute('DELETE FROM logs WHERE Habit_ID = ? AND Date = ?', (multivitamnin_id,today))
    else: 
        cursor.execute("INSERT INTO logs (Habit_ID, Date, value) VALUES (?, ?, ?)", (multivitamnin_id, today, 1))
    
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
    if habit_count < 4:
        cursor.execute("INSERT INTO habits (Name, Type, Goal) VALUES (?, ?, ?)", (habit_name, "Checkbox", None))

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)