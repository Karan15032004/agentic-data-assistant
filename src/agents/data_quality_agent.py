
import os
import json
import re
import sqlite3
import pandas as pd
import numpy as np
from contextlib import contextmanager
from crewai import Agent
from crewai.tools import tool
from src.config import DB_PATH


# =========================================================
# SAFE DATABASE CONNECTION
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
# CORE DATA QUALITY ENGINE
# =========================================================

def _run_data_quality_checks(metadata_dict: dict) -> str:
    """
    Performs enterprise-grade data quality analysis.
    Returns structured JSON string.
    """

    tables = metadata_dict["database_summary"]["tables"]
    quality_report = []

    with get_connection() as conn:

        for table in tables:

            raw_name = table["table_name"]
            table_name = re.sub(r'\W+', '_', raw_name.lower()).strip('_')
            
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
                (table_name,)
            )
            if not cursor.fetchone():
                quality_report.append({
                    "table_name": table_name,
                    "error": f"Table '{table_name}' not found in database."
                })
                continue  # Skip instead of crashing-reliable agent
            df = pd.read_sql_query(
                f"SELECT * FROM {table_name} LIMIT 50000",  # Also added memory limit
                conn
            )
            row_count = len(df)
            column_issues = []

            # Identify primary keys from metadata
            primary_keys = [
                c["column_name"]
                for c in table["schema"]
                if c["is_primary_key"]
            ]

            # =================================================
            # COLUMN LEVEL CHECKS
            # =================================================

            for col in df.columns:

                missing = int(df[col].isnull().sum())
                duplicates = int(df[col].duplicated().sum())
                cardinality = int(df[col].nunique())

                col_issue = {
                    "column_name": col,
                    "missing_values": missing,
                    "duplicate_values": duplicates,
                    "outliers": 0,
                    "data_type_issue": False,
                    "cardinality": cardinality,
                    "duplicate_penalty_flag": False
                }

                # --------------------------------------------
                # Intelligent Duplicate Logic
                # --------------------------------------------

                if row_count > 0:

                    cardinality_ratio = cardinality / row_count
                    duplicate_ratio = duplicates / row_count

                    # Primary key strict enforcement
                    if col in primary_keys and duplicates > 0:
                        col_issue["duplicate_penalty_flag"] = True

                    # High-cardinality columns should not duplicate
                    elif cardinality_ratio > 0.8 and duplicate_ratio > 0.01:
                        col_issue["duplicate_penalty_flag"] = True

                # --------------------------------------------
                # Outlier Detection (IQR method)
                # Skip ID-like columns
                # --------------------------------------------

                col_lower = col.lower()

                skip_outlier = any(keyword in col_lower for keyword in [
                    "id", "postal", "zip", "code"
                ])

                if pd.api.types.is_numeric_dtype(df[col]) and not skip_outlier:

                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1

                    lower = Q1 - 1.5 * IQR
                    upper = Q3 + 1.5 * IQR

                    outliers = df[(df[col] < lower) | (df[col] > upper)]
                    col_issue["outliers"] = int(len(outliers))

                # --------------------------------------------
                # Data Type Consistency Check
                # --------------------------------------------

                expected_type = next(
                    (c["data_type"] for c in table["schema"]
                     if c["column_name"] == col),
                    None
                )

                if expected_type:
                    expected_upper = expected_type.upper()

                    if ("INT" in expected_upper or
                        "FLOAT" in expected_upper or
                        "REAL" in expected_upper):

                        if not pd.api.types.is_numeric_dtype(df[col]):
                            col_issue["data_type_issue"] = True

                column_issues.append(col_issue)

            # =================================================
            # TABLE LEVEL CHECKS
            # =================================================

            duplicate_rows = int(df.duplicated().sum())

            pk_violation = False
            if primary_keys:
                pk_violation = df.duplicated(subset=primary_keys).any()

            # =================================================
            # ENTERPRISE QUALITY SCORE (Percentage-Based)
            # =================================================

            score = 100

            for col in column_issues:

                if row_count > 0:

                    missing_ratio = col["missing_values"] / row_count
                    score -= missing_ratio * 20

                    if col["duplicate_penalty_flag"]:
                        duplicate_ratio = col["duplicate_values"] / row_count
                        score -= duplicate_ratio * 25

                    outlier_ratio = col["outliers"] / row_count
                    score -= outlier_ratio * 20

                if col["data_type_issue"]:
                    score -= 10

            if row_count > 0:
                duplicate_row_ratio = duplicate_rows / row_count
                score -= duplicate_row_ratio * 30

            if pk_violation:
                score -= 20

            score = max(0, round(score, 2))

            # =================================================
            # RISK CLASSIFICATION
            # =================================================

            if score >= 90:
                risk_level = "LOW"
            elif score >= 70:
                risk_level = "MEDIUM"
            else:
                risk_level = "HIGH"

            quality_report.append({
                "table_name": table_name,
                "row_count": row_count,
                "duplicate_rows": duplicate_rows,
                "primary_key_violation": pk_violation,
                "quality_score": score,
                "risk_level": risk_level,
                "columns": column_issues
            })

    return json.dumps({
        "data_quality_summary": {
            "total_tables_analyzed": len(quality_report),
            "tables": quality_report
        }
    })


# =========================================================
# CREWAI TOOL WRAPPER
# =========================================================

@tool("Run Data Quality Checks")
def run_data_quality_checks(metadata_json: str) -> str:
    """
    Performs complete data quality analysis using metadata JSON input.
    Returns structured JSON.
    """
    metadata_dict = json.loads(metadata_json)
    return _run_data_quality_checks(metadata_dict)


# =========================================================
# DATA QUALITY AGENT FACTORY
# =========================================================

def create_data_quality_agent(llm):

    return Agent(
        role="Senior Data Quality Auditor",
        goal="""
        Evaluate structured database quality using metadata.
        Perform column-level and table-level validation.
        Generate a deterministic machine-readable quality report.
        """,

        backstory="""
        You are an enterprise-grade Data Governance Auditor.

        You evaluate structured datasets for integrity, consistency,
        duplication, statistical anomalies, and structural compliance.

        Rules:
        - You NEVER modify database content.
        - You NEVER guess statistics.
        - You NEVER invent metrics.
        - You ONLY use tool outputs.
        - You ALWAYS return valid JSON.
        - You NEVER wrap output in markdown.
        - You NEVER provide natural language commentary.

        You compute reproducible quality scores using measurable defects.
        Your analysis must be deterministic and machine-consumable.
        """,

        tools=[run_data_quality_checks],
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
