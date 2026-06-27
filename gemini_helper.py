import os
from dotenv import load_dotenv
from google import genai
from datetime import date

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def generate_plan(
    title,
    description,
    deadline,
    previous_failures="",
    today=date.today()
):

    prompt = f"""
        You are CommitMate AI, an intelligent commitment planning assistant.

        
        
        Commitment Title:
        {title}

        Description:
        {description}

        Deadline:
        {deadline}

        Today's Date:
        {today}

        Learning Insights:
        {previous_failures}

        If previous failures exist:

        - Avoid repeating mistakes
        - Create more realistic timelines
        - Break large tasks into smaller tasks
        - Add consistency checkpoints


        Create a realistic and practical plan based strictly on the available time between today's date and the deadline.

        IMPORTANT:
        The entire plan MUST fit within the provided deadline.

        Do NOT create timelines extending beyond the deadline.
        Do NOT create month-wise plans unless the deadline is actually months away.
        Generate steps according to the available time remaining.

        Requirements:

        1. First create a section called DETAILED PLAN.
       - Break the work into logical steps.
       - Explain what should be done at each step.
       - Make the plan realistic according to the deadline.

        2. Then create a section called TASK LIST.
        - Create short actionable tasks.
       - One task per line.
       - Keep tasks concise.
       - Do not use paragraphs in this section.
       - Create as many tasks as necessary based on the commitment.

        Output Format:

        === DETAILED PLAN ===

        (Detailed plan here)

        === TASK LIST ===

        Task 1
        Task 2
        Task 3
        Task 4

        Keep the response clear, practical and deadline-focused.
        """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text

def regenerate_plan(title, description, deadline, old_plan):

    prompt = f"""
You are an adaptive productivity AI.

The user is currently behind schedule.

TASK:
Title: {title}
Description: {description}
Deadline: {deadline}

OLD PLAN:
{old_plan}

Now regenerate a NEW optimized plan with:
1. Shorter timeline
2. More realistic steps
3. Prioritized tasks only
4. STRICT maximum 5–7 tasks

Format:

=== DETAILED PLAN ===
...
=== TASK LIST ===
- task 1
- task 2
...
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text

def analyze_risk(title, progress, completed, total):

    prompt = f"""
You are a risk analysis AI.

Task: {title}

Progress: {progress}%
Completed Tasks: {completed}
Total Tasks: {total}

Return ONLY in this format:

LEVEL: High/Medium/Low

REASON:
(reason)

SUGGESTIONS:
(suggestions)
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text

def analyze_failure(title, description, category):

    prompt = f"""
You are a commitment failure analysis AI.

Commitment Title:
{title}

Description:
{description}

Category:
{category}

Analyze:

1. Possible reasons for failure
2. Planning mistakes
3. Time management issues
4. Suggestions for future commitments in the same category

Keep the answer practical and concise.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text