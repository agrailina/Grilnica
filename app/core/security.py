from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import Settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Создание access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=Settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow()
    })
    return jwt.encode(
        to_encode, 
        Settings.SECRET_KEY,  # Берётся из .env
        algorithm=Settings.ALGORITHM
    )

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Создание refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=Settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow()
    })
    return jwt.encode(
        to_encode, 
        Settings.SECRET_KEY, 
        algorithm=Settings.ALGORITHM
    )

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Декодирование любого токена"""
    try:
        payload = jwt.decode(
            token, 
            Settings.SECRET_KEY, 
            algorithms=[Settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        # Логируем ошибку, но не раскрываем детали
        print(f"Token decode error: {type(e).__name__}")
        return None