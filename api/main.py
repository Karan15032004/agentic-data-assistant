import os
import json
import shutil
import pathlib
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crewai import LLM

from src.ingest import IngestionEngine
from src.agents.metadata_agent import create_metadata_agent
from src.agents.data_quality_agent import _run_data_quality_checks
from src.agents.query_agent import create_query_agent
from src.tasks.metadata_task import create_metadata_task
from src.tasks.query_tasks import create_query_task
from src.config import UPLOAD_FOLDER, DATA_DIR, METADATA_OUTPUT_PATH
from crewai import Crew

import re

# =========================================================
# APP INITIALIZATION
# =========================================================

load_dotenv()

# Initializing FastAPI app
app = FastAPI(
    title="Agentic Data Assistant",
    description="AI-Powered Data Pipeline and Query Engine",
    version="1.0.0"
)

# Allow Streamlit to talk to FastAPI
# Without this, browser security blocks the connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

gemini_llm = LLM(
    provider="google",
    model="gemini-2.5-flash"
)


# =========================================================
# PYDANTIC MODELS (Request/Response Schemas)
# =========================================================
class ConversationEntry(BaseModel):
    question: str
    answer_summary: str

class QueryRequest(BaseModel):
    question: str
    conversation_history: list[ConversationEntry] = []  
class PipelineStatus(BaseModel):
    etl_done: bool = False
    metadata_done: bool = False
    quality_done: bool = False


# =========================================================
# PIPELINE STATE
# In-memory tracker — which steps have been completed
# =========================================================

pipeline_state = {
    "etl_done": False,
    "metadata_done": False,
    "quality_done": False,
    "table_name": None,
    "filename": None
}


# =========================================================
# ENDPOINT 1 — HEALTH CHECK
# =========================================================

@app.get("/")
def health_check():
    """
    Simple health check.
    Visit localhost:8000 to confirm API is running.
    """
    return {
        "status": "running",
        "message": "Agentic Data Assistant API is live",
        "version": "1.0.0"
    }


