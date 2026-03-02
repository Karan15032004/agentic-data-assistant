# =========================================================
# sql_executor.py
# =========================================================

import sqlite3
import json
import re
import pandas as pd
from contextlib import contextmanager
from crewai.tools import tool
from src.config import DB_PATH


# =========================================================
# BLOCKED KEYWORDS (Safety Layer)
# =========================================================

BLOCKED_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
    "CREATE", "TRUNCATE", "REPLACE", "ATTACH", "DETACH"
]


# =========================================================
# SQL SAFETY VALIDATOR
# =========================================================

def _is_safe_query(sql: str) -> bool:#SELECT se start hai ya nahi query?
    """
    Blocks any non-SELECT operations.
    """
    # Remove string literals to avoid false positives
    cleaned = re.sub(r"'[^']*'", "", sql.upper())

    for keyword in BLOCKED_KEYWORDS:
        # Word boundary check to avoid partial matches
        if re.search(rf'\b{keyword}\b', cleaned):
            return False

    # Must start with SELECT
    stripped = cleaned.strip()
    if not stripped.startswith("SELECT"):
        return False

    return True


# =========================================================
# SAFE DATABASE CONNECTION (Read-Only)
# =========================================================

@contextmanager
def get_readonly_connection():
    """
    Opens SQLite connection in read-only URI mode.
    """
    uri = f"file:{DB_PATH}?mode=ro"#read only connection with the database
    conn = sqlite3.connect(uri, uri=True)
    try:
        yield conn
    finally:
        conn.close()


# =========================================================
# CORE EXECUTOR
# =========================================================

def _execute_sql(sql: str) -> str:
    """
    Validates and executes a SELECT query.
    Returns JSON string of results.
    """

    # 1. Clean input
    sql = sql.strip()

    # 2. Safety check
    if not _is_safe_query(sql):
        return json.dumps({
            "status": "blocked",
            "message": "Only SELECT queries are permitted.",
            "sql": sql
        })
    if "LIMIT" not in sql.upper():
        sql = sql.rstrip(";") + " LIMIT 100"
    # 3. Execute
    try:
        with get_readonly_connection() as conn:
            df = pd.read_sql_query(sql, conn)

        if df.empty:
            return json.dumps({
                "status": "success",
                "message": "Query executed but returned no results.",
                "sql": sql,
                "rows": 0,
                "data": []
            })

        return json.dumps({
            "status": "success",
            "sql": sql,
            "rows": len(df),
            "columns": list(df.columns),
            "data": df.to_dict(orient="records")
        })

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e),
            "sql": sql
        })


# =========================================================
# CREWAI TOOL
# =========================================================

@tool("Execute SQL Query")
def execute_sql(sql: str) -> str:
    """
    Executes a read-only SELECT SQL query against the warehouse database.
    Input must be a valid SQL SELECT statement.
    Returns results as JSON with columns and data.
    """
    return _execute_sql(sql)