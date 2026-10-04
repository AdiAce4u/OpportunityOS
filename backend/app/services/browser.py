from app.core.config import settings

class BrowserApplicationService:
    """
    Safe adapter boundary.

    Default behavior is simulated submission. A real implementation must be
    provider-specific, permitted by the site, and human-approved.
    """
    def submit(self, job: dict, application_id: int) -> dict:
        if not settings.allow_browser_submit:
            return {
                "status": "SIMULATED_SUBMISSION",
                "application_id": f"DEMO-{application_id}",
            }
        raise NotImplementedError(
            "Add a permitted provider-specific browser adapter first."
        )
