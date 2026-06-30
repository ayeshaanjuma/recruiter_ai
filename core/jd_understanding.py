import os
import json
import re

def parse_jd(jd_text: str) -> dict:
    """
    Parse the raw JD text into a structured role fingerprint JSON.
    Uses Groq/Anthropic if available, else falls back to a deterministic rule-based parser.
    """
    if os.environ.get("GROQ_API_KEY"):
        return _parse_jd_llm(jd_text, provider="groq")
    elif os.environ.get("ANTHROPIC_API_KEY"):
        return _parse_jd_llm(jd_text, provider="anthropic")
    else:
        return _parse_jd_fallback(jd_text)

def _parse_jd_llm(jd_text: str, provider: str) -> dict:
    # Real LLM call would go here using the respective SDKs.
    # For now, we will just use the fallback logic to ensure it doesn't crash 
    # if keys are provided but SDKs fail or we just mock the LLM for simplicity.
    # A complete implementation would use `groq` or `anthropic` client.
    # The prompt would ask for a JSON response conforming to our schema.
    # We will implement a basic stub that calls the fallback for safety.
    try:
        if provider == "groq":
            import groq
            client = groq.Groq(api_key=os.environ.get("GROQ_API_KEY"))
            # In a real scenario, call client.chat.completions.create(...)
            # returning JSON. 
        elif provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            # In a real scenario, call client.messages.create(...)
        
        # We fall back to the deterministic parser if we don't have a real implementation
        # of the prompt extraction in this skeleton.
        return _parse_jd_fallback(jd_text)
    except Exception as e:
        print(f"LLM Parsing failed ({e}), using fallback.")
        return _parse_jd_fallback(jd_text)

def _parse_jd_fallback(jd_text: str) -> dict:
    """
    Deterministic rule-based fallback parser.
    """
    text_lower = jd_text.lower()
    
    # Extract years of experience
    min_years_experience = 0
    yoe_match = re.search(r'(\\d+)\\+?\\s*years?', text_lower)
    if yoe_match:
        min_years_experience = int(yoe_match.group(1))
        
    # Determine seniority
    seniority_band = "mid"
    if "senior" in text_lower or "lead" in text_lower or min_years_experience >= 4:
        seniority_band = "senior"
    elif "junior" in text_lower or min_years_experience <= 1:
        seniority_band = "junior"
        
    # Extract skills
    common_skills = ["python", "fastapi", "docker", "kubernetes", "aws", "gcp", "llm", "langchain", "llamaindex", "chroma", "pinecone", "weaviate", "machine learning", "react", "node.js", "java", "sql"]
    must_have_skills = []
    for skill in common_skills:
        if skill in text_lower:
            must_have_skills.append(skill.capitalize() if len(skill)>3 else skill.upper())
            
    # Implicit signals
    implicit_signals = []
    if "fast-moving" in text_lower or "startup" in text_lower or "ambiguity" in text_lower:
        implicit_signals.append("Comfort with ambiguity and fast-paced environments.")
    if "end-to-end" in text_lower or "ownership" in text_lower or "deploy" in text_lower:
        implicit_signals.append("Capable of full lifecycle deployment, not just prototyping.")
        
    # Role narrative
    role_narrative = (
        f"Looking for a {seniority_band} engineer with {min_years_experience}+ years of experience. "
        f"Needs strong expertise in {', '.join(must_have_skills[:3])}. "
        f"Ideal candidate takes full ownership and can scale ML systems in production."
    )
        
    return {
        "must_have_skills": must_have_skills,
        "nice_to_have_skills": ["Open Source Contributions"],
        "min_years_experience": min_years_experience,
        "seniority_band": seniority_band,
        "implicit_signals": implicit_signals,
        "role_narrative": role_narrative
    }
