import sqlite3
from datetime import date
from flask import Flask, render_template, redirect, url_for

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
    today = date.today()

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
    
    # Add up every logged water value for today.
    # The ? marks are placeholders — Python safely inserts
    # water_id and today into the query instead of pasting them
    # directly into the SQL string (this avoids SQL injection).
    cursor.execute('SELECT SUM(value) FROM logs WHERE Habit_ID = ? AND Date = ?', (water_id, today))
    water_total = cursor.fetchone()[0]
    if water_total is None: water_total = 0
    water_total = int(water_total)

    cursor.execute('SELECT * FROM logs WHERE Habit_ID = ? AND Date = ?', (workout_id, today))
    workout_row = cursor.fetchone()
    if workout_row is None: workout_done = False
    else: workout_done = True

    cursor.execute('SELECT * FROM logs WHERE Habit_ID = ? AND Date = ?', (multivitamin_id, today))
    multivitamin_row = cursor.fetchone()
    if multivitamin_row is None: multivitamin_done = False
    else: multivitamin_done = True


    cursor.execute('SELECT GOAL FROM habits WHERE Name = "Water" ')
    goal_value = int(cursor.fetchone()[0])
    percentage = min((water_total/goal_value) * 100,100)
    blue_value = int(255 - (percentage*1.5))
    
    # SUM() returns None (not 0) if there are no matching rows yet —
    # since logs is still empty, we catch that and default to 0.
    if water_total is None:
        water_total = 0


    # Only close the connection once every query is finished —
    # closing it earlier would make later queries crash.
    conn.close()

    # Pass both habits and water_total into the template so
    # the HTML file can actually use them.
    return render_template("index.html", habits=habits, water_total=water_total, percentage=percentage, blue_value=blue_value, workout_done=workout_done, multivitamin_done=multivitamin_done)

@app.route("/log/water/add", methods=["POST"])
def add_water():
   
    # Step 1: open a fresh connection — every route needs its own,
    # you can't reuse the one from home() since that request already finished.
    conn = sqlite3.connect("habits.db")
    cursor = conn.cursor()
 # get today's date, same as before
    today = date.today()
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

    today = date.today()

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

    today = date.today()

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
    
    today = date.today()

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



if __name__ == "__main__":
    app.run(debug=True)