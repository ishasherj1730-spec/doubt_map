import sqlite3

connection = sqlite3.connect("doubtmap.db")

cursor = connection.cursor()

print("Database connected successfully!")

# Students table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    department TEXT,
    semester INTEGER
)
""")

# Doubts table
cursor.execute("""
CREATE TABLE IF NOT EXISTS doubts (
    doubt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    subject TEXT NOT NULL,
    topic TEXT NOT NULL,
    description TEXT NOT NULL,
    doubt_type TEXT,
    difficulty TEXT,
    status TEXT DEFAULT 'Unresolved',
    date_submitted TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
)
""")

# Resources table
cursor.execute("""
CREATE TABLE IF NOT EXISTS resources (
    resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    topic TEXT,
    resource_name TEXT,
    resource_type TEXT,
    resource_link TEXT
)
""")

# Solutions table
cursor.execute("""
CREATE TABLE IF NOT EXISTS solutions (
    solution_id INTEGER PRIMARY KEY AUTOINCREMENT,
    doubt_id INTEGER,
    solution_text TEXT,
    date_added TEXT,
    FOREIGN KEY (doubt_id) REFERENCES doubts(doubt_id)
)
""")

cursor.execute("""
INSERT INTO students (name, email, department, semester)
VALUES ('Test Student', 'test@example.com', 'MCA', 3)
""")

connection.commit()

print("All tables created successfully!")

connection.close()
