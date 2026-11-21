import json
from datetime import date, datetime
from zoneinfo import ZoneInfo
from uuid import uuid4

from google import genai
from google.genai import types
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.vector_service import search_chunks
from app.services.memory_service import get_history, save_history
from app.repositories.booking_repository import create_booking


client = genai.Client(
    api_key=settings.gemini_api_key
)


SYSTEM_PROMPT = """You are a helpful assistant for a document
question-answering and interview-booking service.

Use the retrieved context to answer document questions.
If context does not contain the answer, say so plainly.
Do not invent facts.

If the user asks to schedule or book an interview,
collect:
- Full name
- Email
- Date (YYYY-MM-DD)
- Time (24-hour HH:MM)

Ask naturally for missing information.

Only mark booking_requested true when the user
clearly wants an interview booking.

Only return booking details the user provided.
Do not invent missing values.

For a complete request, confirm that it has been
recorded as a REQUEST, not a confirmed appointment.

Return JSON with these keys:
answer (string),
booking_requested (boolean),
name (string or null),
email (string or null),
interview_date (string or null),
interview_time (string or null).
"""


def _parse_json_response(content: str) -> dict:
    """Parse the model's JSON response."""

    try:
        return json.loads(content)

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "The language model returned invalid JSON"
        ) from exc


def chat(
    session_id: str,
    question: str,
    db: Session,
) -> tuple[str, list[dict[str, str]], str | None]:

    # 1. Retrieve conversation history from Redis
    history = get_history(session_id)

    # 2. Retrieve relevant document chunks from Qdrant
    sources = search_chunks(
        question,
        limit=5,
    )

    context = "\n\n".join(
        f"[Source {i + 1}: {source['filename']}]\n"
        f"{source['text']}"
        for i, source in enumerate(sources)
    )

    if not context:
        context = "[No documents uploaded yet]"

    # 3. Format conversation history
    history_text = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in history[-10:]
    )

    # 4. Build the prompt
    prompt = f"""
Retrieved document context:

{context}

Previous conversation:

{history_text or "[No previous conversation]"}

Current user question:

{question}
"""

    # 5. Generate response using Gemini
    response = client.models.generate_content(
        model=settings.gemini_chat_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )

    # 6. Parse the JSON response
    data = _parse_json_response(
        response.text or "{}"
    )

    answer = str(
        data.get(
            "answer",
            "Sorry, I could not generate a response.",
        )
    )

    booking_id: str | None = None

    # 7. Handle interview booking
    if data.get("booking_requested"):

        name = data.get("name")
        email = data.get("email")
        interview_date = data.get("interview_date")
        interview_time = data.get("interview_time")

        missing = [
            field
            for field, value in [
                ("name", name),
                ("email", email),
                ("date", interview_date),
                ("time", interview_time),
            ]
            if not value
        ]

        if not missing:

            try:
                date.fromisoformat(
                    str(interview_date)
                )

                datetime.strptime(
                    str(interview_time),
                    "%H:%M",
                )

                today_local = datetime.now(
                    ZoneInfo(settings.timezone)
                ).date()

                if (
                    date.fromisoformat(
                        str(interview_date)
                    ) < today_local
                ):
                    answer = (
                        "That date is in the past. "
                        "Please provide a future interview date."
                    )

                elif "@" not in str(email):
                    answer = (
                        "Please provide a valid email address "
                        "for the booking."
                    )

                else:
                    booking_id = str(uuid4())

                    create_booking(
                        db,
                        booking_id=booking_id,
                        session_id=session_id,
                        name=str(name),
                        email=str(email),
                        interview_date=str(interview_date),
                        interview_time=str(interview_time),
                        timezone=settings.timezone,
                    )

                    answer = (
                        "Your interview request has been saved. "
                        f"Reference ID: {booking_id}. "
                        f"Requested for {interview_date} at "
                        f"{interview_time} ({settings.timezone}). "
                        "This is a request, not yet a confirmed appointment."
                    )

            except ValueError:
                answer = (
                    "Please provide the date in YYYY-MM-DD "
                    "format and time in 24-hour HH:MM format."
                )

    # 8. Save conversation history to Redis
    history.extend(
        [
            {
                "role": "user",
                "content": question,
            },
            {
                "role": "assistant",
                "content": answer,
            },
        ]
    )

    save_history(
        session_id,
        history,
    )

    # 9. Return answer, sources, and booking ID
    return answer, sources, booking_id