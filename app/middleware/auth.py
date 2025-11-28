from fastapi import Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_model import User
from app.auth.jwt import verify_access_token
from datetime import datetime

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request, db: Session = Depends(get_db)):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or missing authorization token"
            )

        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authentication scheme"
            )

        user = self.verify_jwt(credentials.credentials, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        return user  

    def verify_jwt(self, token: str, db: Session):
        try:
            payload = verify_access_token(token)
            user_id = payload.get("sub")

            if user_id is None:
                return None

            user = db.query(User).filter(User.id == user_id).first()
            return user

        except Exception:
            return None


authMiddleware = JWTBearer()

def get_current_user(user: User = Depends(authMiddleware)):
    return user
