import psycopg

VIEW_QUESTION_TABLE_COMMAND = """
SELECT *
FROM questions
LIMIT 5
"""

CREATE_TABLE_COMMAND = """
CREATE TABLE questions (
    id  INTEGER PRIMARY KEY,
    subject TEXT,
    grade INTEGER,
    question_text TEXT NOT NULL,
    answer TEXT
);
"""

CREATE_SUBJECT_COMMAND = """
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
"""

ADD_FOREIGN_KEY_COMMAND = """
ALTER TABLE questions
ADD COLUMN subject_id INTEGER REFERENCES subjects(id)
"""

UPDATE_SUBJECT_ID_TO_QUESTIONS = """
UPDATE questions
SET subject_id = %s
WHERE subject = %s;
"""
subject_mapping = (
    (1, 'Physics'),
    (2, 'Chemistry'),
    (3, 'Biology')
)

# TEST_COMMAND = """
# SELECT questions.id, questions.question_text, subjects.name
# FROM questions
# JOIN subjects ON questions.subject_id = subjects.id
# WHERE subjects.name = 'Physics'
# ORDER BY questions.id;
# """

TEST_COMMAND = """
SELECT id, question_text
FROM questions
WHERE subject_id IS NULL;
"""

with psycopg.connect(
    host="localhost",
    port=5433,
    dbname="science_question_bank",
    user="postgres",
    password="123"
) as conn:
    # conn.execute(CREATE_SUBJECT_COMMAND)
    # print("Successfully create the table")

    # for item in subject_mapping:
    #     conn.execute(UPDATE_SUBJECT_ID_TO_QUESTIONS, item)
    #     print("Successful action")

    cursor = conn.execute(TEST_COMMAND)
    results = cursor.fetchall()
    for result in results:
        print(result)

    # conn.execute(TEST_COMMAND)
    # print("Done!")