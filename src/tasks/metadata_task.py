from crewai import Task
from src.agents.metadata_agent import create_metadata_agent


def create_metadata_task(agent):
    return Task(
        description="""
        Perform full database schema documentation.

        You MUST follow this exact sequence:

        1. Use "List Tables" tool to retrieve all tables.
        2. For EACH table:
            a. Use "Get Table Schema"
            b. Use "Get Table Preview"
            c. Use "Profile Table Columns"
        3. Combine everything into ONE structured JSON report.
        4. Do NOT guess any schema details.
        5. Do NOT assume table names.
        6. Always rely on tools.
        """,
        agent=agent,
        expected_output="""
        A single structured JSON object with this format:

        {
            "database_summary": {
                "total_tables": int,
                "tables": [
                    {
                        "table_name": str,
                        "schema": [...],
                        "preview": [...],
                        "profile": [...]
                    }
                ]
            }
        }
        """
    )
