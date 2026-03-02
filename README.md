# Agentic Data Assistant

An AI-powered data pipeline and natural language query engine built with **CrewAI**, **FastAPI**, and **Streamlit**. Upload any dataset and instantly get AI-generated schema documentation, data quality reports, and plain-English answers to your data questions.

---

## Features

- **ETL Pipeline** — Automatically ingests CSV, Excel, and JSON files, cleans data, and stores it in a local database
- **Metadata Agent** — AI agent that auto-documents your database schema, column types, and data profiles
- **Data Quality Agent** — AI agent that scores your data quality (0-100) and flags issues like nulls, duplicates, and inconsistencies
- **Query Agent** — Converts plain English questions into SQL, executes them, and returns human-readable answers
- **Conversation Memory** — Supports follow-up questions with context from previous queries
- **REST API** — Full FastAPI backend with 8 endpoints and Swagger documentation
- **Interactive UI** — Clean Streamlit frontend with live pipeline status

---

## How It Works

**Streamlit UI** → **FastAPI Backend** → **CrewAI Agents** → **SQLite Database**

1. User uploads a dataset through the Streamlit UI
2. FastAPI backend receives the file and runs the ETL pipeline
3. Metadata Agent (CrewAI) documents the schema automatically
4. Data Quality Agent (CrewAI) scores and flags data issues
5. Query Agent (CrewAI) answers plain English questions using SQL

---

## Project Structure

```
agentic-data-assistant/
├── api/
│   └── main.py                   # FastAPI backend — 8 REST endpoints
├── app/
│   └── streamlit_app.py          # Streamlit frontend — 3 pages
├── src/
│   ├── agents/
│   │   ├── metadata_agent.py     # Schema documentation agent
│   │   ├── data_quality_agent.py # Data quality scoring agent
│   │   └── query_agent.py        # Natural language query agent
│   ├── tasks/
│   │   ├── metadata_task.py      # Metadata agent task definition
│   │   └── query_tasks.py        # Query agent task definition
│   ├── models/
│   │   └── metadata_models.py    # Pydantic data models
│   ├── ingest.py                 # ETL pipeline
│   └── config.py                 # Project configuration
├── run_full_pipeline.py          # CLI — run full pipeline
├── run_metadata.py               # CLI — run metadata agent only
├── run_query.py                  # CLI — run query agent only
├── .env.example                  # Environment variable template
├── requirements.txt              # Python dependencies
└── README.md
```

---

##  Getting Started

### Prerequisites
- Python 3.10+
- Google Gemini API key — free at [aistudio.google.com](https://aistudio.google.com/apikey)

### 1. Clone the repository
```bash
git clone https://github.com/Karan15032004/agentic-data-assistant.git
cd agentic-data-assistant
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
copy .env.example .env
```
Open `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_key_here
```

### 5. Run the application

Terminal 1 — Start FastAPI backend:
```bash
uvicorn api.main:app --reload
```

Terminal 2 — Start Streamlit frontend:
```bash
streamlit run app/streamlit_app.py
```

### 6. Open in browser
```
http://localhost:8501
```

---

## How to Use

1. Go to **Pipeline** page and upload a CSV, Excel, or JSON file
2. Click **Run Full Pipeline** — runs ETL → Metadata Agent → Quality Agent
3. Go to **Data Explorer** to view the auto-generated schema and quality report
4. Go to **Query Chat** and ask questions about your data in plain English

### Example Questions
> *"Who are the top 5 customers by total sales?"*

> *"What is the total revenue by category?"*

> *"Which region has the highest number of orders?"*

> *"What was the best selling product last year?"*

> Follow-up: *"Who bought it the most?"* ← conversation memory works!

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/upload` | Upload file and run ETL |
| POST | `/run-metadata` | Run Metadata Agent |
| GET | `/metadata` | Get saved metadata |
| POST | `/run-quality` | Run Quality Agent |
| GET | `/quality` | Get quality report |
| POST | `/query` | Ask a natural language question |
| GET | `/status` | Get pipeline status |

Full Swagger docs available at `http://localhost:8000/docs`

---

## Built With

| Technology | Purpose |
|---|---|
| [CrewAI](https://crewai.com) | Multi-agent AI framework |
| [FastAPI](https://fastapi.tiangolo.com) | REST API backend |
| [Streamlit](https://streamlit.io) | Interactive frontend |
| [Google Gemini](https://aistudio.google.com) | Large Language Model |
| [SQLite](https://sqlite.org) | Local database |
| [Pandas](https://pandas.pydata.org) | Data processing |
| [Pydantic](https://docs.pydantic.dev) | Data validation |

---

## Supported File Formats

| Format | Extensions |
|--------|-----------|
| CSV | `.csv` |
| Excel | `.xlsx`, `.xls` |
| JSON | `.json` |

---

## Known Limitations

- Uses SQLite — not suitable for production scale
- Gemini free tier has rate limits (5 requests/minute)
- Designed for single-user local use

---
