import os

def re_rank_candidates(jd_fingerprint: dict, shortlisted_candidates: list, top_n: int = 15) -> list:
    """
    LLM judge re-rank: send top ~20-30 surviving candidates to LLM in one batched call.
    Fallback: rank by combined score, generate justification from templates.
    """
    candidates_to_rank = shortlisted_candidates[:30] # take up to 30
    
    if os.environ.get("GROQ_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"):
        ranked = _rank_llm(jd_fingerprint, candidates_to_rank)
    else:
        ranked = _rank_fallback(jd_fingerprint, candidates_to_rank)
        
    return ranked[:top_n]

def _rank_llm(jd_fingerprint: dict, candidates: list) -> list:
    # Stub for real LLM batched ranking.
    # In a real implementation, we would construct a prompt with the JD and candidate summaries
    # and ask the LLM to return a JSON array with candidate IDs, new ranks, and justifications.
    return _rank_fallback(jd_fingerprint, candidates)

def _rank_fallback(jd_fingerprint: dict, candidates: list) -> list:
    # Rank by the prelim_combined_score we calculated in scorer
    sorted_candidates = sorted(candidates, key=lambda x: x["prelim_combined_score"], reverse=True)
    
    for i, cand in enumerate(sorted_candidates):
        cand["overall_score"] = min(100, int(cand["prelim_combined_score"]))
        cand["rank_position"] = i + 1
        
        # Sub-scores
        sub_scores = {
            "skills_match": int(cand["rule_score"]),
            "experience_fit": int(cand["rule_score"]), # simplified, tied to rule score in fallback
            "trajectory_signal": int(cand["career_trajectory_score"]),
            "behavioral_activity": int(cand["behavioral_score"])
        }
        cand["sub_scores"] = sub_scores
        
        # Generate justification based on sub-scores
        justification = ""
        if sub_scores["skills_match"] > 80:
            justification += "Strong alignment with required skills and experience. "
        elif sub_scores["skills_match"] > 50:
            justification += "Moderate skill match with room for growth. "
        else:
            justification += "Missing some core requirements but has related background. "
            
        if sub_scores["behavioral_activity"] > 30:
            justification += "Excellent behavioral signals and demonstrated ownership."
        else:
            justification += "Solid, steady contributor."
            
        cand["justification"] = justification.strip()
        
    return sorted_candidates
