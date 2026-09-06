import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "habits.db")

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS habits(
        ID INTEGER PRIMARY KEY,
        Name varchar(255) NOT NULL,
        Type varchar(255) NOT NULL,
        Goal varchar(255)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs(
        ID INTEGER PRIMARY KEY,
        Habit_ID int NOT NULL,
        Date date NOT NULL,
        value float NOT NULL
    )
''')

cursor.execute('SELECT COUNT(*) FROM habits')
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO habits (Name, Type, Goal) VALUES ('Multivitamin', 'Checkbox', NULL)")
    cursor.execute("INSERT INTO habits (Name, Type, Goal) VALUES ('Workout', 'Checkbox', NULL)")
    cursor.execute("INSERT INTO habits (Name, Type, Goal) VALUES ('Water', 'Counter', 8)")

conn.commit()
conn.close()