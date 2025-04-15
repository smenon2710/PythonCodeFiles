import openai
import os
import re
from ast import literal_eval

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_search_queries(parsed):
    """
    Uses OpenAI GPT to generate intelligent job search queries from a resume.
    Handles various roles, skill types, and adds fallback logic.
    """
    designation = parsed.get("designation", "")
    skills = ", ".join(parsed.get("skills", []))
    experience = "\n".join(parsed.get("experience", []))

    resume_context = f"""
    Designation: {designation}
    Skills: {skills}
    Experience:
    {experience}
    """

    prompt = f"""
You are a job search assistant powered by AI. Your job is to extract the **most relevant job search queries** based on a user's resume. 
The user may be from any domain (tech, marketing, sales, healthcare, legal, etc.).

From the information below, infer **roles, tools, industries, or business functions** the person would search for on LinkedIn or Indeed.

Rules:
- Return **exactly 8** search queries (like "Salesforce Administrator", "Healthcare Business Analyst", "Legal Operations Specialist")
- Return it as a clean **Python list of strings** only, nothing else
- Remove duplicates, generic terms, or overly broad phrases

Resume:
{resume_context}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert AI career assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        output = response.choices[0].message.content.strip()

        # Extract Python list
        match = re.search(r"\[.*?\]", output, re.DOTALL)
        if match:
            query_list = literal_eval(match.group(0))
            if isinstance(query_list, list):
                return [q.strip() for q in query_list][:8]

    except Exception as e:
        print(f"🔴 GPT generation failed: {e}")

    # Fallback method (safe default)
    print("⚠️ Falling back to designation and skills.")
    fallback = parsed.get("skills", []) + ([designation] if designation else [])
    return list(set(fallback))[:8]
