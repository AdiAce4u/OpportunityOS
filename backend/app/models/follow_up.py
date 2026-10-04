from datetime import datetime
from sqlalchemy import DateTime, Integer, JSON, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class FollowUpEvent(Base):
    __tablename__ = "follow_up_events"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(Integer, index=True)
    event_type: Mapped[str] = mapped_column(String(50))  # "STATUS_CHECK", "REMINDER_EMAIL", "INTERVIEW_INVITATION", "OFFER"
    scheduled_for: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(50), default="PENDING")  # "PENDING", "SENT", "RESOLVED"
    subject: Mapped[str] = mapped_column(String(255), default="")
    content: Mapped[str] = mapped_column(Text, default="")
    interview_details: Mapped[dict] = mapped_column(JSON, default=dict)
    prep_notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
