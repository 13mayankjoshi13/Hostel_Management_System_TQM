"""
Strict Validation (Q09 feature #2 / Poka-Yoke - Error Prevention).

All validation happens BEFORE any database write. Every function raises
ValidationError with a clear, user-facing message on failure and returns
the cleaned value on success, so callers can do:

    name = validate_student_name(raw_name)

instead of checking booleans everywhere.
"""


class ValidationError(Exception):
    """Raised when input fails a business validation rule."""
    pass


def validate_student_name(name: str) -> str:
    if name is None or not str(name).strip():
        raise ValidationError("Student name cannot be empty.")
    name = str(name).strip()
    if len(name) < 2:
        raise ValidationError("Student name must be at least 2 characters long.")
    if len(name) > 100:
        raise ValidationError("Student name cannot exceed 100 characters.")
    if not all(ch.isalpha() or ch.isspace() or ch in ".'-" for ch in name):
        raise ValidationError("Student name contains invalid characters.")
    return name


def validate_registration_number(reg_no: str) -> str:
    if reg_no is None or not str(reg_no).strip():
        raise ValidationError("Registration number cannot be empty.")
    reg_no = str(reg_no).strip()
    if len(reg_no) < 3 or len(reg_no) > 30:
        raise ValidationError("Registration number must be between 3 and 30 characters.")
    if not all(ch.isalnum() for ch in reg_no):
        raise ValidationError("Registration number must be alphanumeric only.")
    return reg_no


def validate_contact_number(contact: str) -> str:
    if contact is None or not str(contact).strip():
        raise ValidationError("Contact number cannot be empty.")
    contact = str(contact).strip()
    if not contact.isdigit():
        raise ValidationError("Contact number must contain digits only.")
    if len(contact) != 10:
        raise ValidationError("Contact number must be exactly 10 digits.")
    return contact


def validate_room_number(room_no: str) -> str:
    if room_no is None or not str(room_no).strip():
        raise ValidationError("Room number cannot be empty.")
    room_no = str(room_no).strip()
    if len(room_no) > 10:
        raise ValidationError("Room number cannot exceed 10 characters.")
    if not all(ch.isalnum() for ch in room_no):
        raise ValidationError("Room number must be alphanumeric only.")
    return room_no


def validate_capacity(capacity) -> int:
    try:
        capacity = int(capacity)
    except (TypeError, ValueError):
        raise ValidationError("Room capacity must be a whole number.")
    if capacity <= 0:
        raise ValidationError("Room capacity must be greater than 0.")
    if capacity > 10:
        raise ValidationError("Room capacity cannot exceed 10.")
    return capacity


def validate_complaint_category(category: str) -> str:
    allowed = {"Maintenance", "Cleanliness", "Noise", "Security", "Food", "Other"}
    if category is None or not str(category).strip():
        raise ValidationError("Complaint category cannot be empty.")
    category = str(category).strip().capitalize()
    if category not in allowed:
        raise ValidationError(f"Complaint category must be one of: {', '.join(sorted(allowed))}.")
    return category


def validate_complaint_description(description: str) -> str:
    if description is None or not str(description).strip():
        raise ValidationError("Complaint description cannot be empty.")
    description = str(description).strip()
    if len(description) < 5:
        raise ValidationError("Complaint description must be at least 5 characters long.")
    if len(description) > 500:
        raise ValidationError("Complaint description cannot exceed 500 characters.")
    return description


def validate_assigned_to(name: str) -> str:
    if name is None or not str(name).strip():
        raise ValidationError("Assigned staff name cannot be empty.")
    name = str(name).strip()
    if len(name) < 2 or len(name) > 50:
        raise ValidationError("Assigned staff name must be between 2 and 50 characters.")
    if not all(ch.isalpha() or ch.isspace() or ch in ".'-" for ch in name):
        raise ValidationError("Assigned staff name contains invalid characters.")
    return name


def validate_resolution_notes(notes: str) -> str:
    if notes is None or not str(notes).strip():
        raise ValidationError("Resolution notes cannot be empty.")
    notes = str(notes).strip()
    if len(notes) < 5:
        raise ValidationError("Resolution notes must be at least 5 characters long.")
    if len(notes) > 500:
        raise ValidationError("Resolution notes cannot exceed 500 characters.")
    return notes


def validate_username(username: str) -> str:
    if username is None or not str(username).strip():
        raise ValidationError("Username cannot be empty.")
    username = str(username).strip()
    if len(username) < 3 or len(username) > 30:
        raise ValidationError("Username must be between 3 and 30 characters.")
    if not all(ch.isalnum() or ch == "_" for ch in username):
        raise ValidationError("Username may only contain letters, numbers, and underscores.")
    return username


