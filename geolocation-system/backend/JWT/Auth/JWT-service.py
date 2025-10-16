from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.routing import APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
import logging
import os

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="JWT Service")
router = APIRouter(prefix="/JWT", tags=["JWT"])

# Конфигурация токенов
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


class User(BaseModel):
    id: int
    username: str
    email: str
    role: str


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class VerifyResponse(BaseModel):
    valid: bool
    username: Optional[str] = None


class AuthService:
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: Optional[str] = payload.get("sub")
            if not username:
                return None
            # Заглушка вместо запроса в БД
            return User(id=1, username=username, email="user@example.com", role="user")
        except JWTError:
            return None


auth_service = AuthService()


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """Аутентификация пользователя и выдача JWT токена"""
    logger.info(f"Login attempt for user: {credentials.username}")
    # Заглушка вместо БД
    if credentials.username == "admin" and credentials.password == "admin":
        access_token = auth_service.create_access_token(data={"sub": credentials.username})
        logger.info(f"Successful login for user: {credentials.username}")
        return {"access_token": access_token, "token_type": "bearer"}
    logger.warning(f"Failed login attempt for user: {credentials.username}")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")


@router.get("/me", response_model=User)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Возвращает данные текущего пользователя по JWT"""
    token = credentials.credentials
    user = auth_service.verify_token(token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    return user


@router.get("/verify", response_model=VerifyResponse)
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Проверка валидности JWT токена"""
    token = credentials.credentials
    user = auth_service.verify_token(token)
    return {"valid": user is not None, "username": user.username if user else None}


@router.post("/register")
async def register(user_data: RegisterRequest):
    """Регистрация нового пользователя (заглушка)"""
    logger.info(f"Registration attempt for user: {user_data.username}")
    _hashed = auth_service.get_password_hash(user_data.password)
    logger.info(f"User registered successfully: {user_data.username}")
    return {"message": "User registered successfully"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "jwt-service"}


# Подключение роутера JWT
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

