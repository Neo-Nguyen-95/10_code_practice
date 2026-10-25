import psycopg

with psycopg.connect(
    host="localhost",
    port=5433,
    dbname="science_question_bank",
    user="postgres",
    password="123"
) as conn:
    conn.execute(
        """
        INSERT INTO questions (id, subject, grade, question_text, answer)
        VALUES (%s, %s, %s, %s, %s);
        """,
        (2, "Chemistry", 10, "What is the chemical symbol for oxygen?", "O")
        )
    print("Insert values successfully!")