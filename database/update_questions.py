import psycopg

UPDATE_COMMAND = """
UPDATE questions
SET grade = %s
WHERE id = %s;
"""

with psycopg.connect(
    host="localhost",
    port=5433,
    dbname="science_question_bank",
    user="postgres",
    password="123"
) as conn:
    cursor = conn.execute(
        UPDATE_COMMAND,
        (10, 2)
        )
    print("Rows updated:", cursor.rowcount)