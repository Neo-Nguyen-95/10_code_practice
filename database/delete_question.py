import psycopg

DELETE_COMMAND = """
DELETE FROM questions
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
        DELETE_COMMAND,
        (2,),
        )
    print("Rows updated:", cursor.rowcount)