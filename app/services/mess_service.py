"""Mess: the daily menu (set by mess staff) and student meal feedback."""
import sqlite3
from datetime import date, datetime

from app.database.db import get_connection
from app.utils import session
from app.utils.logging_service import log_audit, log_error
from app.utils.validation import ValidationError

MEALS = ("Breakfast", "Lunch", "Snacks", "Dinner")
LOW_RATING = 3.0


def _day(value, allow_future=True) -> str:
    try:
        parsed = datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError("Enter the date as YYYY-MM-DD.")
    if not allow_future and parsed > date.today():
        raise ValidationError("Feedback cannot be given for a future date.")
    return parsed.isoformat()


def set_menu(menu_date: str, meal: str, items: str) -> None:
    session.require_roles(session.MESS_MANAGE_ROLES, "set the menu")
    day = _day(menu_date)
    if meal not in MEALS:
        raise ValidationError("Choose Breakfast, Lunch, Snacks or Dinner.")
    items = " ".join((items or "").split())
    if len(items) < 3:
        raise ValidationError("Write what is being served (at least 3 characters).")
    if len(items) > 200:
        raise ValidationError("The menu must be 200 characters or fewer.")
    conn = get_connection()
    try:
        conn.execute("INSERT INTO meal_menu (menu_date, meal, items, updated_by) VALUES (?, ?, ?, ?) "
                     "ON CONFLICT(menu_date, meal) DO UPDATE SET items = excluded.items, updated_by = excluded.updated_by",
                     (day, meal, items, session.get_user()))
        conn.commit()
        log_audit("Mess", "SetMenu", f"{day} {meal}", "Success", "Menu saved.")
    except sqlite3.Error as exc:
        log_error("Mess", "DatabaseError", "High", "set_menu", status="Open", message_reference=str(exc))
        raise ValidationError("Could not save the menu due to a database error.")
    finally:
        conn.close()


def get_menu(menu_date: str = None) -> dict:
    """{meal: items or ''} for the day. Any signed-in role may read it."""
    day = _day(menu_date or date.today().isoformat())
    conn = get_connection()
    try:
        found = {r["meal"]: r["items"] for r in conn.execute("SELECT meal, items FROM meal_menu WHERE menu_date = ?", (day,))}
    finally:
        conn.close()
    return {meal: found.get(meal, "") for meal in MEALS}


def submit_feedback(menu_date: str, meal: str, rating: int, comment: str = "") -> None:
    session.require_roles(("Student",), "rate meals")
    day = _day(menu_date, allow_future=False)
    if meal not in MEALS:
        raise ValidationError("Choose a meal.")
    try:
        rating = int(rating)
    except (TypeError, ValueError):
        raise ValidationError("Rating must be a number from 1 to 5.")
    if not 1 <= rating <= 5:
        raise ValidationError("Rating must be from 1 to 5.")
    comment = " ".join((comment or "").split())
    if len(comment) > 200:
        raise ValidationError("The comment must be 200 characters or fewer.")
    if not get_menu(day)[meal]:
        raise ValidationError("No menu was set for that meal, so it cannot be rated.")
    conn = get_connection()
    try:
        conn.execute("INSERT INTO meal_feedback (student_id, menu_date, meal, rating, comment) VALUES (?, ?, ?, ?, ?) "
                     "ON CONFLICT(student_id, menu_date, meal) DO UPDATE SET rating = excluded.rating, comment = excluded.comment",
                     (session.get_student_id(), day, meal, rating, comment))
        conn.commit()
        log_audit("Mess", "Feedback", f"{day} {meal}", "Success", f"Rated {rating}.")
    except sqlite3.Error as exc:
        log_error("Mess", "DatabaseError", "High", "submit_feedback", status="Open", message_reference=str(exc))
        raise ValidationError("Could not save the rating due to a database error.")
    finally:
        conn.close()


def my_ratings(menu_date: str = None) -> dict:
    day = _day(menu_date or date.today().isoformat())
    session.require_roles(("Student",), "view own ratings")
    conn = get_connection()
    try:
        return {r["meal"]: r["rating"] for r in conn.execute(
            "SELECT meal, rating FROM meal_feedback WHERE student_id = ? AND menu_date = ?",
            (session.get_student_id(), day))}
    finally:
        conn.close()


def feedback_summary(days: int = 7) -> list:
    """Average rating per meal over the last `days` days; low averages are flagged."""
    session.require_roles(session.MESS_VIEW_ROLES, "view meal feedback")
    start = date.fromordinal(date.today().toordinal() - int(days) + 1).isoformat()
    conn = get_connection()
    try:
        rows = conn.execute("SELECT meal, COUNT(*) AS votes, AVG(rating) AS avg FROM meal_feedback "
                            "WHERE menu_date >= ? GROUP BY meal", (start,)).fetchall()
    finally:
        conn.close()
    by_meal = {r["meal"]: r for r in rows}
    out = []
    for meal in MEALS:
        row = by_meal.get(meal)
        avg = round(row["avg"], 2) if row else None
        out.append({"meal": meal, "votes": row["votes"] if row else 0, "average": avg,
                    "low": avg is not None and avg < LOW_RATING})
    return out


