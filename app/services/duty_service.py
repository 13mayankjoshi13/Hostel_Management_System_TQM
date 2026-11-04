"""Numbers for a specialist's own duty desk."""
from app.services import complaint_service, staff_log_service, gate_service, housekeeping_service, mess_service, visitor_service
from app.utils import session


def summary() -> list:
    """[(label, value, icon, colour name)] for the signed-in specialist."""
    role = session.get_role()
    if role in session.ROLE_CATEGORIES:
        rows = complaint_service.get_my_queue()
        items = [("Open", sum(1 for r in rows if r["status"] == "Open"), "chat", "orange"),
                 ("Assigned", sum(1 for r in rows if r["status"] == "Assigned"), "users", "info"),
                 ("Resolved", sum(1 for r in rows if r["status"] == "Resolved"), "clipboard", "success")]
        items.append(("Open log entries", staff_log_service.open_count(), "bug", "pink"))
        if role == "Mess Staff":
            items.append(("Waiting in queue", sum(mess_service.queue_counts().values()), "users", "info"))
            menu = mess_service.get_menu()
            items.append(("Meals planned today", f"{sum(1 for v in menu.values() if v)}/4", "calendar", "accent"))
        if role == "Housekeeping Staff":
            p = housekeeping_service.progress()
            items.append(("Cleaned today", f"{p['percent']}%", "key", "accent"))
        return items
    if role == "Security Staff":
        c = gate_service.counts()
        return [("Students out now", c["out_now"], "plane", "orange"),
                ("Late entries today", c["late_today"], "bug", "pink"),
                ("Visitors inside", visitor_service.inside_count(), "users", "info"),
                ("Open log entries", staff_log_service.open_count(), "clipboard", "accent")]
    return []
