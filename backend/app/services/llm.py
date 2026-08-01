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

def gap_analysis(resume_text: str, jd_text: str) -> dict:
    prompt = f"""Compare this resume against this job description. Return ONLY valid JSON with this structure:
{{"missing_skills": ["skill1", "skill2"], "suggestions": ["specific suggestion 1", "specific suggestion 2"]}}

Resume:
{resume_text[:2000]}

Job Description:
{jd_text[:1500]}
"""
    result = call_groq(prompt)
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {"missing_skills": [], "suggestions": []}

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