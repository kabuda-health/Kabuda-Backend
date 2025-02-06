from typing import Annotated

import arrow
import jwt
from fastapi import Depends, Header, HTTPException

from app.settings import settings

JWT_ALGORITHM = "HS256"


def create_jwt(subject: str, name: str, exp: arrow.Arrow) -> str:
    payload = {"sub": subject, "name": name, "exp": exp.timestamp()}
    return jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)


def get_user_id(username: str) -> int:
    # TODO: Implement this function
    return 1


async def verify_token(x_access_token: Annotated[str, Header()]) -> dict:
    try:
        return jwt.decode(
            x_access_token, settings.secret_key, algorithms=[JWT_ALGORITHM]
        )
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))


AuthDep = Annotated[dict, Depends(verify_token)]
