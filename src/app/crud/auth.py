from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone

from app.models.models import User, RefreshToken
from app.core.security import verify_password
from app.core.security import (hash_refresh_token, verify_password)

def auth_login(db: Session, email: str, password: str) -> User | None:
    user = db.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()

    if user is None or not verify_password(
        password,
        user.hashed_password,
    ):
        return None

    return user

def auth_logout(db:Session, user_id: int) -> bool:

    return True

def auth_refresh(db:Session, user_id: int):
    statement = select(User).where(User.user_id == user_id)

    return db.execute(statement).scalar_one_or_none()

def save_refresh_token(
    db: Session,
    user_id: int,
    token: str,
    jti: str,
    expires_at: datetime,
) -> RefreshToken:
    refresh_token = RefreshToken(
        user_id=user_id,
        jti=jti,
        token_hash=hash_refresh_token(token),
        expires_at=expires_at,
    )

    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)

    return refresh_token


def get_refresh_token(
    db: Session,
    token: str,
) -> RefreshToken | None:
    token_hash = hash_refresh_token(token)

    return db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash
        )
    ).scalar_one_or_none()


def revoke_refresh_token(
    db: Session,
    refresh_token: RefreshToken,
) -> None:
    refresh_token.revoked_at = datetime.now(timezone.utc)
    db.commit()