import streamlit as st
import json

st.title("AI-Powered Candidate Ranking System")

try:
    with open("data/ranked_candidates.json", "r") as f:
        candidates = json.load(f)
        
    for i, c in enumerate(candidates):
        score = c.get('final_score', 'N/A')
        if isinstance(score, float):
            score = round(score, 2)
            
        st.subheader(f"Rank {i+1}: {c['name']} (Score: {score})")
        
        # Safely extract original data profile
        profile = c.get('original_data', {}).get('profile', {})
        role = profile.get('current_title', 'Unknown')
        yoe = profile.get('years_of_experience', 0)
        
        st.write(f"**Role:** {role} | **Experience:** {yoe} years")
        st.write(f"**Career Trajectory Score:** {c.get('career_trajectory_score', 0)}")
        st.write(f"**Behavioral / Platform Score:** {c.get('behavioral_score', 0)}")
        st.write(f"**Skills:** {', '.join(c.get('normalized_skills', []))}")
        st.info(c.get('narrative', ''))
        st.divider()
except FileNotFoundError:
    st.error("No ranked candidates found. Please run `python main.py` first to process the dataset.")
