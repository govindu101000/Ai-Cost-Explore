import os
import jwt
import bcrypt

from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_EXPIRE_HOURS = int(
    os.getenv("JWT_EXPIRE_HOURS", "24")
)

JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()


def verify_password(
    password: str,
    password_hash: str
) -> bool:
    return bcrypt.checkpw(
        password.encode(),
        password_hash.encode()
    )


def create_token(
    user_id: int,
    email: str
):

    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow()
        + timedelta(hours=JWT_EXPIRE_HOURS)
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )


def decode_token(token: str):

    return jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALGORITHM]
    )