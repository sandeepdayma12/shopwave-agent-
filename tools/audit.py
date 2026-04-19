from datetime import datetime

from .state import audit_logs


def log_audit(ticket_id: str, action: str, details: str) -> None:
    audit_logs.append(
        {
            "timestamp": datetime.now().isoformat(),
            "ticket_id": ticket_id,
            "action": action,
            "details": details,
        }
    )
