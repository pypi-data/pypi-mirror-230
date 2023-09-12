import re

def validate_email(email):
    email_regex = r"[^@]+@[^@]+\.[^@]+"
    return re.match(email_regex, email) is not None

def is_secure_password(password):
    if len(password) < 8:
        return False

    if not any(char.isupper() for char in password):
        return False
    if not any(char.islower() for char in password):
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char in "!@#$%^&*()-_=+{}[]|;:,<.>/?`~" for char in password):
        return False

    return True