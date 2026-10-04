from datetime import datetime
import json
import logging
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger("OpportunityOS")

class AgentActivityLogger:
    """Helper to collect audit trails and activity logs for UI inspection."""
    
    @staticmethod
    def format_log(stage: str, message: str, level: str = "INFO", metadata: dict[str, Any] | None = None) -> dict:
        now = datetime.now()
        timestamp = now.strftime("%H:%M:%S")
        return {
            "timestamp": timestamp,
            "iso_time": now.isoformat(),
            "stage": stage,
            "message": message,
            "level": level,
            "metadata": metadata or {},
        }
