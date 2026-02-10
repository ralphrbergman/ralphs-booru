from typing import Optional, TypeVar

from sqlalchemy import Select, or_, select
from sqlalchemy.exc import IntegrityError

from db import db, User
from .base import browse_element

T = TypeVar('T')

def browse_user(*args, **kwargs):
    """
    Creates and executes select of users by criteria.
    """
    def user_select(stmt: Select[T]) -> Select[T]:
        terms = kwargs.get('terms')
        if not terms:   return stmt

        conditions = set()

        for word in terms.split():
            conditions.add(User.name == word)
            conditions.add(User.name.icontains(word))
            conditions.add(User.mail == word)
            conditions.add(User.mail.icontains(word))

        return stmt.where(or_(*conditions))

    return browse_element(User, user_select, *args, **kwargs)

def create_user(
    name: str,
    mail: str,
    password: str,
    avatar: Optional[str] = None
) -> Optional[User]:
    """
    Creates and returns user object.

    Args:
        name: User's username
        mail: User's e-mail
        password: Hashed user's password
        avatar: Optional avatar filename
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
