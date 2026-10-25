import csv
import psycopg

INSERT_COMMAND = """
INSERT INTO questions (id, subject, grade, question_text, answer)
VALUES (%s, %s, %s, %s, %s);
"""

with open("database/questions.csv", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    with psycopg.connect(
            host="localhost",
            port=5433,
            dbname="science_question_bank",
            user="postgres",
            password="123"
        ) as conn:
        for row in reader:
            values = (
                int(row["id"]),
                row["subject"],
                int(row["grade"]),
                row['question_text'],
                row["answer"],
            )
            cursor = conn.execute(INSERT_COMMAND, values,)
            print("Rows inserted:", cursor.rowcount)