import psycopg

CHECK_COMMAND = "SELECT current_database(), current_user;"
USUAL_COMMAND = "SELECT * FROM questions;"

with psycopg.connect(
    host="localhost",
    port=5433,
    dbname="science_question_bank",
    user="postgres",
    password="123"
) as conn:
    cursor = conn.execute(USUAL_COMMAND)
    result = cursor.fetchall()
    print(result)