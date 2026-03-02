import os
import json
from dotenv import load_dotenv
from src.config import DATA_DIR
from crewai import Crew, LLM
from src.agents.metadata_agent import create_metadata_agent
from src.tasks.metadata_task import create_metadata_task
from src.models.metadata_models import DatabaseDocumentation


def run_metadata():

    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("❌ GEMINI_API_KEY not found in .env file.")


    gemini_llm = LLM(
    provider="google",
    model="gemini-2.5-flash"
)


    # Create Metadata Agent (Inject LLM)
    metadata_agent = create_metadata_agent(llm=gemini_llm)

    # Create Metadata Task
    metadata_task = create_metadata_task(agent=metadata_agent)

    crew = Crew(
        agents=[metadata_agent],
        tasks=[metadata_task],
        verbose=True
    )

    # Execute Crew
    crew_output = crew.kickoff()

    print("\n📦 Raw Agent Output:\n")
    print(crew_output.raw)

    result = crew_output.raw   
    import re

# Extract first JSON object from the output
    json_match = re.search(r"\{.*\}", result, re.DOTALL)

    if not json_match:
        print("❌ No JSON found in output.")
        print(result)
        return

    cleaned = json_match.group()

    try:
        result_dict = json.loads(cleaned)
    except Exception as e:
        print("\n❌ JSON parsing failed.")
        print("Error:", e)
        print("\nRaw Output:\n", result)
        return

    # Validate Using Pydantic
    try:
        validated = DatabaseDocumentation(**result_dict)
        print("\n✅ Metadata validation successful.")
        import pathlib
        output_path = pathlib.Path(DATA_DIR) / "metadata_output.json"
        output_path.write_text(json.dumps(result_dict, indent=2))
        print(f"💾 Metadata saved to {output_path}")
    except Exception as e:
        print("\n❌ Pydantic validation failed:")
        print(e)
        return

    print("\n🎉 Metadata pipeline completed successfully.")


if __name__ == "__main__":
    run_metadata()
