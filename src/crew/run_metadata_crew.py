import os
import json
from dotenv import load_dotenv
from crewai import Crew, LLM
from src.tasks.metadata_task import create_metadata_task
from src.models.metadata_models import DatabaseDocumentation
from src.agents.metadata_agent import create_metadata_agent


def run_metadata_crew():

    #  Load API Key
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY not found in .env")

    #  Create Gemini LLM
    gemini_llm = LLM(
    provider="google",
    model="gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY")
)

    #  Create Agent with Injected LLM
    metadata_agent = create_metadata_agent(llm=gemini_llm)

    #  Create Task using that agent
    metadata_task = create_metadata_task(agent=metadata_agent)

    #  Create Crew
    crew = Crew(
        agents=[metadata_agent],
        tasks=[metadata_task],
        verbose=True
    )

    #  Run
    print("\n🚀 Running Metadata Crew...\n")
    result = crew.kickoff()

    print("\n📦 Raw Agent Output:\n")
    print(result)

    # Validate JSON
    try:
        result_dict = json.loads(result)
    except Exception:
        print("\n❌ Output is not valid JSON.")
        return

    # Validate via Pydantic
    try:
        validated = DatabaseDocumentation(**result_dict)
        print("\n✅ Metadata validation successful.")
    except Exception as e:
        print("\n❌ Pydantic Validation Failed:")
        print(e)


if __name__ == "__main__":
    run_metadata_crew()
