import os
import sqlite3
import pandas as pd
import json
import re
import time
from contextlib import contextmanager
from crewai import Agent
from crewai.tools import tool
from src.config import DB_PATH


# =========================================================
# GLOBAL CACHE (With Timestamp for Future Expiry Support)
# =========================================================

CACHE = {}

def get_cached(key):
    entry = CACHE.get(key)
    if not entry:
        return None
    return entry["data"]

def cache_result(key, value):
    CACHE[key] = {
        "data": value,
        "timestamp": time.time()
    }

def clear_cache():
    """Manually clear metadata cache (call after ingestion reruns)."""
    CACHE.clear()


# =========================================================
# INPUT SANITIZATION
# =========================================================

def sanitize_input(name: str) -> str:
    """
    Ensures table names match ingestion format.
    Converts to lowercase and replaces non-alphanumeric characters.
    """
    clean = name.lower()
    clean = re.sub(r'\W+', '_', clean)
    return clean.strip('_')


# =========================================================
# SAFE DATABASE CONNECTION (Context Managed)
# =========================================================

@contextmanager
def get_connection():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


# =========================================================
# INTERNAL HELPER: VALIDATE TABLE EXISTS
# =========================================================

def table_exists(conn, table_name: str) -> bool:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
        (table_name,)
    )
    return cursor.fetchone() is not None


# =========================================================
# TOOL 1: LIST TABLES
# =========================================================


def _list_tables_raw() -> str:
    """
    Returns all available table names in JSON.
    """

    cached = get_cached("list_tables")
    if cached:
        return json.dumps(cached)

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]

        result = {
            "status": "success",
            "tables": tables
        }

        cache_result("list_tables", result)
        return json.dumps(result)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })
    

@tool("List Tables")
def list_tables():
    """
    Returns all available table names in the database as JSON.
    """
    return _list_tables_raw()

# =========================================================
# TOOL 2: GET TABLE SCHEMA
# =========================================================

def _1_get_table_schema(table_name: str) -> str:
    """
    Returns structured schema information for a table.
    """

    clean_name = sanitize_input(table_name)
    cache_key = f"schema_{clean_name}"

    cached = get_cached(cache_key)
    if cached:
        return json.dumps(cached)

    try:
        with get_connection() as conn:

            if not table_exists(conn, clean_name):
                return json.dumps({
                    "status": "error",
                    "message": f"Table '{clean_name}' does not exist."
                })

            df = pd.read_sql_query(
                f"PRAGMA table_info({clean_name});",
                conn
            )

        columns = [
            {
                "column_name": row["name"],
                "data_type": row["type"],
                "is_primary_key": bool(row["pk"]),
                "not_null": bool(row["notnull"])
            }
            for _, row in df.iterrows()
        ]

        result = {
            "status": "success",
            "table": clean_name,
            "schema": columns
        }

        cache_result(cache_key, result)
        return json.dumps(result)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })

@tool("Get Table Schema")
def get_table_schema(table_name: str) -> str:
    """
    Returns structured schema information for a given table as JSON.
    """
    return _1_get_table_schema(table_name)

# =========================================================
# TOOL 3: TABLE PREVIEW
# =========================================================


def _get_table_preview1(table_name: str) -> str:
    """
    Returns first 3 rows for contextual understanding.
    No caching because data may change.
    """

    clean_name = sanitize_input(table_name)

    try:
        with get_connection() as conn:

            if not table_exists(conn, clean_name):
                return json.dumps({
                    "status": "error",
                    "message": f"Table '{clean_name}' does not exist."
                })

            df = pd.read_sql_query(
                f"SELECT * FROM {clean_name} LIMIT 3;",
                conn
            )

        if df.empty:
            return json.dumps({
                "status": "empty",
                "message": "Table exists but contains no rows."
            })

        return json.dumps({
            "status": "success",
            "table": clean_name,
            "preview": df.to_dict(orient="records")
        })

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })

@tool("Get Table Preview")
def get_table_preview(table_name:str)->str:
    """
      Returns first 3 rows for contextual understanding.
    No caching because data may change.
    """
    return _get_table_preview1(table_name)

    
# =========================================================
# TOOL 4: PROFILE TABLE
# =========================================================


def _profile_table1(table_name: str) -> str:
    """
    Profiles column statistics (null count, unique count, sample).
    """

    clean_name = sanitize_input(table_name)
    cache_key = f"profile_{clean_name}"

    cached = get_cached(cache_key)
    if cached:
        return json.dumps(cached)

    try:
        with get_connection() as conn:

            if not table_exists(conn, clean_name):
                return json.dumps({
                    "status": "error",
                    "message": f"Table '{clean_name}' does not exist."
                })

            df = pd.read_sql_query(
                f"SELECT * FROM {clean_name} LIMIT 5000;",
                conn
            )

        if df.empty:
            return json.dumps({
                "status": "error",
                "message": "Table is empty."
            })

        stats = []

        for col in df.columns:
            non_null_series = df[col].dropna()
            sample_val = (
                str(non_null_series.iloc[0])
                if not non_null_series.empty else None
            )

            stats.append({
                "column_name": col,
                "null_count": int(df[col].isnull().sum()),
                "unique_count": int(df[col].nunique()),
                "sample_value": sample_val
            })

        result = {
            "status": "success",
            "table": clean_name,
            "profile": stats
        }

        cache_result(cache_key, result)
        return json.dumps(result)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })

@tool("Profile Table Columns")
def profile_table(table_name:str)->str:
        """
    Profiles column statistics (null count, unique count, sample).
    """
        return _profile_table1(table_name)
# =========================================================
# METADATA AGENT DEFINITION
# =========================================================
def create_metadata_agent(llm=None):
    return Agent(
        role="Senior Data Architect",
        goal="""
        Fully map and document the database structure.
        Steps:
        1. List all tables.
        2. For each table, retrieve schema.
        3. Retrieve sample preview.
        4. Retrieve statistical profile.
        5. Compile structured dataset documentation.
        """,
        llm=llm,
        backstory=(
            "You are a highly disciplined and methodical database intelligence specialist. "
            "Your sole responsibility is to inspect structured databases and generate precise, "
            "machine-readable schema documentation. You operate in strict read-only mode and "
            "must never attempt to modify, delete, or alter any database content. "

            "You approach every table analytically: first discovering available tables, "
            "then examining column structures, data types, row counts, and basic statistics. "
            "You prioritize structured JSON outputs over narrative descriptions, ensuring "
            "that downstream agents can reliably consume your results. "

            "You are cautious, deterministic, and validation-focused. "
            "If an error occurs, you report it clearly instead of guessing. "
            "You do not assume schema details without using tools. "

            "You serve as the foundational intelligence layer for other agents, "
            "such as Data Quality and Query Agents. Your accuracy directly affects "
            "the reliability of the entire system."
        ),
        tools=[
            list_tables,
            get_table_schema,
            get_table_preview,
            profile_table
        ],
        verbose=True,
        allow_delegation=False
    )

 