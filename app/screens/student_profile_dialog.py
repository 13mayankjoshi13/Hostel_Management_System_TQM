"""Full student profile window, opened from the global search."""
import tkinter as tk
from tkinter import messagebox

from app.services import profile_service
from app.theme import COLORS, Card, ScrollFrame, chip, get_fonts_cached
from app.utils.validation import ValidationError


def _initials(name: str) -> str:
    parts = name.split()
    return "".join(p[0] for p in parts[:2]).upper() or "?"


def _rupees(paise: int) -> str:
    return f"₹{paise / 100:,.2f}".replace(".00", "")


def open_student_profile(parent, student_id: int):
    try:
        data = profile_service.student_profile(student_id)
    except ValidationError as e:
        messagebox.showerror("Student profile", str(e), parent=parent)
        return None
    fonts = get_fonts_cached()
    student, room = data["student"], data["room"]
    dlg = tk.Toplevel(parent)
    dlg.title(f"{student['name']} — Profile")
    dlg.configure(bg=COLORS["background"])
    dlg.geometry("640x700")
    dlg.minsize(520, 480)
    try:
        dlg.transient(parent.winfo_toplevel())
    except tk.TclError:
        pass

    head = tk.Frame(dlg, bg=COLORS["background"])
    head.pack(fill="x", padx=20, pady=(18, 8))
    avatar = tk.Canvas(head, width=56, height=56, bg=COLORS["background"], highlightthickness=0)
    avatar.create_oval(0, 0, 55, 55, fill=COLORS["accent"], outline="")
    avatar.create_text(28, 28, text=_initials(student["name"]), fill="#FFFFFF", font=fonts["section_title"])
    avatar.pack(side="left")
    names = tk.Frame(head, bg=COLORS["background"])
    names.pack(side="left", padx=14)
    tk.Label(names, text=student["name"], bg=COLORS["background"], fg=COLORS["text_primary"],
             font=fonts["section_title"]).pack(anchor="w")
    tk.Label(names, text=student["registration_number"], bg=COLORS["background"], fg=COLORS["text_secondary"],
             font=fonts["body"]).pack(anchor="w")
    unpaid = data["unpaid_paise"]
    chip(head, f"Dues {_rupees(unpaid)}" if unpaid else "No dues",
         COLORS["danger"] if unpaid else COLORS["success"],
         COLORS["danger_soft"] if unpaid else COLORS["success_soft"]).pack(side="right")

    scroll = ScrollFrame(dlg, bg=COLORS["background"])
    scroll.pack(fill="both", expand=True, padx=20, pady=(0, 6))
    body = scroll.inner

    def section(title, rows, empty=None):
        card = Card(body, fit=True)
        card.pack(fill="x", pady=(0, 10))
        tk.Label(card.body, text=title.upper(), bg=COLORS["surface"], fg=COLORS["text_tertiary"],
                 font=fonts["small_bold"]).pack(anchor="w", pady=(0, 6))
        if not rows:
            tk.Label(card.body, text=empty or "Nothing recorded.", bg=COLORS["surface"],
                     fg=COLORS["text_secondary"], font=fonts["body"]).pack(anchor="w")
        for label, value in rows:
            line = tk.Frame(card.body, bg=COLORS["surface"])
            line.pack(fill="x", pady=1)
            tk.Label(line, text=label, width=24, anchor="nw", bg=COLORS["surface"], fg=COLORS["text_secondary"],
                     font=fonts["label"]).pack(side="left")
            tk.Label(line, text=value, anchor="w", justify="left", wraplength=340, bg=COLORS["surface"],
                     fg=COLORS["text_primary"], font=fonts["body"]).pack(side="left", fill="x", expand=True)

    account = data["account"]
    section("Personal details", [
        ("Contact", student["contact_number"] or "—"), ("Gender", student["gender"] or "Not set"),
        ("Registered", (student["created_at"] or "")[:10] or "—"),
        ("Login account", f"{account['username']} ({account['status']})" if account else "No login account")])
    if room:
        rows = [("Room", f"{room['room_number']} · {room['room_type']}"),
                ("Hostel", f"{room['hostel_type'] or 'Unassigned'} · " +
                 ("Ground floor" if room["floor"] == 0 else f"Floor {room['floor']}")),
                ("Since", (room["allocated_at"] or "")[:10])]
        if data["warden"]:
            rows.append(("Warden", f"{data['warden']['name']} · {data['warden']['contact_number']}"))
        section("Room", rows)
    else:
        section("Room", [], "No active room allocation.")
    att = data["attendance"]
    section("Attendance (last 30 days)", [
        ("Present", str(att["Present"])), ("Absent", str(att["Absent"])), ("On leave", str(att["Leave"]))])
    section("Recent leaves", [(f"{l['from_date'][5:]} → {l['to_date'][5:]}", f"{l['status']} · {l['reason']}")
                              for l in data["leaves"]], "No leaves.")
    section("Recent complaints", [(c["category"], f"{c['status']} · {c['description']}")
                                  for c in data["complaints"]], "No complaints.")
    section("Fines", [(_rupees(f["amount_paise"]), f"{f['status']} · {f['reason']}") for f in data["fines"]],
            "No fines.")
    section("Recent visitors", [(v["in_time"][:16], f"{v['visitor_name']} ({v['relation']}) · {v['purpose']}")
                                for v in data["visitors"]], "No visitors.")
    scroll.update_scroll()
    tk.Button(dlg, text="Close", command=dlg.destroy, bg=COLORS["accent"], fg="#FFFFFF", bd=0, padx=18, pady=6,
              font=fonts["body_bold"], cursor="hand2").pack(pady=(0, 14))
    return dlg
