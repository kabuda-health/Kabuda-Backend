from strawberry.fastapi import GraphQLRouter
import strawberry
from app.dependencies import UserDep
from app.models.user import User as PydanticUser
from fastapi import Request

@strawberry.type
class User:
    id: int
    name: str

    @staticmethod
    def from_pydantic(user: PydanticUser) -> "User":
        return User(id=user.id, name=user.name)

# Define GraphQL Schema
@strawberry.type
class Query:
    @strawberry.field
    def whoami(self, info) -> User:
        user = info.context.get("user")
        if user is None:
            raise Exception("Authentication required")
        return User.from_pydantic(user)

schema = strawberry.Schema(query=Query)

async def get_context(request: Request, user: UserDep) -> dict:
    token = request.headers.get("Authorization")
    if not token:
        return {"user": None}
    
    return {"user": user}

# Initialize GraphQL router
graphql_router = GraphQLRouter(schema, context_getter=get_context, prefix="/data/graphql", tags=['graphql'])

