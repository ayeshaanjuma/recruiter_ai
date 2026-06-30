import streamlit as st
import json
import pandas as pd
import os
from main import run_pipeline, stream_candidates, extract_docx_text

st.set_page_config(page_title="Candidate Ranker", layout="wide")

st.title("AI-Powered Candidate Ranking System")

# --- Sidebar Configuration ---
st.sidebar.header("Configuration")

# JD Input
default_jd_text = ""
jd_path = "data/raw/job_description.docx"
if os.path.exists(jd_path):
    try:
        default_jd_text = extract_docx_text(jd_path)
    except Exception as e:
        default_jd_text = "Could not load default JD."

jd_input = st.sidebar.text_area("Job Description", value=default_jd_text, height=300)

# Dataset Input
dataset_path = st.sidebar.text_input("Dataset Path (.jsonl or .json)", value="data/raw/candidates.jsonl")

# Run Pipeline
if st.sidebar.button("Run Pipeline", type="primary"):
    if not jd_input.strip():
        st.sidebar.error("Job description cannot be empty.")
    elif not os.path.exists(dataset_path):
        st.sidebar.error(f"Dataset not found at {dataset_path}")
    else:
        with st.spinner(f"Running pipeline on {dataset_path}... This may take a few minutes for large datasets."):
            try:
                # Use standard json load if it's a list, otherwise stream
                if dataset_path.endswith('.jsonl'):
                    candidates_stream = stream_candidates(dataset_path)
                else:
                    with open(dataset_path, "r", encoding="utf-8") as f:
                        candidates_stream = json.load(f)
                        
                ranked = run_pipeline(jd_input, candidates_stream)
                
                # Save JSON
                with open("data/ranked_candidates.json", "w", encoding="utf-8") as f:
                    json.dump(ranked, f, indent=2)
                    
                st.sidebar.success("Pipeline complete! Results saved.")
            except Exception as e:
                st.sidebar.error(f"An error occurred: {str(e)}")

# --- Results Display ---
st.header("Top Candidates")

try:
    with open("data/ranked_candidates.json", "r", encoding="utf-8") as f:
        candidates = json.load(f)
        
    for i, c in enumerate(candidates):
        score = c.get('overall_score') or c.get('final_score', 'N/A')
        if isinstance(score, float):
            score = round(score, 2)
            
        st.subheader(f"Rank {i+1}: {c['name']} (Score: {score})")
        
        # Safely extract original data profile
        profile = c.get('original_data', {}).get('profile', {})
        role = profile.get('current_title', 'Unknown')
        yoe = profile.get('years_of_experience', 0)
        
        st.write(f"**Role:** {role} | **Experience:** {yoe} years")
        
        sub_scores = c.get("sub_scores", {})
        if sub_scores:
            st.write(f"**Skills:** {sub_scores.get('skills_match', 0)} | **Experience Fit:** {sub_scores.get('experience_fit', 0)} | **Trajectory:** {sub_scores.get('trajectory_signal', 0)} | **Behavioral:** {sub_scores.get('behavioral_activity', 0)}")
        else:
            st.write(f"**Career Trajectory Score:** {c.get('career_trajectory_score', 0)}")
            st.write(f"**Behavioral / Platform Score:** {c.get('behavioral_score', 0)}")
            
        st.write(f"**Skills:** {', '.join(c.get('normalized_skills', []))}")
        st.info(c.get('justification') or c.get('narrative', ''))
        st.divider()
except FileNotFoundError:
    st.info("No ranked candidates found. Please run the pipeline from the sidebar to process a dataset.")
