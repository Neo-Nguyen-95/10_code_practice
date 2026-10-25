import psycopg

INSEPCT_COMMAND = """
SELECT *
FROM questions;
"""

with psycopg.connect(
    host="localhost",
    port=5433,
    dbname="science_question_bank",
    user="postgres",
    password="123"
) as conn:
    cursor = conn.execute(INSEPCT_COMMAND)
    print("Rows updated:")
    for row in cursor.fetchall():
        print(row)