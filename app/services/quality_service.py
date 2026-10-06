"""
Quality Monitoring / SQC data-prep service.

Pure read-only analysis over real data already produced by bug_service
and complaint_service — this module never writes anything and never
fabricates a number. If there are no bugs yet, every function below
returns an empty/zero result rather than inventing sample data; the UI
is responsible for showing an honest "not enough data yet" state.

Two SQC tools are served:
  - Pareto: bug counts by category, sorted descending, with running
    cumulative percentage (the classic 80/20 defect-concentration view).
  - Fishbone (Cause-and-Effect): each bug's Category is mapped onto the
    six standard fishbone branches used in the course material (People,
    Process, Software/Code, Database, Infrastructure, Measurement) so
    real defect titles show up as causes under the right branch.
"""
from app.services import bug_service

# Maps a bug's recorded Category (what the person logging the bug picks)
# onto the six fishbone branches specified in the course material. This
# mapping is a judgment call, documented here so it's easy to revisit:
# Functional bugs are usually business-logic/process mistakes; UI/UX
# issues are about how people experience the system; Validation and
# Security are code-level defects; Performance is usually an
# infrastructure concern; Data Integrity points at the database;
# anything uncategorized falls under Measurement (i.e. our own defect
# classification needs improving).
CATEGORY_TO_FISHBONE = {
    "Functional": "Process",
    "UI/UX": "People",
    "Validation": "Software/Code",
    "Security": "Software/Code",
    "Performance": "Infrastructure",
    "Data Integrity": "Database",
    "Other": "Measurement",
}

FISHBONE_BRANCHES = ["People", "Process", "Software/Code", "Database", "Infrastructure", "Measurement"]


def get_quality_summary() -> dict:
    """Headline counts for the Quality Monitoring KPI strip."""
    bugs = bug_service.get_all_bugs()
    total = len(bugs)
    by_status = {}
    for b in bugs:
        by_status[b["status"]] = by_status.get(b["status"], 0) + 1
    critical_high_open = sum(
        1 for b in bugs
        if b["status"] in ("Open", "In Progress") and b["severity"] in ("Critical", "High")
    )
    fixed_or_closed = by_status.get("Fixed", 0) + by_status.get("Closed", 0)
    fix_rate_pct = round(fixed_or_closed / total * 100) if total > 0 else 0

    return {
        "total": total,
        "open": by_status.get("Open", 0),
        "in_progress": by_status.get("In Progress", 0),
        "fixed": by_status.get("Fixed", 0),
        "closed": by_status.get("Closed", 0),
        "critical_high_open": critical_high_open,
        "fix_rate_pct": fix_rate_pct,
    }


def get_pareto_data() -> list:
    """
    Returns [(category, count, cumulative_pct), ...] sorted by count
    descending — the standard Pareto ordering. Empty list if no bugs
    have been logged yet.
    """
    bugs = bug_service.get_all_bugs()
    if not bugs:
        return []

    counts = {}
    for b in bugs:
        counts[b["category"]] = counts.get(b["category"], 0) + 1

    ordered = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    total = sum(c for _, c in ordered)

    result = []
    running = 0
    for category, count in ordered:
        running += count
        cumulative_pct = round(running / total * 100, 1)
        result.append((category, count, cumulative_pct))
    return result


def get_fishbone_data() -> dict:
    """
    Returns {branch: [bug_title, ...]} for all six standard branches
    (empty list where there are no causes yet), built from real bug
    titles via CATEGORY_TO_FISHBONE.
    """
    branches = {name: [] for name in FISHBONE_BRANCHES}
    for b in bug_service.get_all_bugs():
        branch = CATEGORY_TO_FISHBONE.get(b["category"], "Measurement")
        branches[branch].append(b["title"])
    return branches
