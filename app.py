from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from main import run_pipeline

app = FastAPI(title="Candidate Ranking API")

class RankRequest(BaseModel):
    jd_text: str
    candidates: List[dict]

@app.post("/rank")
def rank_candidates(request: RankRequest):
    try:
        if not request.jd_text or not request.candidates:
            raise HTTPException(status_code=400, detail="Missing jd_text or candidates")
            
        ranked = run_pipeline(request.jd_text, request.candidates)
        return {"ranked_candidates": ranked}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
