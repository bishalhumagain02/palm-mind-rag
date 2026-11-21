from pydantic import BaseModel

class BookingResponse(BaseModel):
    booking_id: str
    session_id: str
    name: str
    email: str
    interview_date: str
    interview_time: str
    timezone: str
    status: str
