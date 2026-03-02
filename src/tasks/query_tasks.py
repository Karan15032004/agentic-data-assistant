from crewai import Task

def create_query_task(agent, question: str, conversation_history: list = None):
    
    # Build conversation context string
    context_str = ""
    if conversation_history:
        context_str = "\n\nCONVERSATION HISTORY (for context only):\n"
        for i, entry in enumerate(conversation_history[-3:]):  # last 3 only
            context_str += f"Q{i+1}: {entry['question']}\n"
            context_str += f"A{i+1}: {entry['answer_summary']}\n\n"
        context_str += "Use this history to understand references like 'it', 'that product', 'same customer' etc.\n"

    return Task(
        description=f"""
        Answer the following natural language question using the database:

        QUESTION: {question}
        {context_str}

        You MUST follow this exact sequence:
        1. Analyze the question carefully.
           - If the question uses pronouns like "it", "that", "they", "same" —
             resolve them using the conversation history above.
        2. Identify the relevant table and columns from your schema knowledge.
        3. Write a correct SQL SELECT query.
        4. Execute it using the Execute SQL Query tool.
        5. Return the result as a structured JSON object.

        STRICT OUTPUT RULES:
        - Return ONLY a valid JSON object.
        - No markdown, no commentary, no explanation outside JSON.
        - You MUST include the original QUESTION exactly as provided in the "question" field.
        - The "question" field value MUST be: "{question}"
        - If query fails or question is unanswerable, return error JSON.
        """,
        agent=agent,
        expected_output="""
        {{
            "status": "success" | "error",
            "question": "original question here",
            "answer_summary": "one line answer",
            "sql_used": "executed SQL",
            "rows": int,
            "data": [{{"column1": value}}]
        }}

        Or error:
        {{
            "status": "error",
            "question": "original question",
            "message": "reason"
        }}
        """
    )