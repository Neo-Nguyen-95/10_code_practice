import psycopg

COMMAND = """
ALTER TABLE questions
ADD COLUMN subject_id INTEGER REFERENCES subjects(id)
"""

with psycopg.connect(
    host="localhost",
    port=5433,
    dbname="science_question_bank",
    user="postgres",
    password="123"
) as conn:
    conn.execute(COMMAND)
    print("Action successfully!")

    