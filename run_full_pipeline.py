import os
import json
import pathlib
import re
from dotenv import load_dotenv
from crewai import Crew, LLM

from src.ingest import IngestionEngine
from src.agents.metadata_agent import create_metadata_agent
from src.agents.data_quality_agent import create_data_quality_agent, _run_data_quality_checks
from src.agents.query_agent import create_query_agent
from src.tasks.metadata_task import create_metadata_task
from src.tasks.query_tasks import create_query_task
from src.config import DATA_DIR, METADATA_OUTPUT_PATH


# ETL
def step_etl(filename: str) -> dict:
    print("\n🔄 Step 1: Running ETL Pipeline...")
    engine = IngestionEngine()
    report = engine.process_file(filename)
    if report["status"] != "success":
        raise RuntimeError(f"ETL Failed: {report.get('error')}")
    print(f"✅ ETL Complete — {report['rows_written']} rows written to '{report['table_name']}'")
    return report


# METADATA AGENT
def step_metadata(llm) -> dict:
    print("\n🔄 Step 2: Running Metadata Agent...")

    metadata_agent = create_metadata_agent(llm=llm)
    metadata_task = create_metadata_task(agent=metadata_agent)

    crew = Crew(
        agents=[metadata_agent],
        tasks=[metadata_task],
        verbose=False 
    )

    crew_output = crew.kickoff()
    raw = crew_output.raw

    # Extract JSON
    json_match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not json_match:
        raise RuntimeError("Metadata Agent returned no valid JSON.")

    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        metadata_dict = json.loads(raw[start:end])
    except Exception as e:
        raise RuntimeError(f"Metadata JSON parsing failed: {e}")

    # Save to disk
    output_path = pathlib.Path(METADATA_OUTPUT_PATH)
    output_path.write_text(json.dumps(metadata_dict, indent=2))

    print(f"✅ Metadata Complete — schema saved to {METADATA_OUTPUT_PATH}")
    return metadata_dict


# DATA QUALITY AGENT
def step_quality(metadata_dict: dict) -> dict:
    print("\n🔄 Step 3: Running Data Quality Agent...")

    quality_json = _run_data_quality_checks(metadata_dict)
    quality_dict = json.loads(quality_json)

    # Print summary
    tables = quality_dict["data_quality_summary"]["tables"]
    for table in tables:
        print(f"  Table : {table['table_name']}")
        print(f"  Score : {table['quality_score']}")
        print(f"  Risk  : {table['risk_level']}")

    # Save to disk
    output_path = pathlib.Path(DATA_DIR) / "quality_output.json"
    output_path.write_text(json.dumps(quality_dict, indent=2))

    print(f"✅ Quality Check Complete — report saved to data/quality_output.json")
    return quality_dict


# QUERY AGENT
def step_query(llm) -> None:
    print("\n✅ Step 4: Query Agent Ready.")
    print("=" * 50)

    query_agent = create_query_agent(llm=llm)

    while True:
        question = input("\n💬 Ask your question (or type 'exit' to quit):\n> ").strip()

        if not question:
            print("❌ Question cannot be empty.")
            continue

        if question.lower() == "exit":
            print("👋 Goodbye!")
            break

        query_task = create_query_task(query_agent, question)

        crew = Crew(
            agents=[query_agent],
            tasks=[query_task],
            verbose=False
        )

        print("\n🚀 Running Query Agent...\n")
        crew_output = crew.kickoff()
        raw_output = crew_output.raw

        # Extract JSON
        try:
            start = raw_output.index("{")
            end = raw_output.rindex("}") + 1
            result = json.loads(raw_output[start:end])
        except Exception as e:
            print(f"\n❌ JSON parsing failed: {e}")
            continue

        # Display result
        print("\n Result:\n")
        if result.get("status") == "success":
            print(f"  Question : {result.get('question')}")
            print(f"  Summary  : {result.get('answer_summary')}")
            print(f"  Rows     : {result.get('rows')}")
            print(f"  SQL Used : {result.get('sql_used')}")
            print("\n  Data:")
            print(json.dumps(result.get("data"), indent=2))
        else:
            print(f"❌ {result.get('message')}")

        # Save result
        output_path = pathlib.Path(DATA_DIR) / "query_output.json"
        output_path.write_text(json.dumps(result, indent=2))
        print(f"\n💾 Saved to data/query_output.json")



# MAIN ORCHESTRATOR
def run_full_pipeline(filename: str):

    print("\n" + "=" * 50)
    print(" Agentic Data Assistant — Full Pipeline")
    print("=" * 50)

    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("❌ GEMINI_API_KEY not found in .env file.")

    llm =LLM(
    provider="google",
    model="gemini-2.5-flash"
)

    etl_report = step_etl(filename)
    metadata_dict = step_metadata(llm)
    quality_dict = step_quality(metadata_dict)
    step_query(llm)

# ENTRY POINT

if __name__ == "__main__":
    import sys
    filename = sys.argv[1] if len(sys.argv) > 1 else "train.csv"
    run_full_pipeline(filename)