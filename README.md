# CommitMate AI

## Introduction

CommitMate AI is an AI-powered productivity companion designed to help users plan, prioritize, and complete commitments before deadlines are missed.

The platform goes beyond traditional reminder systems by generating actionable execution plans, tracking progress, identifying risks, and learning from past failures to provide smarter future recommendations.

This project was developed for the Google AI Studio Hackathon under the problem statement **"The Last-Minute Life Saver."**

---

## Problem Statement

Students, professionals, and entrepreneurs frequently miss deadlines, assignments, meetings, bill payments, interviews, and important commitments.

Most productivity tools rely on passive reminders that are easy to ignore and provide limited assistance in actually completing tasks.

The goal of this project is to create an AI-powered productivity companion that proactively helps users take meaningful action and improve task completion.

---

## Solution Overview

CommitMate AI uses Google Gemini AI to transform user commitments into structured execution plans.

The platform assists users by:

- Breaking commitments into manageable tasks
- Tracking progress toward completion
- Detecting commitments that are at risk
- Providing AI-generated improvement suggestions
- Learning from past failures to improve future planning

---

## Key Features

- AI-powered commitment planning
- Automatic task generation
- Progress tracking dashboard
- Risk analysis for commitments
- AI-generated plan improvement
- Failure feedback collection
- Adaptive learning from previous commitments
- Smart notifications and reminders

---

## Application Modules

### Home Page
Provides an overview of the platform and its features.

### Add Commitment
Allows users to create commitments with deadlines and categories.

### Dashboard
Displays commitments grouped into:
- Active
- Upcoming
- High Risk
- Missed
- Completed

### Commitment Details
Shows:
- AI-generated execution plan
- Task checklist
- Progress tracking
- Risk analysis
- Improvement suggestions

### Failure Review
Collects user feedback on missed commitments to improve future recommendations.

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
Stores commitment details, deadlines, categories, plans, and progress information.

### tasks
Stores generated task lists and completion status.

### failure_feedback
Stores user feedback and learning data used for future recommendations.

---

## Google Technologies Used

- Google AI Studio
- Gemini API
- Gemini Models

---

## Project Workflow

1. User creates a commitment.
2. Gemini AI generates an execution plan.
3. Tasks are automatically created.
4. User tracks task completion.
5. Progress is monitored continuously.
6. AI performs risk analysis.
7. Improved plans can be generated if required.
8. Failure feedback is collected for missed commitments.
9. Future plans are enhanced using historical feedback.

---

## Future Scope

- Calendar integration
- Voice-enabled task management
- Mobile application support
- Personalized scheduling recommendations
- Advanced productivity analytics

---

## Installation

```bash
git clone <repository-url>
cd CommitMate-AI
pip install -r requirements.txt