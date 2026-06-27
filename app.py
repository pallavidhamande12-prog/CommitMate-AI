from flask import Flask, render_template, request, redirect
import mysql.connector
from gemini_helper import generate_plan, analyze_risk, analyze_failure, regenerate_plan
import re
from datetime import datetime, date
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# ---------------- DATABASE ----------------
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = db.cursor()

#---------------- CATEGORY ----------------
def get_category(commitment, progress):

    deadline = commitment[3]
    days_left = (deadline - date.today()).days

    # COMPLETED
    if progress == 100:
        return "completed"

    # MISSED
    if days_left < 0:
        return "missed"

    # UPCOMING (not started yet, but still time)
    if progress == 0 and days_left > 1:
        return "upcoming"

    # HIGH RISK (ONLY if actually overdue pressure OR low progress on longer tasks)
    if days_left > 0 and days_left <= 2 and progress < 40:
        return "high_risk"

    # SAME-DAY / SHORT TASK HANDLING (IMPORTANT FIX)
    if days_left == 0:
        if progress >= 50:
            return "active"
        else:
            return "high_risk"

    # NORMAL WORKING STATE
    return "active"

# ---------------- TASK PARSER ----------------
def extract_tasks(ai_plan):

    if not ai_plan:
        return []

    text = ai_plan.lower()

    # find task section in flexible way
    match = re.split(r"task list[:\-]?", ai_plan, flags=re.IGNORECASE)

    if len(match) < 2:
        return []

    task_block = match[-1]

    tasks = []

    for line in task_block.split("\n"):

        line = line.strip()

        # remove bullets, numbering, symbols
        line = re.sub(r"^[-•*\d\.\)\s]+", "", line)

        if len(line) > 2:
            if re.fullmatch(r"[=\-_*]+", line):
                continue
            tasks.append(line)

    return tasks

# ---------------- POSSIBLE FAILURE REASONS ----------------
STUDY_REASONS = [
    "Started preparation too late",
    "Too many topics to cover",
    "Poor time management",
    "Lack of revision",
    "College assignments consumed time",
    "Difficulty understanding concepts",
    "Lost motivation",
    "Health issues"
]

WORK_REASONS = [
    "Unrealistic deadline",
    "Too many parallel tasks",
    "Dependency on others",
    "Poor time management",
    "Unexpected work arrived",
    "Technical difficulties",
    "Lost motivation",
    "Health issues"
]

PERSONAL_REASONS = [
    "Family commitments",
    "Lack of consistency",
    "Priorities changed",
    "Lost motivation",
    "Health issues",
    "Poor time management",
    "Unexpected personal events"
]

FINANCE_REASONS = [
    "Insufficient funds",
    "Unexpected expenses",
    "Poor budgeting",
    "Delayed income",
    "Priorities changed",
    "Lack of planning",
    "Health issues"
]

# ---------------- HOME ----------------
@app.route('/')
def home():

    cursor.execute("SELECT * FROM commitments")
    commitments = cursor.fetchall()

    today = date.today()

    high_risk_count = 0
    upcoming_count = 0
    missed_count = 0

    for c in commitments:

        # get progress
        cursor.execute("""
            SELECT COUNT(*) FROM tasks WHERE commitment_id=%s
        """, (c[0],))
        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM tasks 
            WHERE commitment_id=%s AND is_completed=1
        """, (c[0],))
        done = cursor.fetchone()[0]

        progress = int((done / total) * 100) if total else 0

        # SINGLE SOURCE OF TRUTH
        category = get_category(c, progress)

        # COUNT BASED ON CATEGORY
        if category == "missed":
            missed_count += 1

        elif category == "high_risk":
            high_risk_count += 1

        elif category == "upcoming":
            upcoming_count += 1

    return render_template(
        'index.html',
        high_risk_count=high_risk_count,
        upcoming_count=upcoming_count,
        missed_count=missed_count,
        commitments=commitments,
        active_commitments=len(commitments)
    )


# ---------------- ADD ----------------
@app.route('/add', methods=['GET', 'POST'])
def add_commitment():

    if request.method == "POST":

        title = request.form['title']
        description = request.form['description']
        deadline = request.form['deadline']
        category = request.form['category']

        # Fetch previous failure reasons from same category
        cursor.execute("""
            SELECT reason
            FROM failure_feedback
            WHERE category=%s
        """, (category,))

        failure_rows = cursor.fetchall()

        previous_failures = "\n".join(
            [row[0] for row in failure_rows]
        )

        adaptive_plan = False

        if previous_failures.strip():
            adaptive_plan = True

        try:

            plan = generate_plan(
                title,
                description,
                deadline,
                previous_failures=previous_failures
            )

        except Exception as e:

            print("Gemini failed:", e)

            plan = """
