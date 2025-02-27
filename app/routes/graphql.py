import strawberry
from strawberry.fastapi import GraphQLRouter

from app.dependencies import UserDep
from app.models.user import UserType


# Define GraphQL Schema
@strawberry.type
class Query:
    @strawberry.field
    def whoami(self, info) -> UserType:
        user = info.context.get("user")
        if user is None:
            raise Exception("Authentication required")
        return UserType.from_pydantic(user)


schema = strawberry.Schema(query=Query)


async def get_context(user: UserDep) -> dict:
    return {"user": user}


# Initialize GraphQL router
router = GraphQLRouter(
    schema,
    context_getter=get_context,  # type: ignore
    prefix="/data/graphql",
    tags=["graphql"],
)
