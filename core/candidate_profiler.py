import os

def profile_candidate(candidate_data: dict) -> dict:
    """
    Extract signals per candidate:
    - Normalized skills
    - Career trajectory signal
    - Behavioral score
    - Candidate narrative
    """
    # Normalize skills
    # Real schema: "skills": [{"name": "Python", ...}, ...]
    raw_skills = candidate_data.get("skills", [])
    if raw_skills and isinstance(raw_skills[0], dict):
        normalized_skills = [s.get("name", "").strip().lower() for s in raw_skills if s.get("name")]
    else:
        # Fallback for synthetic schema
        normalized_skills = [s.strip().lower() for s in raw_skills]
    
    # Career trajectory
    trajectory = candidate_data.get("career_trajectory", "flat")
    if "career_history" in candidate_data:
        # Simplistic heuristic: if they have multiple roles, we give them progression score
        if len(candidate_data["career_history"]) > 1:
            trajectory = "progression"
    
    if trajectory == "progression":
        traj_score = 100
    elif trajectory == "non-linear":
        traj_score = 60
    else:
        traj_score = 30
        
    # Behavioral score (e.g. GitHub + OSS activity)
    if "redrob_signals" in candidate_data:
        gh_score = candidate_data["redrob_signals"].get("github_activity_score", 0)
        gh_score = max(0, gh_score) # -1 means no github
        # Map out of 100
        behavioral_score = int(gh_score)
    else:
        gh_commits = candidate_data.get("github_commits_last_year", 0)
        oss = candidate_data.get("open_source_contributions", 0)
        
        # Simple heuristic to bound score between 0 and 100
        gh_score = min(gh_commits / 1000.0 * 50, 50)  # Max 50 points from commits
        oss_score = min(oss / 20.0 * 50, 50)          # Max 50 points from OSS
        behavioral_score = int(gh_score + oss_score)
    
    # Narrative generation
    if os.environ.get("GROQ_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"):
        narrative = _generate_narrative_llm(candidate_data)
    else:
        narrative = _generate_narrative_fallback(candidate_data)
        
    # Adapt fields for output
    candidate_id = candidate_data.get("candidate_id") or candidate_data.get("id")
    profile = candidate_data.get("profile", {})
    name = profile.get("anonymized_name") or candidate_data.get("name")
    
    return {
        "candidate_id": candidate_id,
        "name": name,
        "original_data": candidate_data,
        "normalized_skills": normalized_skills,
        "career_trajectory_score": traj_score,
        "behavioral_score": behavioral_score,
        "narrative": narrative
    }

def _generate_narrative_llm(candidate_data: dict) -> str:
    # Stub for real LLM call
    return _generate_narrative_fallback(candidate_data)

def _generate_narrative_fallback(candidate_data: dict) -> str:
    """
    Deterministic 2-3 sentence narrative highlighting what they did and depth of ownership.
    """
    profile = candidate_data.get("profile", {})
    name = profile.get("anonymized_name") or candidate_data.get("name", "Candidate")
    role = profile.get("current_title") or candidate_data.get("current_role", "Engineer")
    yoe = profile.get("years_of_experience") or candidate_data.get("years_of_experience", 0)
    
    if "redrob_signals" in candidate_data:
        gh_commits = max(0, candidate_data["redrob_signals"].get("github_activity_score", 0)) * 10 # scale for narrative
    else:
        gh_commits = candidate_data.get("github_commits_last_year", 0)
    
    narrative = f"{name} is a {role} with {yoe} years of experience. "
    if gh_commits > 500:
        narrative += f"They have a strong track record of hands-on delivery and deep technical ownership, evidenced by high coding activity. "
    else:
        narrative += f"They have steadily contributed to engineering teams with solid, consistent output. "
        
    traj = candidate_data.get("career_trajectory", "flat")
    if traj == "progression":
        narrative += "Their career shows clear upward progression and increasing responsibility."
        
    return narrative.strip()
