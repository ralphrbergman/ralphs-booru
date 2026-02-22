from logging import getLogger
from typing import Optional, TypeVar

from flask_sqlalchemy.pagination import SelectPagination
from sqlalchemy import Select, or_, select

from db import db, User
from .base import browse_element

T = TypeVar('T')

logger = getLogger('app_logger')

def browse_user(*args, **kwargs) -> SelectPagination[User]:
    """
    Paginates users by criteria.

    Args:
        direction (str, optional): Sorting direction, asc for ascending
        and desc for descending
        limit (int): Amount of users per page
        page (int): Page
        sort (str): User's column to sort by
        terms (str): Username or user's e-mail
    """
    def user_select(stmt: Select[T]) -> Select[T]:
        terms: str = kwargs.get('terms')
        if not terms:   return stmt

        conditions = set()

        for word in terms.split():
            conditions.add(User.name == word)
            conditions.add(User.name.icontains(word))
            conditions.add(User.mail == word)
            conditions.add(User.mail.icontains(word))
            logger.debug(f'Searching users for username and e-mail of {word}')

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

    logger.info(f'Created user: {user.id}')
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
