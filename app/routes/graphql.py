from functools import cached_property

import strawberry
from fastapi.security.utils import get_authorization_scheme_param
from strawberry import Info
from strawberry.exceptions import StrawberryGraphQLError
from strawberry.fastapi import BaseContext, GraphQLRouter

from app.dependencies import AuthServiceDep
from app.models.user import User, UserGQL
from app.services.auth_service import AuthService


class Context(BaseContext):
    def __init__(self, auth_service: AuthService) -> None:
        self.auth_service = auth_service

    @cached_property
    def user(self) -> User:
        if not self.request:
            raise RuntimeError("Request is not set")

        authorization = self.request.headers.get("Authorization")
        scheme, token = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise StrawberryGraphQLError(
                "Authorization header is invalid", extensions={"code": 401}
            )
        try:
            payload = self.auth_service.verify_access_token(token)
            return User.from_jwt_payload(payload)
        except Exception as e:
            raise StrawberryGraphQLError(
                f"Verify access token failed: {e}", extensions={"code": 403}
            )


# Define GraphQL Schema
@strawberry.type
class Query:
    @strawberry.field
    def whoami(self, info: Info[Context]) -> UserGQL:
        user = info.context.user
        return UserGQL.from_pydantic(user)


schema = strawberry.Schema(query=Query)


async def get_context(auth_service: AuthServiceDep) -> Context:
    return Context(auth_service)


# Initialize GraphQL router
router = GraphQLRouter(
    schema,
    context_getter=get_context,  # type: ignore[arg-type]
    prefix="/graphql",
    tags=["graphql"],
)
