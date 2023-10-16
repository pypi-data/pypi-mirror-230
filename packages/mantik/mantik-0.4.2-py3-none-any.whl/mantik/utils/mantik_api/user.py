import uuid

import pydantic


class User(pydantic.BaseModel):
    user_id: uuid.UUID = pydantic.Field(..., alias="userId")
    name: str
    email: str
