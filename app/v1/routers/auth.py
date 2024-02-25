import logging
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import Response

from jose import jwt
from datetime import datetime, timedelta

from core.databases.external import ExternalDB
from core.settings import SecuritySettings
from core.schemas.auth import Token


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
)


log = logging.getLogger()


def create_access_token(
    data: dict,
    expires_delta: Union[timedelta, None] = None,
):
    sec_settings = SecuritySettings()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=5)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        sec_settings.secret_key,
        algorithm=sec_settings.algorith
    )
    return encoded_jwt


@router.post("/tokens", response_model=Token)
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Authenticate user to external server, create and return access token.
    Return 401 if authentication fails.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    sec_settings = SecuritySettings()
    ext_db = ExternalDB()
    user = ext_db.authenticate_user(form_data.username, form_data.password)
    if not user:
        log.warn("Unable to fetch the user")
        raise credentials_exception
    access_token_expires = timedelta(
        minutes=sec_settings.access_token_expire_minutes
    )
    access_token = create_access_token(
        data={"sub": user.login}, expires_delta=access_token_expires
    )
    log.info(f"Token issued for user {user.login}")
    response.set_cookie(
        key="Authorization",
        value=f"Bearer {access_token}",
        httponly=False,
        max_age=60*sec_settings.access_token_expire_minutes,
        expires=60*sec_settings.access_token_expire_minutes,
    )
    return {"access_token": access_token, "token_type": "bearer"}
