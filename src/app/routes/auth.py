from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jwt.exceptions import InvalidTokenError

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.core.database import get_db
from app.crud import auth as auth_crud
from app.crud.user import get_user_by_id
from app.schemas.auth import LoginRequest, RefreshRequest
from app.schemas.common import SuccessResponse
from app.schemas.token import Token

router = APIRouter(prefix="/auth", tags=["Authentication"])

def _refresh_token_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )

def _get_valid_refresh_token(
    db: Session,
    raw_token: str,
):
    try:
        payload = decode_refresh_token(raw_token)
        user_id = int(payload["sub"])
        jti = payload["jti"]
    except (
        InvalidTokenError,
        KeyError,
        TypeError,
        ValueError,
    ):
        raise _refresh_token_error()

    stored_token = auth_crud.get_refresh_token(
        db,
        raw_token,
    )

    if stored_token is None:
        raise _refresh_token_error()

    if stored_token.jti != jti:
        raise _refresh_token_error()

    if stored_token.revoked_at is not None:
        raise _refresh_token_error()

    expires_at = stored_token.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    if expires_at <= datetime.now(timezone.utc):
        raise _refresh_token_error()

    user = get_user_by_id(db, user_id)

    if user is None:
        raise _refresh_token_error()

    return stored_token, user


@router.post("/login", response_model=Token)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
) -> Token:
    user = auth_crud.auth_login(
        db=db,
        email=credentials.email,
        password=credentials.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(user.user_id)

    refresh_token, jti, expires_at = create_refresh_token(
        user.user_id
    )

    auth_crud.save_refresh_token(
        db=db,
        user_id=user.user_id,
        token=refresh_token,
        jti=jti,
        expires_at=expires_at,
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=Token)
def refresh(
    credentials: RefreshRequest,
    db: Session = Depends(get_db),
) -> Token:
    stored_token, user = _get_valid_refresh_token(
        db,
        credentials.refresh_token,
    )

    auth_crud.revoke_refresh_token(
        db,
        stored_token,
    )

    access_token = create_access_token(user.user_id)

    refresh_token, jti, expires_at = create_refresh_token(
        user.user_id
    )

    auth_crud.save_refresh_token(
        db=db,
        user_id=user.user_id,
        token=refresh_token,
        jti=jti,
        expires_at=expires_at,
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/logout", response_model=SuccessResponse)
def logout(
    credentials: RefreshRequest,
    db: Session = Depends(get_db),
) -> SuccessResponse:
    stored_token = auth_crud.get_refresh_token(
        db,
        credentials.refresh_token,
    )

    if stored_token is not None:
        auth_crud.revoke_refresh_token(
            db,
            stored_token,
        )

    return SuccessResponse()