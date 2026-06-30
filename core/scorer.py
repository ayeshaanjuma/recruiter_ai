import math

# Try to import sentence_transformers, if not available, fallback to sklearn TF-IDF
try:
    from sentence_transformers import SentenceTransformer, util
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        HAS_SKLEARN = True
    except ImportError:
        HAS_SKLEARN = False

def compute_scores(jd_fingerprint: dict, candidate_profiles: list) -> list:
    """
    Compute semantic score and rule-based score for candidates.
    Returns the candidates ranked by a combined heuristic, before LLM judge.
    """
    
    # 1. Semantic Recall
    jd_narrative = jd_fingerprint.get("role_narrative", "")
    candidate_narratives = [p.get("narrative", "") for p in candidate_profiles]
    
    semantic_scores = _compute_semantic_scores(jd_narrative, candidate_narratives)
    
    # 2. Rule-based Filter/Score
    for idx, profile in enumerate(candidate_profiles):
        profile["semantic_score"] = semantic_scores[idx]
        profile["rule_score"] = _compute_rule_score(jd_fingerprint, profile)
        
    # Sort by a preliminary combined score (semantic + rule + behavioral)
    def prelim_score(p):
        return (p["semantic_score"] * 0.4) + (p["rule_score"] * 0.4) + (p["behavioral_score"] * 0.2)
        
    for p in candidate_profiles:
        p["prelim_combined_score"] = prelim_score(p)
        
    # Sort descending
    sorted_candidates = sorted(candidate_profiles, key=lambda x: x["prelim_combined_score"], reverse=True)
    
    # Return top ~50%
    cutoff = max(1, len(sorted_candidates) // 2)
    return sorted_candidates[:cutoff]

def _compute_semantic_scores(jd_narrative: str, candidate_narratives: list) -> list:
    if not jd_narrative or not candidate_narratives:
        return [0] * len(candidate_narratives)
        
    if HAS_SENTENCE_TRANSFORMERS:
        try:
            model = SentenceTransformer('all-MiniLM-L6-v2')
            jd_emb = model.encode(jd_narrative)
            cand_embs = model.encode(candidate_narratives)
            scores = util.cos_sim(jd_emb, cand_embs)[0].tolist()
            return [max(0, min(100, s * 100)) for s in scores]
        except Exception as e:
            print(f"SentenceTransformer failed: {e}. Falling back to TF-IDF.")
            
    if HAS_SKLEARN:
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([jd_narrative] + candidate_narratives)
            jd_vec = tfidf_matrix[0:1]
            cand_vecs = tfidf_matrix[1:]
            scores = cosine_similarity(jd_vec, cand_vecs)[0].tolist()
            return [max(0, min(100, s * 100)) for s in scores]
        except Exception as e:
            print(f"TF-IDF failed: {e}. Returning dummy scores.")
            
    # Absolute fallback if neither library is working
    return [50.0] * len(candidate_narratives)

def _compute_rule_score(jd_fingerprint: dict, candidate_profile: dict) -> float:
    score = 0.0
    
    # Skills match
    must_have = [s.lower() for s in jd_fingerprint.get("must_have_skills", [])]
    cand_skills = candidate_profile.get("normalized_skills", [])
    if must_have:
        matched = set(must_have).intersection(set(cand_skills))
        skills_score = (len(matched) / len(must_have)) * 50
        score += skills_score
    else:
        score += 50
        
    # Experience match
    min_yoe = jd_fingerprint.get("min_years_experience", 0)
    cand_yoe = candidate_profile.get("original_data", {}).get("years_of_experience", 0)
    
    if cand_yoe >= min_yoe:
        score += 50
    elif cand_yoe >= min_yoe - 2:
        score += 25
        
    # Cap at 100
    return min(100.0, score)
