from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ResearchStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    RESEARCHING = "researching"
    ANALYZING = "analyzing"
    SYNTHESIZING = "synthesizing"
    EDITING = "editing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"

class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500)
    depth: str = Field("standard", description="Research depth: quick, standard, deep")
    max_sources: int = Field(10, ge=1, le=50)

class SearchResult(BaseModel):
    title: str
    url: str
    content: str
    source: str
    relevance_score: float
    published_date: Optional[str] = None

class AnalysisResult(BaseModel):
    key_insights: List[str]
    patterns: List[str]
    contradictions: List[Dict[str, str]]
    credibility_score: float
    confidence_level: float

class ResearchReport(BaseModel):
    id: int
    topic: str
    summary: str
    sections: List[Dict[str, Any]]
    citations: List[Dict[str, str]]
    quality_score: float
    created_at: datetime
    status: ResearchStatus
    
class ResearchResponse(BaseModel):
    report_id: int
    status: ResearchStatus
    message: str
    data: Optional[Dict[str, Any]] = None