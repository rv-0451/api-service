from typing import Optional

from fastapi import Security, Depends, HTTPException, status
from fastapi.security import OAuth2, HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.security.api_key import APIKeyHeader
from fastapi.requests import Request

from jose import jwt, JWTError
import secrets

from core.schemas.users import User
from core.settings import SecuritySettings
from core.schemas.auth import TokenData
from core.databases.external import ExternalDB


class OAuth2PasswordBearerHeaderOrCookie(OAuth2):
    """
    This class is used instead of standard OAuth2PasswordBearer
    to check for cookie also.
    This class will check headers and then fall back to cookies.
    Based on https://github.com/tiangolo/fastapi/issues/480#issuecomment-526149030
    """
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str = None,
        scopes: dict = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        header_authorization: str = request.headers.get("Authorization")
        cookie_authorization: str = request.cookies.get("Authorization")

        header_scheme, header_param = get_authorization_scheme_param(
            header_authorization
        )
        cookie_scheme, cookie_param = get_authorization_scheme_param(
            cookie_authorization
        )

        if header_scheme.lower() == "bearer":
            authorization = True
            scheme = header_scheme
            param = header_param
        elif cookie_scheme.lower() == "bearer":
            authorization = True
            scheme = cookie_scheme
            param = cookie_param
        else:
            authorization = False

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


sec_settings = SecuritySettings()

oauth2_scheme = OAuth2PasswordBearerHeaderOrCookie(tokenUrl="/api/v1/auth/tokens", auto_error=False)
api_key_header = APIKeyHeader(name=sec_settings.api_key_name, auto_error=False)
basic = HTTPBasic(auto_error=False)


def get_external_user(token: str = Depends(oauth2_scheme)):
    """
    Check if token was sent. Decode token and extract username from it.
    Query external server and get external user model.
    Return None if any step fails or user does not exist in the external system.
    """
    if not token:
        return None
    try:
        payload = jwt.decode(
            token,
            sec_settings.secret_key,
            algorithms=[sec_settings.algorith]
        )
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username)
    except JWTError:
        return None
    ext_db = ExternalDB()
    user = ext_db.get_user(token_data.username)
    return user


async def get_api_key_user(api_key_header: str = Security(api_key_header)):
    """
    Check if header was sent. Check api key is correct.
    Return basic user model with header name as user login.
    Return None if any step fails.
    """
    if not api_key_header:
        return None
    correct_apikey = secrets.compare_digest(api_key_header, sec_settings.api_key)
    if not correct_apikey:
        return None
    return User(login=sec_settings.api_key_name.lower())


async def get_http_basic_user(credentials: HTTPBasicCredentials = Depends(basic)):
    """
    Check if http basic creds were sent. Check if creds are correct.
    Return basic user model with basic user name as user login.
    Return None if any step fails.
    """
    if not credentials:
        return None
    correct_username = secrets.compare_digest(
        credentials.username,
        sec_settings.basic_username
    )
    correct_password = secrets.compare_digest(
        credentials.password,
        sec_settings.basic_password
    )
    if not (correct_username and correct_password):
        return None
    return User(login=sec_settings.basic_username.lower())


async def auth_check(
    apikey_user: User = Depends(get_api_key_user),
    basic_user: User = Depends(get_http_basic_user),
    external_user: User = Depends(get_external_user),
):
    """
    Resolve all auth dependencies: apikey, basic, bearer.
    Check for non-None result in order.
    Return user model of the first correctly resolved dependency.
    Return 401 if none of the dependencies were resolved.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "ApiKey, Basic, Bearer"},
    )
    if apikey_user:
        return apikey_user
    if basic_user:
        return basic_user
    if external_user:
        return external_user
    raise credentials_exception
