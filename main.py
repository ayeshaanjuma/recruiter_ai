import json
import pandas as pd
import os
from core.jd_understanding import parse_jd
from core.candidate_profiler import profile_candidate
from core.scorer import compute_scores
from core.judge import re_rank_candidates

def extract_docx_text(filepath: str) -> str:
    import docx
    doc = docx.Document(filepath)
    return "\n".join([p.text for p in doc.paragraphs])

def stream_candidates(filepath: str):
    import json
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def run_pipeline(jd_text: str, candidates_stream) -> list:
    print("Stage 1: JD Understanding...")
    jd_fingerprint = parse_jd(jd_text)
    
    print("Stage 2: Candidate Profiling...")
    profiles = []
    # If list, iterate. If generator, also iterate.
    for c in candidates_stream:
        profiles.append(profile_candidate(c))
    
    print("Stage 3a: Semantic Recall and Rule Scoring...")
    shortlisted = compute_scores(jd_fingerprint, profiles)
    
    print("Stage 3b: LLM Judge Re-ranking...")
    final_ranked = re_rank_candidates(jd_fingerprint, shortlisted, top_n=15)
    
    return final_ranked

if __name__ == "__main__":
    jd_path = "data/raw/job_description.docx"
    candidates_path = "data/raw/candidates.jsonl"
    
    if not os.path.exists(jd_path) or not os.path.exists(candidates_path):
        print(f"Real data files not found in data/raw/. Looking for {jd_path} and {candidates_path}")
        exit(1)
        
    jd_text = extract_docx_text(jd_path)
    
    print(f"Loaded JD from docx. Streaming candidates...")
    
    candidates_stream = stream_candidates(candidates_path)
    
    ranked = run_pipeline(jd_text, candidates_stream)
    
    # Save JSON
    with open("data/ranked_candidates.json", "w") as f:
        json.dump(ranked, f, indent=2)
        
    # Save CSV
    csv_data = []
    for c in ranked:
        csv_data.append({
            "rank": c["rank_position"],
            "candidate_id": c["candidate_id"],
            "name": c["name"],
            "overall_score": c["overall_score"],
            "skills_match": c["sub_scores"]["skills_match"],
            "experience_fit": c["sub_scores"]["experience_fit"],
            "trajectory_signal": c["sub_scores"]["trajectory_signal"],
            "behavioral_activity": c["sub_scores"]["behavioral_activity"],
            "justification": c["justification"]
        })
        
    df = pd.DataFrame(csv_data)
    df.to_csv("data/ranked_candidates.csv", index=False)
    
    print("\\nPipeline complete! Top 3 candidates:")
    for c in ranked[:3]:
        print(f"{c['rank_position']}. {c['name']} (Score: {c['overall_score']}) - {c['justification']}")
