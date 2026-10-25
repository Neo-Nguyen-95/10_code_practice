import psycopg

with psycopg.connect(
    host="localhost",
    port=5433,
    dbname="postgres",
    user="postgres",
    password="123",
    autocommit=True
) as conn:
    cursor = conn.execute("CREATE DATABASE science_question_bank;")
    print("Database created")