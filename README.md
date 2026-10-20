# 🥋 CP Coach

> An intelligent, personalized Competitive Programming Coach that analyzes your Codeforces submission history, diagnoses topic strengths and weaknesses, and prescribes tailored practice paths to level up your rating.

---

## ✨ Features

- **⚡ Instant Handle Analysis**: Enter **any** Codeforces handle to auto-sync their complete submission and contest rating history directly from the official Codeforces API.
- **📊 Topic Skill Radar**: Proprietary scoring formula combining accuracy percentage and attempt volume (capped to prevent volume bias) rendered with an interactive polygon radar chart.
- **🎯 Smart Recommendation Engine**:
  - Ingests the complete Codeforces catalog of **11,400+ problems** and 32,000+ topic tags into a normalized PostgreSQL database.
  - Automatically excludes problems you have already solved with verdict `OK`.
  - Scores candidate problems against your **current rating sweet spot** (+50 to +150 rating target) and **weak topic tags**.
  - Provides direct 1-click links to Codeforces with personalized pedagogical reasoning (e.g., *"Targets weak topic: bitmasks, dfs and similar"*).
- **🧪 Tested Algorithms**: Pytest test suite covering scoring bounds, descending rank stability, and recommendation filters.
- **🛡️ Secure By Design**: Environment variable separation with zero database credentials committed to source control.

---

## 🏗️ Architecture & Tech Stack

```
cp-coach/
├── backend/            # FastAPI REST API & Algorithm Layer
│   ├── main.py         # Endpoints (/stats, /score, /recommend, /sync)
│   ├── scorer.py       # Skill scoring formula (accuracy + volume)
│   ├── recommender.py  # Problem matching & ranking algorithm
│   ├── sync_user.py    # Codeforces API on-demand sync pipeline
│   └── tests.py        # Pytest unit tests for algorithms
├── frontend/           # React + TypeScript + Vite Dashboard
│   └── src/App.tsx     # Radar chart, handle search, practice cards, & skill bars
└── data/               # Database DDL & Batch Ingestion Scripts
    ├── create_tables.py   # PostgreSQL schema creation
    ├── load_problemset.py # Fast bulk upsert of 11,400+ CF problems
    └── fetch_cf.py        # Codeforces API data fetcher
```

### Technologies Used
- **Backend**: Python 3.13, [FastAPI](https://fastapi.tiangolo.com/), Uvicorn, psycopg2-binary, python-dotenv, Pytest
- **Database**: [PostgreSQL 18](https://www.postgresql.org/) (6 normalized tables with foreign keys and composite join tables)
- **Frontend**: [React 19](https://react.dev/), [TypeScript](https://www.typescriptlang.org/), [Vite](https://vitejs.dev/), [Recharts](https://recharts.org/)
- **Data Source**: [Codeforces Public REST API](https://codeforces.com/apiHelp)

---

## 🗄️ Database Schema

The database `cpcoach` consists of six normalized relational tables:
- `users`: Codeforces handle and creation timestamp.
- `problems`: `contest_id`, `problem_index`, `name`, and difficulty `rating` (unique on contest_id + problem_index).
- `tags`: Canonical Codeforces tags (e.g. `dp`, `graphs`, `greedy`).
- `problem_tags`: Many-to-many join table linking problems and tags.
- `submissions`: User submissions with verdict, programming language, timestamp, and contest ID.
- `rating_history`: Contest-by-contest rating progression.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL 16+ running locally with database `cpcoach`

### 1. Database Setup & Secrets
Create a `.env` file inside `backend/.env`:
```env
DB_NAME=cpcoach
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
```

Run table creation and problemset ingestion:
```powershell
cd data
..\backend\.venv\Scripts\python.exe create_tables.py
..\backend\.venv\Scripts\python.exe fetch_cf.py
..\backend\.venv\Scripts\python.exe load_problemset.py
```

### 2. Backend Setup
```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
API Documentation available at `http://localhost:8000/docs`.

Run unit tests:
```powershell
.venv\Scripts\python.exe -m pytest tests.py -v
```

### 3. Frontend Setup
```powershell
cd frontend
npm install
npm run dev
```
The app will be available at `http://localhost:5173`.

---

## 🗺️ Roadmap

- [x] **Phase 1**: Codeforces API data pipeline + PostgreSQL schema + basic dashboard.
- [x] **Phase 2**: Weighted topic skill scoring + unit tests + Recharts radar chart.
- [x] **Phase 3**: Global 11,400+ problem catalog ingestion + personalized recommendation engine.
- [x] **Dynamic User Search**: Real-time on-demand Codeforces sync for any valid handle.
- [ ] **Phase 4**: Interactive AI Coach layer (staged progressive hints without spoilers + "Why did I fail?" submission debugging).
- [ ] **Phase 5**: Embeddings-based similar problem search, progress prediction, and adaptive contest simulations.
