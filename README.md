# CommitMate AI

## Introduction

CommitMate AI is an AI-powered productivity companion designed to help users plan, prioritize, and complete commitments before deadlines are missed.

The platform goes beyond traditional reminder systems by generating actionable execution plans, tracking progress, identifying risks, and learning from past failures to provide smarter future recommendations.

This project was developed for the Google AI Studio Hackathon under the problem statement **"The Last-Minute Life Saver."**

---

## Problem Statement

Students, professionals, entrepreneurs, and working individuals frequently miss important deadlines, assignments, meetings, bill payments, interviews, and personal commitments.

Most productivity tools rely on passive reminders that are easy to ignore and provide limited assistance in actually completing tasks. Users often know what they need to do but struggle with planning, prioritization, and consistent execution.

The objective of this project is to build an AI-powered productivity companion that proactively helps users take meaningful action and improve task completion rates.

---

## Solution Overview

CommitMate AI leverages Google Gemini AI to transform commitments into structured execution plans.

The system assists users by:

- Breaking commitments into manageable tasks
- Tracking progress toward completion
- Identifying commitments at risk of failure
- Providing AI-generated improvement suggestions
- Learning from past failures to improve future planning

Rather than simply reminding users about deadlines, CommitMate AI focuses on helping users successfully complete their commitments.

---

## Key Features

### AI-Powered Commitment Planning
Generates detailed execution plans using Google Gemini AI.

### Automatic Task Generation
Converts AI-generated plans into actionable task checklists.

### Progress Tracking
Tracks task completion and calculates commitment progress.

### Risk Analysis
Identifies commitments that are likely to miss their deadlines.

### Plan Improvement
Generates improved plans for high-risk commitments.

### Failure Feedback System
Collects reasons for missed commitments to understand common challenges.

### Adaptive Learning
Uses historical failure feedback to generate smarter future recommendations.

### Smart Notifications
Provides reminders for upcoming, missed, and high-risk commitments.

---

## Application Modules

### Home Page
Provides an overview of the platform and its capabilities.

### Add Commitment
Allows users to create commitments with deadlines and categories.

### Dashboard
Displays commitments categorized as:

- Active
- Upcoming
- High Risk
- Missed
- Completed

### Commitment Details
Displays:

- AI-generated execution plan
- Task checklist
- Progress tracking
- Risk analysis
- Improvement suggestions

### Edit Commitment
Allows users to update commitment details and regenerate plans.

### Failure Review
Collects user feedback on missed commitments and stores learning data.

---

## Technology Stack

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript

### Backend
- Python
- Flask

### Database
- MySQL

### Artificial Intelligence
- Google Gemini API
- Google AI Studio

---

## Database Structure

### commitments
Stores commitment details, deadlines, categories, generated plans, and progress information.

### tasks
Stores task checklists and completion status.

### failure_feedback
Stores user feedback and learning information used for future recommendations.

---

## Google Technologies Used

- Google AI Studio
- Gemini API
- Gemini Models

Google Gemini is used to generate execution plans, analyze commitment risks, provide improvement suggestions, and support adaptive planning based on previous user feedback.

---

## Project Workflow

1. User creates a commitment.
2. Commitment details are sent to Gemini AI.
3. Gemini generates a structured execution plan.
4. Tasks are automatically created and stored.
5. Users track progress by completing tasks.
6. AI performs risk analysis based on progress and deadlines.
7. Improved plans can be generated when required.
8. Failure feedback is collected for missed commitments.
9. Future plans are enhanced using historical feedback.

---

## Future Scope

- Calendar integration
- Voice-enabled task management
- Mobile application support
- Personalized scheduling recommendations
- Advanced productivity analytics
- Integration with external productivity platforms

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/pallavidhamande12-prog/CommitMate-AI.git
cd CommitMate-AI
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file in the project root and add:

```env
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=commitmate_ai

GEMINI_API_KEY=your_gemini_api_key
```

### Run the Application

```bash
python app.py
```

### Open in Browser

```text
http://localhost:5000
```

---

## Repository

GitHub Repository:

https://github.com/pallavidhamande12-prog/CommitMate-AI

---

## Author

**Pallavi Dhamande**

Developed as part of the **Google AI Studio Hackathon 2026**.