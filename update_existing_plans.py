import mysql.connector
from gemini_helper import generate_plan
import os
from dotenv import load_dotenv

load_dotenv()


conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

cursor = conn.cursor()

cursor.execute("""
SELECT id, title, description, deadline
FROM commitments
WHERE ai_plan IS NULL
OR ai_plan LIKE '%temporarily unavailable%'
""")

commitments = cursor.fetchall()

for commitment in commitments:

    id = commitment[0]
    title = commitment[1]
    description = commitment[2]
    deadline = commitment[3]

    print("Generating plan for:", title)

    try:
        plan = generate_plan(
        title,
        description,
        deadline
        )

        cursor.execute("""
        UPDATE commitments
        SET ai_plan = %s
        WHERE id = %s
        """, (plan, id))

        conn.commit()

        print("Success")

    except Exception as e:
        print("Failed:", e)

        plan = """
        AI Plan temporarily unavailable.

        Please try again later.
        """

        cursor.execute("""
        UPDATE commitments
        SET ai_plan = %s
        WHERE id = %s
        """, (plan, id))

        conn.commit()

cursor.close()
conn.close()