def validate_password(password: str) -> str:
    if password is None or not str(password):
        raise ValidationError("Password cannot be empty.")
    if len(password) < 6:
        raise ValidationError("Password must be at least 6 characters long.")
    if not any(ch.isdigit() for ch in password):
        raise ValidationError("Password must contain at least one digit.")
    if not any(ch.isalpha() for ch in password):
        raise ValidationError("Password must contain at least one letter.")
    return password


def validate_role(role: str) -> str:
    allowed = {"Administrator", "Warden", "Staff"}
    if role is None or not str(role).strip():
        raise ValidationError("Role cannot be empty.")
    role = str(role).strip().capitalize()
    if role not in allowed:
        raise ValidationError(f"Role must be one of: {', '.join(sorted(allowed))}.")
    return role


def validate_bug_module(module: str) -> str:
    allowed = {"Student", "Room", "Allocation", "Complaint", "Database", "UI", "Other"}
    if module is None or not str(module).strip():
        raise ValidationError("Module cannot be empty.")
    raw = str(module).strip()
    module = "UI" if raw.upper() == "UI" else raw.capitalize()
    if module not in allowed:
        raise ValidationError(f"Module must be one of: {', '.join(sorted(allowed))}.")
    return module


def validate_bug_category(category: str) -> str:
    allowed = {"Functional", "UI/UX", "Validation", "Performance", "Data Integrity", "Security", "Other"}
    if category is None or not str(category).strip():
        raise ValidationError("Bug category cannot be empty.")
    category = str(category).strip()
    if category not in allowed:
        raise ValidationError(f"Bug category must be one of: {', '.join(sorted(allowed))}.")
    return category


def validate_bug_title(title: str) -> str:
    if title is None or not str(title).strip():
        raise ValidationError("Bug title cannot be empty.")
    title = str(title).strip()
    if len(title) < 5:
        raise ValidationError("Bug title must be at least 5 characters long.")
    if len(title) > 120:
        raise ValidationError("Bug title cannot exceed 120 characters.")
    return title


def validate_bug_description(description: str) -> str:
    if description is None or not str(description).strip():
        raise ValidationError("Bug description cannot be empty.")
    description = str(description).strip()
    if len(description) < 5:
        raise ValidationError("Bug description must be at least 5 characters long.")
    if len(description) > 500:
        raise ValidationError("Bug description cannot exceed 500 characters.")
    return description


def validate_severity(severity: str) -> str:
    allowed = {"Low", "Medium", "High", "Critical"}
    if severity is None or not str(severity).strip():
        raise ValidationError("Severity cannot be empty.")
    severity = str(severity).strip().capitalize()
    if severity not in allowed:
        raise ValidationError(f"Severity must be one of: {', '.join(sorted(allowed))}.")
    return severity


def validate_priority(priority: str) -> str:
    allowed = {"Low", "Medium", "High"}
    if priority is None or not str(priority).strip():
        raise ValidationError("Priority cannot be empty.")
    priority = str(priority).strip().capitalize()
    if priority not in allowed:
        raise ValidationError(f"Priority must be one of: {', '.join(sorted(allowed))}.")
    return priority


def validate_root_cause(text: str) -> str:
    if text is None or not str(text).strip():
        raise ValidationError("Root cause cannot be empty.")
    text = str(text).strip()
    if len(text) < 5:
        raise ValidationError("Root cause must be at least 5 characters long.")
    if len(text) > 300:
        raise ValidationError("Root cause cannot exceed 300 characters.")
    return text


def validate_corrective_action(text: str) -> str:
    if text is None or not str(text).strip():
        raise ValidationError("Corrective action cannot be empty.")
    text = str(text).strip()
    if len(text) < 5:
        raise ValidationError("Corrective action must be at least 5 characters long.")
    if len(text) > 300:
        raise ValidationError("Corrective action cannot exceed 300 characters.")
    return text


def validate_test_case(text: str) -> str:
    if text is None or not str(text).strip():
        raise ValidationError("Test case reference cannot be empty.")
    text = str(text).strip()
    if len(text) < 3:
        raise ValidationError("Test case reference must be at least 3 characters long.")
    if len(text) > 300:
        raise ValidationError("Test case reference cannot exceed 300 characters.")
    return text


def validate_room_type(room_type: str) -> str:
    allowed = {"Single", "Double", "Triple", "Dormitory"}
    if room_type is None or not str(room_type).strip():
        raise ValidationError("Room type cannot be empty.")
    room_type = str(room_type).strip().capitalize()
    if room_type not in allowed:
        raise ValidationError(f"Room type must be one of: {', '.join(sorted(allowed))}.")
    return room_type
