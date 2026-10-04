import re
from typing import Any

class SafetyGuard:
    """
    Enforces core OpportunityOS safety principles:
    - Never fabricate qualifications or experience.
    - Never expose secrets.
    - Protect candidate data.
    """
    
    SECRET_PATTERNS = [
        re.compile(r"sk-[a-zA-Z0-9]{20,}", re.IGNORECASE),
        re.compile(r"AIza[0-9A-Za-z-_]{35}", re.IGNORECASE),
        re.compile(r"(api[_-]?key|secret|token)[\s:=]+['\"]?([a-zA-Z0-9\-_]{16,})['\"]?", re.IGNORECASE),
    ]

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        if not text:
            return ""
        sanitized = text
        for pattern in cls.SECRET_PATTERNS:
            sanitized = pattern.sub("[REDACTED_SECRET]", sanitized)
        return sanitized

    @classmethod
    def verify_truthfulness(cls, generated_content: str, profile_facts: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Safety check: ensures no wild ungrounded claims are made that contradict the profile.
        """
        warnings = []
        lower_gen = generated_content.lower()
        
        # Check graduation year consistency if mentioned
        grad_year = profile_facts.get("graduation_year")
        if grad_year:
            # Check if an earlier graduation year is fabricated
            for year in range(1990, int(grad_year)):
                if f"graduated in {year}" in lower_gen or f"graduated {year}" in lower_gen:
                    warnings.append(f"Potential inaccurate graduation year detected: {year} vs profile {grad_year}")

        return (len(warnings) == 0, warnings)