AI Plan temporarily unavailable.

Please try again later.
"""

        cursor.execute("""
            INSERT INTO commitments
            (
                title,
                description,
                deadline,
                category,
                ai_plan,
                adaptive_plan
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            title,
            description,
            deadline,
            category,
            plan,
            adaptive_plan
        ))

        db.commit()

        commitment_id = cursor.lastrowid

        tasks = extract_tasks(plan)

        for task in tasks:

            cursor.execute("""
                INSERT INTO tasks
                (commitment_id, task_name)
                VALUES (%s, %s)
            """, (
                commitment_id,
                task
            ))

        db.commit()

        return redirect(f"/commitment/{commitment_id}")

    return render_template('add_commitment.html')

# ---------------- VIEW ALL ----------------
@app.route('/view_commitments')
def view_commitments():

    cursor.execute("SELECT * FROM commitments")
    commitments = cursor.fetchall()

    categorized = {
        "active": [],
        "completed": [],
        "upcoming": [],
        "high_risk": [],
        "missed": []
    }

    for c in commitments:

        cursor.execute("""
            SELECT COUNT(*) FROM tasks WHERE commitment_id=%s
        """, (c[0],))
        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM tasks 
            WHERE commitment_id=%s AND is_completed=1
        """, (c[0],))
        done = cursor.fetchone()[0]

        progress = int((done / total) * 100) if total else 0

        category = get_category(c, progress)

        categorized[category].append({
            "data": c,
            "progress": progress
        })

    return render_template(
        "view_commitments.html",
        categorized=categorized
    )

# ---------------- DETAILS PAGE ----------------
@app.route('/commitment/<int:id>')
def commitment_details(id):

    try:
        cursor.execute("SELECT * FROM commitments WHERE id=%s", (id,))
        commitment = cursor.fetchone()
        adaptive_plan = commitment[7]

        if not commitment:
            return "Commitment not found"

        ai_plan = commitment[6] or ""

        detailed_plan = ai_plan.split("TASK LIST")[0].strip()

        cursor.execute("""
            SELECT * FROM tasks WHERE commitment_id=%s
        """, (id,))
        tasks = cursor.fetchall()

        total = len(tasks)
        done = 0

        for task in tasks:
            if task[3] == 1:
                done += 1

        progress = int((done / total) * 100) if total else 0

        today = date.today()

        deadline_missed = (
            commitment[3] < today and progress < 100
    )

        risk = None  
        improve_failed = request.args.get(
        "improve_failed"
        )
        return render_template(
            "commitment_details.html",
            commitment=commitment,
            tasks=tasks,
            detailed_plan=detailed_plan,
            progress=progress,
            risk=risk,
            deadline_missed=deadline_missed,
            improve_failed=improve_failed,
            adaptive_plan=adaptive_plan
        )

    except Exception as e:
        print("DETAIL PAGE ERROR:", e)
        return "Something went wrong while loading commitment."

# ---------------- EDIT ----------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_commitment(id):

    cursor.execute("""
        SELECT * FROM commitments
        WHERE id=%s
    """, (id,))

    commitment = cursor.fetchone()

    if not commitment:
        return "Commitment not found"

    if request.method == "POST":

        title = request.form['title']
        description = request.form['description']
        deadline = request.form['deadline']

        category = commitment[4]

        # Fetch previous failures
        cursor.execute("""
            SELECT reason
            FROM failure_feedback
            WHERE category=%s
        """, (category,))

        failure_rows = cursor.fetchall()

        previous_failures = "\n".join(
            [row[0] for row in failure_rows]
        )

        try:

            plan = generate_plan(
                title,
                description,
                deadline,
                previous_failures=previous_failures
            )

        except Exception as e:

            print("Edit AI Error:", e)

            plan = """
