from passlib.context import CryptContext


pwc_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwc_context.hash(password)

def verify(plain_password, hashed_password):
    """Verifies if plain_password and hashed_password match"""
    return pwc_context.verify(plain_password, hashed_password) 