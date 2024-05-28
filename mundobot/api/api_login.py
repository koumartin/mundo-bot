import os
import sys
from datetime import timedelta, datetime, timezone
from typing import Annotated
import requests

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from pydantic import BaseModel
from starlette import status

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')

DISCORD_AUTH_URL = 'https://discord.com/api/v10/oauth2/@me'


class Token(BaseModel):
    access_token: str
    token_type: str


class UserData(BaseModel):
    discord_user_id: int


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, os.environ.get('API_JWT_SECRET_KEY'), algorithms=[ALGORITHM])
        user_id: str = payload.get('sub')
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        print(e, file=sys.stderr)
        raise credentials_exception
    return UserData(discord_user_id=user_id)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.environ.get('API_JWT_SECRET_KEY'), algorithm=ALGORITHM)
    return encoded_jwt


get_current_user_depends = Annotated[UserData, Depends(get_current_user)]


class LoginRouter:
    def __init__(self):
        self.router = APIRouter(
            prefix="/login",
            tags=["login"],
        )
        self.setup_routes()
        self.active_users = {}

    def setup_routes(self):
        @self.router.post('')
        async def login(discord_token: str) -> Token:
            # Find if user already is logged in
            if discord_token in self.active_users:
                access_token = self.active_users[discord_token]
                return Token(access_token=access_token, token_type="Bearer")
            else:
                # Not logged in -> get login session from discord
                resp = requests.get(DISCORD_AUTH_URL, headers={'Authorization': f'Bearer {discord_token}'})
                if resp.status_code != 200:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                        detail='Access token not authorized in discord')
                user_id = resp.json()['user']['id']

                access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
                access_token = create_access_token(data={'sub': user_id}, expires_delta=access_token_expires)
                self.active_users[discord_token] = access_token

                return Token(access_token=access_token, token_type='bearer')

