import json
import os
import random

def generate_jd():
    return """
Title: Senior AI Software Engineer
Location: Remote
About Us: We are a fast-moving startup building the next generation of AI tools. 
You will own the end-to-end development of our machine learning pipeline.

Requirements:
- 4+ years of software engineering experience.
- Strong proficiency in Python and FastAPI.
- Experience with large language models (LLMs) and tools like LangChain, LlamaIndex, or raw API integrations (OpenAI, Anthropic).
- Experience deploying and scaling ML models in production (AWS/GCP, Docker, Kubernetes).
- Familiarity with vector databases (Chroma, Pinecone, Weaviate).
- You must be comfortable with ambiguity and taking full ownership of features.
- A strong track record of open source contributions is a huge plus.
"""

def generate_candidates(num_candidates=60):
    first_names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy", "Mallory", "Nina", "Oscar", "Peggy", "Trent", "Victor", "Walter", "Zoe"]
    last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris"]
    
    tech_stacks = [
        ["Python", "FastAPI", "Docker", "AWS", "PyTorch", "OpenAI API"],
        ["JavaScript", "React", "Node.js", "Express", "MongoDB"],
        ["Python", "Django", "PostgreSQL", "Redis", "Celery"],
        ["Java", "Spring Boot", "Kafka", "MySQL", "Kubernetes"],
        ["Python", "Flask", "ChromaDB", "LangChain", "GCP", "Kubernetes"],
        ["C++", "CUDA", "TensorFlow", "Linux"],
        ["Python", "FastAPI", "Anthropic API", "VectorDB", "AWS", "Docker"],
        ["Ruby", "Ruby on Rails", "PostgreSQL", "Heroku"],
        ["Go", "gRPC", "Kubernetes", "AWS", "Docker"],
    ]
    
    roles = ["Software Engineer", "Senior Software Engineer", "Backend Developer", "Machine Learning Engineer", "Data Scientist", "Full Stack Developer", "AI Engineer", "Lead Developer"]
    
    trajectories = ["progression", "flat", "non-linear"]
    
    candidates = []
    
    for i in range(num_candidates):
        is_strong = (i % 5 == 0) # Every 5th candidate is strong for the specific role
        
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        if is_strong:
            skills = random.choice([tech_stacks[0], tech_stacks[4], tech_stacks[6]])
            role = random.choice(["Senior Software Engineer", "Machine Learning Engineer", "AI Engineer"])
            yoe = random.randint(4, 10)
            github_commits = random.randint(500, 2000)
            oss_contributions = random.randint(10, 50)
            trajectory = "progression"
        else:
            skills = random.choice(tech_stacks)
            role = random.choice(roles)
            yoe = random.randint(1, 15)
            github_commits = random.randint(10, 300)
            oss_contributions = random.randint(0, 5)
            trajectory = random.choice(trajectories)
            
        candidate = {
            "id": f"CAND_{i+1:03d}",
            "name": name,
            "current_role": role,
            "years_of_experience": yoe,
            "skills": skills,
            "github_commits_last_year": github_commits,
            "open_source_contributions": oss_contributions,
            "career_trajectory": trajectory,
            "past_companies_count": random.randint(1, 5)
        }
        candidates.append(candidate)
        
    return candidates

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/raw", exist_ok=True)
    
    jd_text = generate_jd()
    with open("data/job_description.txt", "w") as f:
        f.write(jd_text.strip())
        
    candidates = generate_candidates(60)
    with open("data/candidates.json", "w") as f:
        json.dump(candidates, f, indent=2)
        
    print(f"Generated synthetic data in recruiter_ai/data/")
    print(f"- data/job_description.txt")
    print(f"- data/candidates.json ({len(candidates)} candidates)")
