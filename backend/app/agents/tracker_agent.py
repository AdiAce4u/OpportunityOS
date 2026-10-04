from typing import Any
from app.agents.state import JobState
from app.agents.supervisor import log_event
from app.tools.tracking_tools import create_follow_up

def schedule_follow_up(state: JobState) -> JobState:
    """
    Tracker Agent Node:
    Monitors application status and schedules automated check-ins.
    """
    app_id = state.get("application_id")
    if app_id:
        # Schedule a polite follow-up after 5 days
        create_follow_up(app_id, event_type="REMINDER_EMAIL", days_later=5)
        log_event(
            state,
            "TrackerAgent",
            "Application tracked. Follow-up reminder scheduled for 5 days from today."
        )
    return state