AI Plan temporarily unavailable.

Please try again later.
"""

        # Update commitment
        cursor.execute("""
            UPDATE commitments
            SET title=%s,
                description=%s,
                deadline=%s,
                ai_plan=%s
            WHERE id=%s
        """, (
            title,
            description,
            deadline,
            plan,
            id
        ))

        # Delete old tasks
        cursor.execute("""
            DELETE FROM tasks
            WHERE commitment_id=%s
        """, (id,))

        # Generate new tasks
        tasks = extract_tasks(plan)

        for task in tasks:

            cursor.execute("""
                INSERT INTO tasks
                (commitment_id, task_name)
                VALUES (%s, %s)
            """, (
                id,
                task
            ))

        db.commit()

        return redirect(f"/commitment/{id}")

    return render_template(
        "edit_commitment.html",
        commitment=commitment
    )


# ---------------- RISK ANALYSIS (BUTTON ONLY) ----------------
@app.route('/risk/<int:id>')
def risk_analysis(id):

    try:
        cursor.execute("SELECT title FROM commitments WHERE id=%s", (id,))
        title = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tasks WHERE commitment_id=%s", (id,))
        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM tasks 
            WHERE commitment_id=%s AND is_completed=1
        """, (id,))
        done = cursor.fetchone()[0]

        progress = int((done / total) * 100) if total else 0

        risk = analyze_risk(title, progress, done, total)

        show_improve = False
        print("RISK RESPONSE:")
        print(risk)

        if isinstance(risk, str):
            if "high" in risk.lower():
                show_improve = True

    except Exception as e:
        print("Risk error:", e)

        risk = {
            "level": "Unavailable",
            "reason": "AI failed or quota exceeded",
            "suggestions": "Retry after some time"
        }

    cursor.execute("SELECT * FROM commitments WHERE id=%s", (id,))
    commitment = cursor.fetchone()

    cursor.execute("SELECT * FROM tasks WHERE commitment_id=%s", (id,))
    tasks = cursor.fetchall()

    ai_plan = commitment[6]
    detailed_plan = ai_plan.split("TASK LIST")[0]

    return render_template(
        "commitment_details.html",
        commitment=commitment,
        tasks=tasks,
        detailed_plan=detailed_plan,
        progress=progress,
        risk=risk,
        show_improve=show_improve
    )

# ---------------- UPDATE TASK ----------------
@app.route('/update_task/<int:task_id>', methods=['POST'])
def update_task(task_id):

    # Get commitment id of this task
    cursor.execute("""
        SELECT commitment_id
        FROM tasks
        WHERE id=%s
    """, (task_id,))

    commitment_id = cursor.fetchone()[0]

    # Get deadline of commitment
    cursor.execute("""
        SELECT deadline
        FROM commitments
        WHERE id=%s
    """, (commitment_id,))

    deadline = cursor.fetchone()[0]

    # If deadline already missed, don't allow updates
    if deadline < date.today():
        return redirect(f"/commitment/{commitment_id}")

    # Otherwise update task normally
    cursor.execute("""
        UPDATE tasks
        SET is_completed = NOT is_completed
        WHERE id=%s
    """, (task_id,))

    db.commit()

    return redirect(f"/commitment/{commitment_id}")


# ---------------- RETRY AI ----------------
@app.route('/retry_ai/<int:id>')
def retry_ai(id):

    cursor.execute("""
        SELECT title,
               description,
               deadline,
               category
        FROM commitments
        WHERE id=%s
    """, (id,))

    data = cursor.fetchone()

    if not data:
        return "Commitment not found"

    title, description, deadline, category = data

    # Fetch previous failure reasons from same category
    cursor.execute("""
        SELECT reason
        FROM failure_feedback
        WHERE category=%s
    """, (category,))

    failure_rows = cursor.fetchall()

    previous_failures = "\n".join(
        [row[0] for row in failure_rows]
    )

    try:

        plan = generate_plan(
            title,
            description,
            deadline,
            previous_failures=previous_failures
        )

    except Exception as e:

        print("Retry failed:", e)

        plan = """
AI Plan temporarily unavailable.

Please try again later.
"""

    # Update AI Plan
    cursor.execute("""
        UPDATE commitments
        SET ai_plan=%s
        WHERE id=%s
    """, (
        plan,
        id
    ))

    # Delete old tasks
    cursor.execute("""
        DELETE FROM tasks
        WHERE commitment_id=%s
    """, (id,))

    # Generate new tasks
    tasks = extract_tasks(plan)

    for task in tasks:

        cursor.execute("""
            INSERT INTO tasks
            (commitment_id, task_name)
            VALUES (%s, %s)
        """, (
            id,
            task
        ))

    db.commit()

    return redirect(f"/commitment/{id}")

