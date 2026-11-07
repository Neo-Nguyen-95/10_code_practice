import psycopg

SUBJECT_DATA = (
    (1, "Physics"),
    (2, "Chemistry"),
    (3, "Biology"),
)

with psycopg.connect(
    host="localhost",
    port=5433,
    dbname="science_question_bank",
    user="postgres",
    password="123"
) as conn:
    for data in SUBJECT_DATA:
        conn.execute(
            """
            INSERT INTO subjects (id, name)
            VALUES (%s, %s);
            """,
            data
            )
        print("Insert values successfully!")