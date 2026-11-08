import psycopg

INSEPCT_TABLE_COMMAND = """
SELECT *
FROM questions;
"""

INSPECT_DATABASE_COMMAND = """
SELECT datname
FROM pg_database
WHERE datistemplate = false
ORDER BY datname;
"""

INSPECT_TABLE_IN_DATABASE_COMMAND = """
SELECT table_name, column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name IN ('questions', 'subjects')
ORDER BY table_name;
"""

with psycopg.connect(
    host="localhost",
    port=5433,
    dbname="science_question_bank",
    user="postgres",
    password="123"
) as conn:
    print(
        '\nList of DB:'
        '\n----------'
        )
    cursor = conn.execute(INSPECT_DATABASE_COMMAND)
    for row in cursor.fetchall():
        print(row)

    print('\nTables and their attributes:')
    print(
        '\n(table_name, column_name, data_type, is_nullable)'
        '\n-------------------------------------------------'
        )
    cursor = conn.execute(INSPECT_TABLE_IN_DATABASE_COMMAND)
    for row in cursor.fetchall():
        print(row)

    print('\nData of a table:')
    cursor = conn.execute(INSEPCT_TABLE_COMMAND)
    for row in cursor.fetchall():
        print(row)