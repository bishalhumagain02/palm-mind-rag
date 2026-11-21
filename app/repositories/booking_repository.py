from sqlalchemy.orm import Session
from app.db.models import BookingRecord

def create_booking(db: Session, *, booking_id: str, session_id: str, name: str, email: str, interview_date: str, interview_time: str, timezone: str) -> BookingRecord:
    record = BookingRecord(id=booking_id, session_id=session_id, name=name, email=email, interview_date=interview_date, interview_time=interview_time, timezone=timezone, status="requested")
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def get_booking(db: Session, booking_id: str) -> BookingRecord | None:
    return db.get(BookingRecord, booking_id)
