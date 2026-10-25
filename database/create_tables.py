import psycopg

CREATE_TABLE_COMMAND = """
CREATE TABLE questions (
    id  INTEGER PRIMARY KEY,
    subject TEXT,
    grade INTEGER,
    question_text TEXT NOT NULL,
    answer TEXT
);
"""

with psycopg.connect(
    host="localhost",
    port=5433,
    dbname="science_question_bank",
    user="postgres",
    password="123"
) as conn:
    conn.execute(CREATE_TABLE_COMMAND)
    print("Successfully create questions table")