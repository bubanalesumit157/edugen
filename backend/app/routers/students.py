from fastapi import APIRouter
from .. import schemas
from services.ml_engine import grade_submission

router = APIRouter()

@router.post("/grade")
async def grade_student_submission(request: schemas.GradingRequest):
    """
    Called by StudentPortal.tsx
    Receives: { question, answer, rubric }
    Returns: { score, feedback }
    """
    result = await grade_submission(request.question, request.answer, request.rubric)
    return result