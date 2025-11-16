"""
Database Schemas for Avatar Interview SaaS

Each Pydantic model corresponds to a MongoDB collection.
Collection name is the lowercase of the class name.
"""
from typing import Optional, List
from pydantic import BaseModel, Field

class Candidate(BaseModel):
    """Candidate profile stored as 'candidate' collection"""
    name: str = Field(..., description="Full name of the candidate")
    email: str = Field(..., description="Unique email address")
    role: Optional[str] = Field(None, description="Target role or position")
    experience: Optional[str] = Field(None, description="Short experience summary")

class Interview(BaseModel):
    """Interview session stored as 'interview' collection"""
    title: str = Field(..., description="Interview title or job role")
    candidate_email: str = Field(..., description="Email of the candidate for this interview")
    status: str = Field("scheduled", description="scheduled|in_progress|completed")
    questions: List[str] = Field(default_factory=list, description="Ordered list of questions")

class Answer(BaseModel):
    """Answers stored as 'answer' collection (one doc per answer)"""
    interview_id: str = Field(..., description="Related interview id")
    question_index: int = Field(..., ge=0, description="Index of the question answered")
    transcript: str = Field(..., description="Text transcript of the candidate's response")
    sentiment: Optional[str] = Field(None, description="Optional sentiment/analysis summary")

# Example existing models remain usable by the database viewer
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = Field(None, ge=0, le=120)
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    category: str
    in_stock: bool = True
