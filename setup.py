import sqlite3

conn = sqlite3.connect("habits.db")
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

cursor.execute('''
    INSERT INTO habits (Name, Type, Goal) VALUES
    ('Multivitamin', 'Checkbox', NULL)
''')
cursor.execute('''
    INSERT INTO habits (Name, Type, Goal) VALUES
    ('Workout', 'Checkbox', NULL)
''')
cursor.execute('''
    INSERT INTO habits (Name, Type, Goal) VALUES
    ('Water', 'Counter', 8)
''')


conn.commit()
conn.close()