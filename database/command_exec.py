import psycopg

COMMAND = """
UPDATE questions
SET weight = 30
WHERE subject_id = 3;
"""

with psycopg.connect(
    host="localhost",
    port=5433,
    dbname="science_question_bank",
    user="postgres",
    password="123"
) as conn:
    conn.execute(COMMAND)
    print("Successful action!")