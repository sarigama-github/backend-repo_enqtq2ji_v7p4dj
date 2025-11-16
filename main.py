import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents

app = FastAPI(title="Avatar Interview SaaS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateCandidate(BaseModel):
    name: str
    email: str
    role: Optional[str] = None
    experience: Optional[str] = None

class CreateInterview(BaseModel):
    title: str
    candidate_email: str
    questions: List[str]

class SubmitAnswer(BaseModel):
    interview_id: str
    question_index: int
    transcript: str
    sentiment: Optional[str] = None


@app.get("/")
def read_root():
    return {"message": "Avatar Interview SaaS Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response


@app.post("/api/candidates")
def create_candidate(payload: CreateCandidate):
    try:
        candidate_id = create_document("candidate", payload.model_dump())
        return {"id": candidate_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/candidates")
def list_candidates(email: Optional[str] = None):
    try:
        filt = {"email": email} if email else {}
        docs = get_documents("candidate", filt, limit=50)
        for d in docs:
            d["id"] = str(d.get("_id"))
            d.pop("_id", None)
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interviews")
def create_interview(payload: CreateInterview):
    try:
        # Ensure candidate exists (best-effort)
        candidate = get_documents("candidate", {"email": payload.candidate_email}, limit=1)
        if not candidate:
            _ = create_document("candidate", {"name": payload.candidate_email.split("@")[0].title(), "email": payload.candidate_email})
        interview_id = create_document("interview", payload.model_dump())
        return {"id": interview_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/interviews")
def list_interviews(candidate_email: Optional[str] = None):
    try:
        filt = {"candidate_email": candidate_email} if candidate_email else {}
        docs = get_documents("interview", filt, limit=50)
        for d in docs:
            d["id"] = str(d.get("_id"))
            d.pop("_id", None)
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/answers")
def submit_answer(payload: SubmitAnswer):
    try:
        # validate interview id format
        try:
            _ = ObjectId(payload.interview_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid interview_id")
        answer_id = create_document("answer", payload.model_dump())
        return {"id": answer_id, "status": "created"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
