# AI-Powered Candidate Ranking System

This is a multi-stage, AI-driven candidate ranking system that takes a Job Description (JD) and a pool of candidates, and generates a ranked shortlist with explainable sub-scores and narratives. It uses a hybrid architecture involving LLMs, Semantic Search (Embeddings), and rule-based heuristics.

## Features
- **Stage 1: JD Understanding**: Extracts core skills, requirements, and implicit signals into a role fingerprint.
- **Stage 2: Candidate Profiling**: Generates normalized skills, a behavioral score (based on GitHub/OSS), trajectory analysis, and an LLM-powered narrative for each candidate.
- **Stage 3: Hybrid Scoring**: Semantic recall using `sentence-transformers` + rule-based scoring + LLM-based re-ranking to produce a highly accurate and explainable shortlist.
- **Robust Fallbacks**: Works deterministically out-of-the-box even without LLM API keys or internet access (uses regex parsers and TF-IDF if necessary).

## Setup & Requirements

1. **Install Python 3.11+**
2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

## Adding API Keys

The system uses local determinism by default. To unlock the full power of the LLM parser and judge, you can provide an API key. We support both Groq and Anthropic.
```bash
# On Linux / macOS
export GROQ_API_KEY="your-groq-key"
export ANTHROPIC_API_KEY="your-anthropic-key"

# On Windows (PowerShell)
$env:GROQ_API_KEY="your-groq-key"
$env:ANTHROPIC_API_KEY="your-anthropic-key"
```

## Swapping in Real Data

By default, we generate synthetic data for testing. When you receive the real data, you only need to modify `main.py` or create a new ingestion script that maps the real data columns to our internal schema:
```json
{
  "id": "String",
  "name": "String",
  "current_role": "String",
  "years_of_experience": "Int",
  "skills": ["List", "of", "Strings"],
  "github_commits_last_year": "Int",
  "open_source_contributions": "Int",
  "career_trajectory": "String (progression, flat, non-linear)",
  "past_companies_count": "Int"
}
```

## Running the System

### 1. Generate Synthetic Data
Run the following to populate `./data/` with `job_description.txt` and `candidates.json`:
```bash
python generate_synthetic_data.py
```

### 2. Run the Command-Line Pipeline
This will output `ranked_candidates.json` and `ranked_candidates.csv` in the `data/` directory.
```bash
python main.py
```

### 3. Run the FastAPI Backend
This will start the API at `http://localhost:8000`. You can POST JSON payload to `/rank`.
```bash
uvicorn app:app --reload
```
You can view the Swagger UI at `http://localhost:8000/docs`.

### 4. Run the Streamlit UI
This will launch an interactive web UI where you can paste the JD and view the ranked candidates.
```bash
streamlit run ui.py
```
