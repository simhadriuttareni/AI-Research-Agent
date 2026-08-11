from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from datetime import datetime
from app.models.database import get_db, ResearchReport
from sqlalchemy.orm import Session
import logging
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["research"])

class ResearchRequest(BaseModel):
    topic: str
    depth: str = "standard"
    max_sources: int = 10

@router.post("/research")
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        report = ResearchReport(
            topic=request.topic,
            status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        
        background_tasks.add_task(
            execute_research,
            report.id,
            request.topic,
            db
        )
        
        return {
            "report_id": report.id,
            "status": "pending",
            "message": "Research started successfully"
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/research/{report_id}")
async def get_research(report_id: int, db: Session = Depends(get_db)):
    try:
        report = db.query(ResearchReport).filter(ResearchReport.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {
            "id": report.id,
            "topic": report.topic,
            "status": report.status,
            "created_at": report.created_at.isoformat(),
            "updated_at": report.updated_at.isoformat(),
            "quality_score": report.quality_score,
            "report": report.final_report,
            "citations": report.citations,
            "error": report.error_message
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/research")
async def list_research(limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    try:
        reports = db.query(ResearchReport).offset(offset).limit(limit).all()
        return {
            "count": len(reports),
            "reports": [
                {
                    "id": r.id,
                    "topic": r.topic,
                    "status": r.status,
                    "created_at": r.created_at.isoformat(),
                    "quality_score": r.quality_score
                }
                for r in reports
            ]
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def execute_research(report_id: int, topic: str, db: Session):
    try:
        # Update status
        report = db.query(ResearchReport).filter(ResearchReport.id == report_id).first()
        if report:
            report.status = "researching"
            report.updated_at = datetime.utcnow()
            db.commit()
        
        # Import and run research
        from app.utils.research_engine import ResearchEngine
        
        engine = ResearchEngine()
        result = await engine.research(topic)
        
        # Update report
        report = db.query(ResearchReport).filter(ResearchReport.id == report_id).first()
        if report:
            report.status = "completed"
            report.final_report = result.get("report", "")
            report.citations = result.get("citations", [])
            report.quality_score = result.get("score", 0)
            report.updated_at = datetime.utcnow()
            db.commit()
            
    except Exception as e:
        logger.error(f"Research execution error: {str(e)}")
        report = db.query(ResearchReport).filter(ResearchReport.id == report_id).first()
        if report:
            report.status = "failed"
            report.error_message = str(e)
            report.updated_at = datetime.utcnow()
            db.commit()
