from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from db import db, User
from .base import browse_element

def browse_user(*args, **kwargs):
    return browse_element(User, *args, **kwargs)

def create_user(name: str, mail: str, password: str, avatar: Optional[str] = None) -> Optional[User]:
    """
    Creates and returns user object.

    Args:
        name: User's username
        mail: User's e-mail
        password: Hashed user's password
        avatar: Optional avatar filename

    Returns:
        User: Created user
    """
    user = User()

    user.role_id = 3
    user.name = name
    user.mail = mail
    user.password = password
    user.avatar_name = avatar

    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError as exc:
        # User's name & e-mail can raise this.
        db.session.rollback()

        return None

    return user

def get_user(user_id: int) -> Optional[User]:
    """
    Returns user from given user ID.

    Args:
        user_id: User's unique ID

    Returns:
        User: Found user, if any
    """
    return db.session.scalar(select(User).where(User.id.is_(user_id)))

def get_user_by_username(username: str) -> Optional[User]:
    """
    Returns user from given username.

    Args:
        username: Username

    Returns:
        User: Found user, if any
    """
    return db.session.scalar(select(User).where(User.name.is_(username)))
