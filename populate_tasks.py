import mysql.connector
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
SELECT id, ai_plan
FROM commitments
""")

commitments = cursor.fetchall()

for commitment in commitments:

    commitment_id = commitment[0]
    ai_plan = commitment[1]

    if not ai_plan:
        continue

    if "=== TASK LIST ===" not in ai_plan:
        continue

    task_section = ai_plan.split("=== TASK LIST ===")[1]

    for line in task_section.split("\n"):

        task = line.strip()

        if not task:
            continue

        task = task.lstrip("* ").strip()

        cursor.execute("""
        INSERT INTO tasks
        (commitment_id, task_name)
        VALUES (%s, %s)
        """, (commitment_id, task))

conn.commit()

print("Tasks populated successfully!")

cursor.close()
conn.close()