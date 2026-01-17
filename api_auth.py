from typing import Optional

from apiflask import HTTPTokenAuth

from db import User
from db.models.user import find_user_by_key

auth = HTTPTokenAuth()

@auth.verify_token
def verify_token(key: str) -> Optional[User]:
    return find_user_by_key(key)
