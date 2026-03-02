# Agentic Data Assistant

An AI-powered data pipeline and natural language query engine built with CrewAI, FastAPI, and Streamlit. Upload any dataset and instantly get AI-generated schema documentation, data quality reports, and plain-English answers to your data questions.

# Features

- ETL Pipeline — Automatically ingests CSV, Excel, and JSON files, cleans data, and stores it in a local database
- Metadata Agent — AI agent that auto-documents your database schema, column types, and data profiles
- Data Quality Agent — AI agent that scores your data quality (0-100) and flags issues like nulls, duplicates, and inconsistencies
- Query Agent — Converts plain English questions into SQL, executes them, and returns human-readable answers
- Conversation Memory — Supports follow-up questions with context from previous queries
- REST API — Full FastAPI backend with 8 endpoints and Swagger documentation
- Interactive UI — Clean Streamlit frontend with live pipeline status


# Architecture
┌─────────────────┐         ┌──────────────────────────────────────┐
│   Streamlit UI  │ ──────► │           FastAPI Backend            │
│  localhost:8501 │         │          localhost:8000              │
└─────────────────┘         └──────────────────────────────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    │                     │                     │
             ┌──────▼──────┐    ┌─────────▼───────┐   ┌────────▼────────┐
             │ ETL Pipeline│    │ Metadata Agent  │   │  Query Agent    │
             │  (ingest.py)│    │   (CrewAI)      │   │   (CrewAI)      │
             └──────┬──────┘    └─────────┬───────┘   └────────┬────────┘
                    │                     │                     │
                    └─────────────────────▼─────────────────────┘
                                   ┌──────────┐
                                   │ SQLite DB│
                                   │warehouse │
                                   └──────────┘


# Project Structure
agentic-data-assistant/
│
├── api/
│   └── main.py                  # FastAPI backend — 8 REST endpoints
│
├── app/
│   └── streamlit_app.py         # Streamlit frontend — 3 pages
│
├── src/
│   ├── agents/
│   │   ├── metadata_agent.py    # Schema documentation agent
│   │   ├── data_quality_agent.py# Data quality scoring agent
│   │   └── query_agent.py       # Natural language query agent
│   │
│   ├── tasks/
│   │   ├── metadata_task.py     # Metadata agent task definition
│   │   └── query_tasks.py       # Query agent task definition
│   │
│   ├── models/
│   │   └── metadata_models.py   # Pydantic data models
│   │
│   ├── ingest.py                # ETL pipeline
│   └── config.py                # Project configuration
│
├── data/                        # Generated files (gitignored)
│   ├── uploads/                 # Uploaded datasets
│   ├── metadata_output.json     # Generated schema docs
│   └── quality_output.json      # Generated quality report
│
├── run_full_pipeline.py         # CLI — run full pipeline
├── run_metadata.py              # CLI — run metadata agent only
├── run_query.py                 # CLI — run query agent only
├── .env.example                 # Environment variable template
├── requirements.txt             # Python dependencies
└── README.md

# Getting Started
Prerequisites

Python 3.10+
Google Gemini API key (free at aistudio.google.com)

1. Clone the repository
bashgit clone https://github.com/yourusername/agentic-data-assistant.git
cd agentic-data-assistant
2. Create virtual environment
bashpython -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
3. Install dependencies
bashpip install -r requirements.txt
4. Set up environment variables
bash# Copy the example file
copy .env.example .env       # Windows
cp .env.example .env         # Mac/Linux

# Open .env and add your Gemini API key
GEMINI_API_KEY=your_key_here
5. Run the application
Terminal 1 — Start FastAPI backend:
bashuvicorn api.main:app --reload
Terminal 2 — Start Streamlit frontend:
bashstreamlit run app/streamlit_app.py
6. Open in browser
http://localhost:8501

# How to Use

Upload a CSV, Excel, or JSON file on the Pipeline page
Click Run Full Pipeline — this runs ETL → Metadata Agent → Quality Agent
Go to Data Explorer to view the auto-generated schema and quality report
Go to Query Chat and ask questions about your data in plain English

# Example Questions

"Who are the top 5 customers by total sales?"
"What is the total revenue by category?"
"Which region has the highest number of orders?"
"What was the best selling product last year?"
Follow-up: "Who bought it the most?" ← conversation memory works!


# API Endpoints
MethodEndpointDescriptionGET/Health checkPOST/uploadUpload file and run ETLPOST/run-metadataRun Metadata AgentGET/metadataGet saved metadataPOST/run-qualityRun Quality AgentGET/qualityGet quality reportPOST/queryAsk a natural language questionGET/statusGet pipeline status
Full Swagger documentation available at http://localhost:8000/docs

# Built With
TechnologyPurposeCrewAIMulti-agent AI frameworkFastAPIREST API backendStreamlitInteractive frontendGoogle GeminiLarge Language ModelSQLiteLocal databasePandasData processingPydanticData validation

# Supported File Formats

CSV — .csv
Excel — .xlsx, .xls
JSON — .json


# Known Limitations

Uses SQLite — not suitable for production scale databases
Gemini free tier has rate limits (5 requests/minute) — pipeline may be slow on first run
Designed for single-user local use

