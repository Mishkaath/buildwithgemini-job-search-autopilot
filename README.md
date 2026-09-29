# Job Search Autopilot

![Demo](demo.gif)

An autonomous AI agent designed to manage the end-to-end job search, application, and tracking lifecycle. Built with the Google Agent Platform (ADK), reasoning engines, and a custom FastAPI + vanilla web UI, it acts as your personal job hunting copilot.

## Core Capabilities

1. **PROMPT STUDIO**: A configuration panel where users can write and save natural language search sessions (roles, salary bands, locations, skills, company filters). The agent intelligently parses these into structured filters.
2. **DISCOVERY ENGINE**: Automatically pulls and deduplicates relevant jobs across public ATS boards (Greenhouse, Lever, Ashby), company web searches, and career news.
3. **RANKING & FIT SCORING**: Scores each job (0-100) against your active criteria by evaluating skill overlap using Gemini, providing visible rationale for its score.
4. **RESUME TAILORING ENGINE**: Takes your master profile and generates per-job tailored resume variants strictly aligned to the job description—without fabricating facts.
5. **TRACKER DASHBOARD & RESEARCH**: A split-screen, multi-tab UI with a dense table showing Company, Role, Status, Fit Score, Date Applied, Resume Version used, HR Contacts for referrals, and Interview Prep topics.
6. **EMAIL INTELLIGENCE**: Parses inbound notifications/emails to auto-advance application statuses.

## UI Design & Architecture

- **Theme**: Dark/navy & purple layout using deep purple and a gold/amber accent.
- **Layout**: Three panels/tabs - "Dashboard Tracker", "Prompt Studio", and "AI Assistant Chat".
- **Backend**: Python 3.11 with FastAPI proxying A2A requests to Agent Runtime, tracked via Firestore.
