from datetime import datetime

from sqlalchemy.orm import Session

from models.users import User
from schemas.auth import LoginRequest
from utils.security import hash_password, verify_password


class UserClass:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        normalized = email.strip().lower()
        return self.db.query(User).filter(User.email == normalized).first()

    def authenticate(self, credentials: LoginRequest) -> User | None:
        user = self.get_by_email(str(credentials.email))
        if user is None or not user.is_active:
            return None
        if not verify_password(credentials.password, user.password):
            return None

        user.last_login_at = datetime.utcnow()
        user.updated_date = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_user(
        self,
        *,
        email: str,
        password: str,
        full_name: str | None = None,
        is_active: bool = True,
    ) -> User:
        now = datetime.utcnow()
        user = User(
            email=email.strip().lower(),
            password=hash_password(password),
            full_name=full_name,
            is_active=is_active,
            added_date=now,
            updated_date=now,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def count(self) -> int:
        return self.db.query(User).count()
