# PathFinder AI — Student Growth & Opportunity Navigator

A Streamlit application layer built on the existing Member 1–4 ML work.

## What the app includes

- Login / Sign Up
- Home dashboard
- Resume upload (PDF / DOCX)
- AI profile extraction from the resume
- Personal details + target career selection
- Skill assessment
- Skill gap detection
- Live opportunity matching from the existing opportunity cache
- Personalized learning roadmap
- What-If Career Simulator
- Progress tracking

## Run locally

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## Data flow

```text
Resume Upload
    ↓
Member 1 — Profile & Resume Intelligence
    ↓
Member 2 — Skill Assessment + Skill Gap Detection
    ↓
Member 3 — Opportunity Matching
    ↓
Member 4 — Roadmap + What-If Career Simulator
    ↓
Member 5 — Streamlit UI + Progress Tracking
```

The existing Member 1–4 modules remain in place. The Streamlit integration calls them after a user submits a resume and target career.

Authentication is a local SQLite demo database stored in `data/pathfinder_auth.db` after first use. For production multi-user deployment, replace this with a hosted authentication provider.
