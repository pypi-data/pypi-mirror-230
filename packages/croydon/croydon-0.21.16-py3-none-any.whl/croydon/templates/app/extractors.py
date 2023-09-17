from typing import Optional, Callable, Awaitable
from fastapi import Header, Depends, Request

from croydon import ctx
from croydon.errors import AuthenticationError

from app.models import Token, User, Session


async def auth_token(authorization: Optional[str] = Header(default=None)) -> Optional[Token]:
    if authorization is None:
        return None

    parts = authorization.split(" ")
    if len(parts) != 2:
        return None

    token_type, token = parts

    if token_type != "Token":
        return None

    token = await Token.cache_get(token)
    if token:
        if token.is_expired():
            ctx.log.debug(f"token {token.token} is expired")
            return None
        await token.auto_prolong()
    return token


def authenticated_user(required: bool = True) -> Callable[[Optional[Token]], Awaitable[Optional[User]]]:
    async def inner(token: Optional[Token] = Depends(auth_token),
                    session: Optional[Session] = Depends(current_session)) -> Optional[User]:
        if token is not None:
            user = await token.user()
            if user:
                ctx.log.debug("authenticated_user found by token")
                return user

        if session is not None:
            user = await session.user()
            if user:
                ctx.log.debug("authenticated_user found by session")
                return user

        if required:
            ctx.log.debug("authenticated_user was not found but auth is required")
            raise AuthenticationError()

        ctx.log.debug("authenticated_user was not found")
        return None

    return inner


async def current_session(request: Request) -> Session:
    return request.state.session