# ---------------- IMPROVE PLAN ----------------
@app.route('/improve/<int:id>')
def improve_plan(id):

    cursor.execute("""
        SELECT title,
               description,
               deadline,
               ai_plan
        FROM commitments
        WHERE id=%s
    """, (id,))

    data = cursor.fetchone()

    if not data:
        return "Commitment not found"

    title, description, deadline, old_plan = data

    try:

        new_plan = regenerate_plan(
            title,
            description,
            deadline,
            old_plan
        )

        # UPDATE PLAN ONLY IF GEMINI SUCCEEDS
        cursor.execute("""
            UPDATE commitments
            SET ai_plan=%s
            WHERE id=%s
        """, (
            new_plan,
            id
        ))

        # DELETE OLD TASKS
        cursor.execute("""
            DELETE FROM tasks
            WHERE commitment_id=%s
        """, (id,))

        # INSERT NEW TASKS
        tasks = extract_tasks(new_plan)

        for task in tasks:

            cursor.execute("""
                INSERT INTO tasks
                (commitment_id, task_name)
                VALUES (%s, %s)
            """, (
                id,
                task
            ))

        db.commit()

    except Exception as e:

        print("Improve Plan Error:", e)

        # KEEP OLD PLAN + OLD TASKS
        return redirect(
            f"/commitment/{id}?improve_failed=1"
        )

    return redirect(f"/commitment/{id}")

# ---------------- ANALYZE FAILURE ----------------
@app.route('/failure_analysis/<int:id>')
def failure_analysis(id):

    cursor.execute("""
        SELECT * FROM commitments
        WHERE id=%s
    """, (id,))

    commitment = cursor.fetchone()

    category = commitment[4]

    if category.lower() == "study":
        reasons = STUDY_REASONS

    elif category.lower() == "work":
        reasons = WORK_REASONS

    elif category.lower() == "personal":
        reasons = PERSONAL_REASONS

    else:
        reasons = FINANCE_REASONS

    return render_template(
        "failure_analysis.html",
        commitment=commitment,
        reasons=reasons
    )

# ---------------- SUBMIT FAILURE FEEDBACK ----------------
@app.route('/submit_failure_feedback/<int:id>', methods=['POST'])
def submit_failure_feedback(id):

    selected_reasons = request.form.getlist('reasons')
    other_reason = request.form.get('other_reason')

    cursor.execute("""
        SELECT category
        FROM commitments
        WHERE id=%s
    """, (id,))

    category = cursor.fetchone()[0]

    for reason in selected_reasons:

        cursor.execute("""
            INSERT INTO failure_feedback
            (commitment_id, category, reason)
            VALUES (%s, %s, %s)
        """, (id, category, reason))

    if other_reason.strip():

        cursor.execute("""
            INSERT INTO failure_feedback
            (commitment_id, category, reason, other_reason)
            VALUES (%s, %s, %s, %s)
        """, (
            id,
            category,
            "Other",
            other_reason
        ))

    db.commit()

    return """
    <h2>✅ Thank You!</h2>
    <p>Your feedback has been recorded.</p>
    <a href="/view_commitments">
        Return to Dashboard
    </a>
    """

# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
def delete_commitment(id):

    cursor.execute("DELETE FROM tasks WHERE commitment_id=%s", (id,))
    cursor.execute("DELETE FROM commitments WHERE id=%s", (id,))

    db.commit()

    return redirect('/view_commitments')


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)