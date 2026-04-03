import bcrypt
from config import settings
import logging

logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    try:
        # Generate salt and hash the password
        salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to hash password: {str(e)}")
        raise

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        logger.error(f"Failed to verify password: {str(e)}")
        return False

def validate_phone_number(phone: str) -> bool:
    """Validate Indian mobile number format"""
    import re
    return bool(re.match(r'^[6-9]\d{9}$', phone))

def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def sanitize_string(text: str) -> str:
    """Sanitize string input"""
    if not text:
        return ""
    # Remove potentially harmful characters
    import re
    text = re.sub(r'[<>"\';]', '', text)
    return text.strip()

def validate_password_strength(password: str) -> dict:
    """Validate password strength and return feedback"""
    feedback = {
        "is_valid": True,
        "errors": [],
        "score": 0
    }
    
    if len(password) < 8:
        feedback["is_valid"] = False
        feedback["errors"].append("Password must be at least 8 characters long")
    else:
        feedback["score"] += 1
    
    if not any(c.isupper() for c in password):
        feedback["is_valid"] = False
        feedback["errors"].append("Password must contain at least one uppercase letter")
    else:
        feedback["score"] += 1
    
    if not any(c.islower() for c in password):
        feedback["is_valid"] = False
        feedback["errors"].append("Password must contain at least one lowercase letter")
    else:
        feedback["score"] += 1
    
    if not any(c.isdigit() for c in password):
        feedback["is_valid"] = False
        feedback["errors"].append("Password must contain at least one digit")
    else:
        feedback["score"] += 1
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        feedback["errors"].append("Password should contain at least one special character")
    else:
        feedback["score"] += 1
    
    return feedback
