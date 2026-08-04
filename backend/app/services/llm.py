from groq import Groq
from app.core.config import settings
import json

client = Groq(api_key=settings.groq_api_key)

def call_groq(prompt: str, system: str = "You are a helpful assistant.") -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content

def extract_skills(text: str) -> list[str]:
    prompt = f"""Extract a flat JSON list of technical and professional skills mentioned in this text. Only return the JSON array, nothing else.

Text:
{text[:3000]}
"""
    result = call_groq(prompt)
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return []

def gap_analysis(resume_skills: list[str], jd_skills: list[str], jd_text: str) -> dict:
    resume_set = {s.lower().strip() for s in resume_skills}
    jd_set = {s.lower().strip() for s in jd_skills}
    missing = sorted(jd_set - resume_set)

    if not missing:
        return {"missing_skills": [], "suggestions": ["No major skill gaps detected based on extracted skills."]}

    prompt = f"""A candidate is missing these specific skills required by a job description: {missing}.
Given brief context on the role from this job description excerpt:
{jd_text[:800]}

Return ONLY valid JSON with this structure:
{{"suggestions": ["specific, actionable suggestion for closing gap 1", "specific suggestion for gap 2"]}}
Keep suggestions concrete and practical (e.g. course names, project ideas), 2-4 suggestions total.
"""
    result = call_groq(prompt)
    try:
        parsed = json.loads(result)
        return {"missing_skills": missing, "suggestions": parsed.get("suggestions", [])}
    except json.JSONDecodeError:
        return {"missing_skills": missing, "suggestions": []}

def bias_check(jd_text: str) -> dict:
    prompt = f"""Analyze this job description for potentially biased, exclusionary, or inflated language (gendered wording, unrealistic experience requirements, etc). Return ONLY valid JSON:
{{"flags": [{{"phrase": "...", "issue": "..."}}]}}

Job Description:
{jd_text[:1500]}
"""
    result = call_groq(prompt)
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {"flags": []}