def recent_comments(limit: int = 8) -> list:
    session.require_roles(session.MESS_VIEW_ROLES, "view meal feedback")
    conn = get_connection()
    try:
        return [dict(r) for r in conn.execute(
            "SELECT menu_date, meal, rating, comment FROM meal_feedback WHERE comment != '' "
            "ORDER BY created_at DESC, rowid DESC LIMIT ?", (int(limit),))]
    finally:
        conn.close()


def join_queue(meal: str) -> None:
    session.require_roles(("Student",), "join the mess queue")
    if meal not in MEALS:
        raise ValidationError("Choose a meal.")
    day = date.today().isoformat()
    if not get_menu(day)[meal]:
        raise ValidationError("No menu is set for that meal, so there is no queue.")
    conn = get_connection()
    try:
        cur = conn.execute("INSERT OR IGNORE INTO meal_queue (student_id, queue_date, meal) VALUES (?, ?, ?)",
                           (session.get_student_id(), day, meal))
        if cur.rowcount == 0:
            raise ValidationError("You have already joined this queue.")
        conn.commit()
        log_audit("Mess", "JoinQueue", f"{day} {meal}", "Success", "Joined the queue.")
    except sqlite3.Error as exc:
        log_error("Mess", "DatabaseError", "High", "join_queue", status="Open", message_reference=str(exc))
        raise ValidationError("Could not join the queue due to a database error.")
    finally:
        conn.close()


def leave_queue(meal: str) -> None:
    session.require_roles(("Student",), "leave the mess queue")
    conn = get_connection()
    try:
        conn.execute("DELETE FROM meal_queue WHERE student_id = ? AND queue_date = ? AND meal = ? AND status = 'Waiting'",
                     (session.get_student_id(), date.today().isoformat(), meal))
        conn.commit()
        log_audit("Mess", "LeaveQueue", meal, "Success", "Left the queue.")
    except sqlite3.Error as exc:
        log_error("Mess", "DatabaseError", "High", "leave_queue", status="Open", message_reference=str(exc))
        raise ValidationError("Could not leave the queue due to a database error.")
    finally:
        conn.close()


def my_queue_status(menu_date: str = None) -> dict:
    """{meal: {'status', 'position'}} for the signed-in student; position counts waiting students ahead + 1."""
    session.require_roles(("Student",), "view own queue")
    day = menu_date or date.today().isoformat()
    conn = get_connection()
    try:
        out = {}
        for r in conn.execute("SELECT queue_id, meal, status FROM meal_queue WHERE student_id = ? AND queue_date = ?",
                              (session.get_student_id(), day)).fetchall():
            pos = None
            if r["status"] == "Waiting":
                pos = conn.execute("SELECT COUNT(*) FROM meal_queue WHERE queue_date = ? AND meal = ? "
                                   "AND status = 'Waiting' AND queue_id <= ?", (day, r["meal"], r["queue_id"])).fetchone()[0]
            out[r["meal"]] = {"status": r["status"], "position": pos}
        return out
    finally:
        conn.close()


def queue_counts(menu_date: str = None) -> dict:
    day = menu_date or date.today().isoformat()
    conn = get_connection()
    try:
        found = {r["meal"]: r["n"] for r in conn.execute(
            "SELECT meal, COUNT(*) AS n FROM meal_queue WHERE queue_date = ? AND status = 'Waiting' GROUP BY meal", (day,))}
    finally:
        conn.close()
    return {meal: found.get(meal, 0) for meal in MEALS}


def get_queue() -> list:
    """Waiting students for today, in join order."""
    session.require_roles(session.MESS_VIEW_ROLES, "view the mess queue")
    conn = get_connection()
    try:
        return [dict(r) for r in conn.execute(
            "SELECT q.queue_id, q.meal, q.joined_at, s.name AS student_name, r.room_number FROM meal_queue q "
            "JOIN students s ON s.student_id = q.student_id "
            "LEFT JOIN allocations al ON al.student_id = s.student_id AND al.status = 'Active' "
            "LEFT JOIN rooms r ON r.room_id = al.room_id WHERE q.queue_date = ? AND q.status = 'Waiting' "
            "ORDER BY q.queue_id", (date.today().isoformat(),))]
    finally:
        conn.close()


def serve(queue_id) -> None:
    session.require_roles(session.MESS_MANAGE_ROLES, "serve students")
    conn = get_connection()
    try:
        conn.execute("UPDATE meal_queue SET status = 'Served' WHERE queue_id = ?", (int(queue_id),))
        conn.commit()
        log_audit("Mess", "Serve", str(queue_id), "Success", "Marked served.")
    except sqlite3.Error as exc:
        log_error("Mess", "DatabaseError", "High", "serve", status="Open", message_reference=str(exc))
        raise ValidationError("Could not update the queue due to a database error.")
    finally:
        conn.close()


def clear_queue(meal: str = None) -> None:
    session.require_roles(session.MESS_MANAGE_ROLES, "clear the queue")
    conn = get_connection()
    try:
        sql, args = "DELETE FROM meal_queue WHERE queue_date = ? AND status = 'Waiting'", [date.today().isoformat()]
        if meal:
            sql += " AND meal = ?"
            args.append(meal)
        conn.execute(sql, args)
        conn.commit()
        log_audit("Mess", "ClearQueue", meal or "All", "Success", "Queue cleared.")
    except sqlite3.Error as exc:
        log_error("Mess", "DatabaseError", "High", "clear_queue", status="Open", message_reference=str(exc))
        raise ValidationError("Could not clear the queue due to a database error.")
    finally:
        conn.close()
