import re

def generate_student_password(name: str) -> str:
    """
    Standardize password generation for students.
    Rule: FirstName@123
    - Logic: Extract all alphabetical sequences.
    - Pick the first sequence with length > 1 (to skip single-letter initials).
    - If all sequences are 1-char, use the first one.
    - Capitalize first letter, lower others.
    """
    if not name:
        return "Student@123"
    
    # Extract all alphabetical parts
    parts = re.findall(r'[a-zA-Z]+', name)
    
    if not parts:
        return "Student@123"
    
    # Try to find the first part that is likely a full name (length > 1)
    # This avoids taking "S" from "S.KUMAR" if "KUMAR" is available
    target_part = parts[0]
    for p in parts:
        if len(p) > 1:
            target_part = p
            break
            
    # Capitalize first letter, lower others
    standardized_name = target_part.capitalize()
    
    return f"{standardized_name}@123"
