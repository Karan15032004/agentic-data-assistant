import json
import pathlib
from crewai import Agent
from src.tools.sql_executor import execute_sql
from src.config import METADATA_OUTPUT_PATH


# =========================================================
# LOAD SCHEMA CONTEXT
# =========================================================

def _load_schema_context() -> str:
    path = pathlib.Path(METADATA_OUTPUT_PATH)

    if not path.exists():
        raise FileNotFoundError(
            f"metadata_output.json not found at {METADATA_OUTPUT_PATH}. "
            "Please run run_metadata.py first."
        )

    with open(path, "r") as f:
        metadata = json.load(f)

    tables = metadata["database_summary"]["tables"]
    schema_lines = []

    for table in tables:
        table_name = table["table_name"]
        schema_lines.append(f"TABLE: {table_name}")

        for col in table["schema"]:
            pk = " (PRIMARY KEY)" if col["is_primary_key"] else ""
            schema_lines.append(
                f"  - {col['column_name']}: {col['data_type']}{pk}"
            )

        schema_lines.append("")

    return "\n".join(schema_lines)


# =========================================================
# QUERY AGENT FACTORY
# =========================================================

def create_query_agent(llm=None):

    schema_context = _load_schema_context()

    return Agent(
        role="Senior SQL Data Analyst",

        goal="""
        Convert natural language questions into accurate SQL queries.
        Execute them using the Execute SQL Query tool.
        Return structured JSON output.
        """,

        backstory=f"""
        You are an expert SQL analyst working with a SQLite database.

        You have full knowledge of the database schema:

        {schema_context}

        STRICT RULES:
        - You ONLY use the Execute SQL Query tool.
        - You NEVER invent table or column names.
        - You ALWAYS use exact schema names.
        - You NEVER modify data.
        - You NEVER wrap SQL in markdown.
        - You ALWAYS return valid JSON.
        - You MUST return ONLY the JSON object.        
        - Do NOT include any explanation outside JSON. 
        - Do NOT include markdown of any kind.
        - After calling the tool, reuse the returned "data" exactly as provided.
        - Do not modify raw data values.        
        - Your final response format MUST be:
        {{
            "status": "success" | "error",
            "answer_summary": "...short explanation...",
            "rows": int,
            "data": [...]
        }}

        - If the question cannot be answered, return:

        {{
            "status": "error",
            "message": "Reason here"
        }}
        """,

        tools=[execute_sql],
        verbose=True,
        allow_delegation=False,
        llm=llm
    )