# =========================================================
# ENDPOINT 2 — UPLOAD FILE + RUN ETL
# =========================================================

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Accepts CSV/JSON/Excel file.
    Saves to uploads folder.
    Runs ETL pipeline.
    Returns ingestion report.
    """

    # 1. Validate file extension
    allowed = {".csv", ".json", ".xlsx", ".xls"}
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {allowed}"
        )

    # 2. Save file to uploads folder
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. Run ETL
    engine = IngestionEngine()
    report = engine.process_file(file.filename)

    if report["status"] != "success":
        raise HTTPException(
            status_code=500,
            detail=f"ETL Failed: {report.get('error')}"
        )

    # 4. Update pipeline state
    pipeline_state["etl_done"] = True
    pipeline_state["filename"] = file.filename
    pipeline_state["table_name"] = report["table_name"]

    return {
        "status": "success",
        "filename": file.filename,
        "table_name": report["table_name"],
        "rows_read": report["rows_read"],
        "duplicates_removed": report["duplicates_removed"],
        "rows_written": report["rows_written"],
        "columns_detected": report["columns_detected"],
        "column_names": report["column_names"]
    }


# =========================================================
# ENDPOINT 3 — RUN METADATA AGENT
# =========================================================

@app.post("/run-metadata")
def run_metadata():
    """
    Runs Metadata Agent on the ingested database.
    Saves metadata_output.json.
    Returns schema documentation.
    """

    # Guard — ETL must run first
    if not pipeline_state["etl_done"]:
        raise HTTPException(
            status_code=400,
            detail="ETL not completed. Please upload a file first."
        )

    # Run metadata agent
    metadata_agent = create_metadata_agent(llm=gemini_llm)
    metadata_task = create_metadata_task(agent=metadata_agent)

    crew = Crew(
        agents=[metadata_agent],
        tasks=[metadata_task],
        verbose=False
    )

    crew_output = crew.kickoff()
    raw = crew_output.raw

    # Extract JSON
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        metadata_dict = json.loads(raw[start:end])
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Metadata parsing failed: {e}"
        )

    # Save to disk
    pathlib.Path(METADATA_OUTPUT_PATH).write_text(
        json.dumps(metadata_dict, indent=2)
    )

    # Update state
    pipeline_state["metadata_done"] = True

    return metadata_dict


# =========================================================
# ENDPOINT 4 — GET METADATA (Read from disk)
# =========================================================

@app.get("/metadata")
def get_metadata():
    """
    Returns saved metadata JSON.
    Run /run-metadata first to generate it.
    """

    path = pathlib.Path(METADATA_OUTPUT_PATH)

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="Metadata not found. Run /run-metadata first."
        )

    return json.loads(path.read_text())


# =========================================================
# ENDPOINT 5 — RUN QUALITY AGENT
# =========================================================

@app.post("/run-quality")
def run_quality():
    """
    Runs Data Quality Agent using metadata.
    Returns quality report with scores.
    """

    # Guard — metadata must exist first
    if not pipeline_state["metadata_done"]:
        raise HTTPException(
            status_code=400,
            detail="Metadata not generated. Run /run-metadata first."
        )

    # Load metadata
    metadata_dict = json.loads(
        pathlib.Path(METADATA_OUTPUT_PATH).read_text()
    )

    # Run quality checks
    quality_json = _run_data_quality_checks(metadata_dict)
    quality_dict = json.loads(quality_json)

    # Save to disk
    output_path = pathlib.Path(DATA_DIR) / "quality_output.json"
    output_path.write_text(json.dumps(quality_dict, indent=2))

    # Update state
    pipeline_state["quality_done"] = True

    return quality_dict


# =========================================================
# ENDPOINT 6 — GET QUALITY REPORT (Read from disk)
# =========================================================

@app.get("/quality")
def get_quality():
    """
    Returns saved quality report JSON.
    Run /run-quality first to generate it.
    """

    path = pathlib.Path(DATA_DIR) / "quality_output.json"

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="Quality report not found. Run /run-quality first."
        )

    return json.loads(path.read_text())


# =========================================================
# ENDPOINT 7 — QUERY AGENT
# =========================================================

@app.post("/query")
def query(request: QueryRequest):
    """
    Accepts natural language question + conversation history.
    Runs Query Agent with context.
    Returns SQL + answer.
    """

    if not pipeline_state["quality_done"]:
        raise HTTPException(
            status_code=400,
            detail="Pipeline not complete. Run upload → metadata → quality first."
        )

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    # Convert conversation history to plain dicts
    history = [
        {"question": e.question, "answer_summary": e.answer_summary}
        for e in request.conversation_history
    ]

    # Run query agent WITH conversation history
    query_agent = create_query_agent(llm=gemini_llm)
    query_task = create_query_task(
        query_agent,
        request.question,
        conversation_history=history  # ← pass history here
    )

    crew = Crew(
        agents=[query_agent],
        tasks=[query_task],
        verbose=False
    )

    crew_output = crew.kickoff()
    raw_output = crew_output.raw

    try:
        start = raw_output.index("{")
        end = raw_output.rindex("}") + 1
        result = json.loads(raw_output[start:end])
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query parsing failed: {e}"
        )

    output_path = pathlib.Path(DATA_DIR) / "query_output.json"
    output_path.write_text(json.dumps(result, indent=2))

    sql = result.get("sql_used", "")
    first_word = sql.strip().split()[0].upper()

    if first_word != "SELECT":
        raise HTTPException(
            status_code=400,
            detail=f"Only SELECT queries are allowed. Got: {first_word}"
        )
    return result


# =========================================================
# ENDPOINT 8 — PIPELINE STATUS
# =========================================================

@app.get("/status")
def get_status():
    """
    Returns current pipeline state.
    Shows which steps have been completed.
    """
    return pipeline_state
