# Hostel Management System — TQM Project

**Student:** Mayank Joshi  
**Roll No.:** 2410302037  
**Branch:** CSE  
**Section:** B  
**Course:** BBAT104 — Fundamentals of TQM  
**Academic Session:** 2026–27

## Assigned Project

**Baseline System:** Hostel Management System  
**Assigned Quality Goal:** **Q09 — Reduce Bugs**

The project allotment sheet assigns Mayank Joshi to the Hostel Management System with Q09 — Reduce Bugs. The five suggested Q09 features are:

1. Exception Handling
2. Strict Validation
3. Module Tests
4. Bug Tracker
5. Error Logs

The Hostel Management System will therefore use these five features as its primary quality-goal implementation while also applying the required TQM concepts and SQC tools.

## Core Operational Focus

The baseline hostel system focuses on:

- Room allocation
- Complaint resolution

## Main TQM Approach

**Prevent → Control → Detect → Record → Analyze → Improve**

Quality will be built into the software process rather than checked only after development.

## Planned System Modules

- Authentication and user roles
- Student management
- Room management
- Room allocation
- Complaint management
- Quality/error monitoring
- Audit logging
- Bug tracking
- Reporting

## TQM Artifacts

The `TQM/` directory contains:

- Customer requirements
- Assigned quality goal
- Quality features
- Error prevention
- Process control
- Process map
- SIPOC
- CTQ tree
- FMEA
- Quality monitoring
- Pareto analysis
- Fishbone analysis
- PDCA
- Requirements traceability
- Quality data templates

## Development

The application will be developed incrementally using Python, SQLite and a GUI based on the technologies specified in the course guidelines.

## Repository Principle

> Quality should be built into the process, not checked only at the end.

## Implementation Status

The five Q09 features are implemented:

| Q09 Feature | Where |
|---|---|
| Exception Handling | `app/utils/exception_handler.py`; services convert database errors into controlled messages |
| Strict Validation | `app/utils/validation.py`; forward-only status pipelines in the services |
| Module Tests | `tests/` — 132 tests, all passing at Batch 16 |
| Bug Tracker | `app/services/bug_service.py`, `app/screens/bug_screen.py`; a bug can only be marked Fixed with root cause, corrective action and test case |
| Error Logs | `app/utils/logging_service.py` → `TQM/data/error_logs.csv` (plus audit and defect logs) |

Also built: a student portal (own room, complaints, leave), leave tracking, room allotment list export, a Washroom complaint category (from a hosteller interview), login with Administrator / Warden / Staff / Student roles, user management (Administrator only), student, room, allocation and complaint modules, and a Quality Monitoring screen (Pareto and Fishbone).

Quality results (defect counts, improvement percentages) are **not yet measured**; they will be reported only from real recorded data.

## Run

```bash
python run.py                                  # first run creates admin / admin123 — change it in User Management
python -m unittest discover -s tests -t .      # run all module tests
```
