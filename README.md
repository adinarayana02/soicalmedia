# ◈ SENTINEL — Agentic AI Digital Wellbeing Platform

A production-ready FastAPI application for ethical social media behavior analysis using a 3-agent AI architecture.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python main.py
# OR
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Open in Browser
```
http://localhost:8000
```

### 4. Demo Login
- **Email:** `demo@sentinel.ai`
- **Password:** `demo1234`

---

## 🏗️ Architecture

```
SENTINEL
├── main.py                    # FastAPI app + lifespan (DB init + demo seed)
├── config.py                  # Settings (pydantic-settings)
├── requirements.txt
│
├── routes/
│   ├── auth.py                # GET / | POST /login | POST /register | GET /logout
│   ├── dashboard.py           # GET /dashboard
│   ├── insights.py            # GET /insights
│   ├── recommendations.py     # GET /recommendations
│   └── connect.py             # GET /connect | POST /connect/demo | POST /analyze
│
├── templates/                 # Jinja2 templates (dark futuristic UI)
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── insights.html
│   ├── recommendations.html
│   └── connect.html
│
├── static/
│   ├── css/style.css          # Full design system (CSS variables, responsive)
│   └── js/app.js              # Animated score ring, counters
│
├── ai_engine/                 # Core AI layer
│   ├── agent.py               # 3-Agent orchestrator (Observer → Evaluator → Advisor)
│   ├── text_model.py          # Lexicon-based NLP: sentiment, emotion, toxicity
│   ├── behavior_model.py      # Behavioral pattern analysis
│   ├── fusion.py              # Signal fusion layer
│   └── explainability.py      # Human-readable explanations
│
├── database/
│   ├── db.py                  # Async SQLAlchemy engine
│   └── models.py              # User, Activity, Analysis, BehaviorRecord
│
├── services/
│   ├── data_processing.py     # Preprocessing + demo data generator
│   └── risk_scoring.py        # Risk metadata (colors, icons, labels)
│
└── utils/
    └── helpers.py             # JWT auth, password hashing
```

---

## 🧠 AI System — 3 Agents

### Agent 1: Observer
- Runs NLP on all post text (sentiment, emotion, toxicity)
- Extracts behavioral features (late-night ratio, frequency, streaks)

### Agent 2: Evaluator
- Fuses text + behavior signals into a unified feature vector
- Computes **Digital Wellbeing Score** (0–100) using weighted rules:
  - Negative sentiment ratio → −25 pts max
  - Toxicity → −20 pts max
  - Late-night usage → −15 pts max
  - Negative streak → −15 pts max
  - High frequency → −10 pts max
  - Positive ratio → +10 pts bonus
- Assigns **Risk Category**: Safe / Moderate / High

### Agent 3: Advisor
- Generates human-readable explanations with evidence
- Produces personalized, non-judgmental recommendations
- Confidence scores per finding

---

## 🌐 Routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Login page |
| POST | `/login` | Authenticate user |
| POST | `/register` | Create account |
| GET | `/logout` | Clear session |
| GET | `/dashboard` | Main wellbeing dashboard |
| GET | `/insights` | Behavioral NLP findings |
| GET | `/recommendations` | Advisor suggestions |
| GET | `/connect` | Platform connection page |
| POST | `/connect/demo` | Load demo activity profile |
| POST | `/analyze` | JSON API: run AI analysis |
| GET | `/api/docs` | Swagger UI |

---

## 🔐 Privacy Design

- ✅ Only user-consented data processed
- ✅ Raw post content never stored — only derived signals
- ✅ No scraping, no private messages, no watch history
- ✅ Every AI decision includes human-readable explanation
- ✅ All insights are non-clinical
- ✅ Users can delete all data

---

## 🗄️ Database Schema

```sql
users        (user_id, name, email, hashed_password, created_at, consent_given)
activity     (post_id, user_id, text_content, platform, timestamp)
analysis     (id, post_id, sentiment, sentiment_score, emotion, toxicity)
behavior     (id, user_id, wellbeing_score, risk_category, explanation, confidence)
```

---

## 📊 Dashboard Features

- **Animated SVG score ring** (0–100 wellbeing score)
- **Risk level badge** (Safe / Moderate / High) — color coded
- **Sentiment trend chart** (Chart.js line chart)
- **Toxicity bar chart** (color-coded by severity)
- **4 key metrics**: Late-night %, Posts/day, Volatility, Dominant Emotion
- **Detected patterns** from Observer Agent
- **Explainable reasons** from Advisor Agent

---

## 🎨 UI Design

- Dark theme: `#080c14` background
- Typography: **Syne** (display) + **Space Mono** (data/labels)
- Accent: `#22d3ee` (cyan) + `#818cf8` (indigo)
- Responsive grid layout
- CSS-only animations + JS animated score counter
- Chart.js for data visualization

---

## ⚙️ Environment Variables

Create a `.env` file to override defaults:
```env
SECRET_KEY=your-very-secret-key-here
DATABASE_URL=sqlite+aiosqlite:///./sentinel.db
DEBUG=false
```

For production, use PostgreSQL:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/sentinel
```

---

## 🔧 Extending with Real APIs

Replace `generate_demo_activities()` in `services/data_processing.py` with real OAuth-connected calls:

```python
# Twitter API v2 example
import tweepy
client = tweepy.Client(bearer_token=BEARER_TOKEN)
tweets = client.get_users_tweets(user_id, max_results=100)
```

Connect via `/connect` page once OAuth flows are implemented.
