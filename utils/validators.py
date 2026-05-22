"""Input validation utilities."""
import re
from typing import Tuple

def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not email:
        return False, "Email não pode estar vazio"
    if not re.match(pattern, email):
        return False, "Formato de email inválido"
    if len(email) > 254:
        return False, "Email muito longo (máx 254 caracteres)"
    return True, "Válido"

def validate_password(password: str) -> Tuple[bool, str]:
    """Validate password strength."""
    if not password:
        return False, "Senha não pode estar vazia"
    if len(password) < 8:
        return False, "Mínimo 8 caracteres"
    if not re.search(r'[A-Z]', password):
        return False, "Precisa de letra maiúscula"
    if not re.search(r'[a-z]', password):
        return False, "Precisa de letra minúscula"
    if not re.search(r'\d', password):
        return False, "Precisa de número"
    if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
        return False, "Precisa de caractere especial (!@#$%^&*...)"
    return True, "Válido"

def validate_question_text(text: str) -> Tuple[bool, str]:
    """Validate question text."""
    if not text:
        return False, "Texto da questão não pode estar vazio"
    if len(text) < 10:
        return False, "Texto muito curto (mínimo 10 caracteres)"
    if len(text) > 5000:
        return False, "Texto muito longo (máximo 5000 caracteres)"
    return True, "Válido"

def validate_name(name: str, min_length: int = 3, max_length: int = 100) -> Tuple[bool, str]:
    """Validate name field."""
    if not name:
        return False, "Nome não pode estar vazio"
    if len(name) < min_length:
        return False, f"Nome muito curto (mínimo {min_length} caracteres)"
    if len(name) > max_length:
        return False, f"Nome muito longo (máximo {max_length} caracteres)"
    if not re.match(r'^[a-zA-Z0-9\s\-áéíóúãõçñ]+$', name):
        return False, "Nome contém caracteres inválidos"
    return True, "Válido"
