import os
import json
import pathlib
from dotenv import load_dotenv
from crewai import Crew, LLM
from src.agents.query_agent import create_query_agent
from src.tasks.query_tasks import create_query_task
from src.config import DATA_DIR


def run_query():

    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError(" GEMINI_API_KEY not found in .env file.")

    llm = LLM(
    provider="google",
    model="gemini-2.5-flash"
)

    query_agent = create_query_agent(llm=llm)

    #  Question Loop
    while True:
        question = input("\n💬 Ask your question (or type 'exit' to quit):\n> ").strip()

        if not question:
            print(" Question cannot be empty.")
            continue

        if question.lower() == "exit":
            print(" Goodbye!")
            break

        query_task = create_query_task(query_agent, question)

        crew = Crew(
            agents=[query_agent],
            tasks=[query_task],
            verbose=True
        )

        print("\n🚀 Running Query Agent...\n")
        crew_output = crew.kickoff()
        raw_output = crew_output.raw

        print("\n📦 Raw Agent Output:\n")
        print(raw_output)

        try:
            start = raw_output.index("{")
            end = raw_output.rindex("}") + 1
            cleaned = raw_output[start:end]
            result = json.loads(cleaned)
        except (ValueError, json.JSONDecodeError) as e:
            print("\n❌ JSON parsing failed.")
            print("Error:", e)
            print("Raw output was:\n", raw_output)
            continue  # Don't exit, try next question

        print("\n📊 Final Structured Result:\n")
        if result.get("status") == "success":
            print(f"  Question : {result.get('question')}")
            print(f"  Summary  : {result.get('answer_summary')}")
            print(f"  Rows     : {result.get('rows')}")
            print(f"  SQL Used : {result.get('sql_used')}")
            print("\n  Data:")
            print(json.dumps(result.get("data"), indent=2))
        else:
            print(f"❌ Error: {result.get('message')}")

        # Save Result
        output_path = pathlib.Path(DATA_DIR) / "query_output.json"
        output_path.write_text(json.dumps(result, indent=2))
        print(f"\n💾 Result saved to {output_path}")
        print("\n🎉 Query execution completed.\n")


if __name__ == "__main__":
    run_query()