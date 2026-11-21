from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.booking import BookingResponse
from app.services.rag_service import chat
from app.repositories.booking_repository import get_booking

router = APIRouter()

@router.post("", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    try:
        answer, sources, booking_id = chat(payload.session_id, payload.question, db)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Chat service error: {exc}") from exc
    return ChatResponse(session_id=payload.session_id, answer=answer, source_documents=sources, booking_id=booking_id)

@router.get("/bookings/{booking_id}", response_model=BookingResponse)
def booking_detail(booking_id: str, db: Session = Depends(get_db)) -> BookingResponse:
    record = get_booking(db, booking_id)
    if not record:
        raise HTTPException(status_code=404, detail="Booking not found")
    return BookingResponse(booking_id=record.id, session_id=record.session_id, name=record.name, email=record.email, interview_date=record.interview_date, interview_time=record.interview_time, timezone=record.timezone, status=record.status)
