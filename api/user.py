from typing import Literal, Optional

from flask_sqlalchemy.pagination import SelectPagination
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError

from db import db, User
from encryption import bcrypt

DEFAULT_LIMIT = 20
DEFAULT_SORT = 'desc'
LIMIT_THRESHOLD = 100

def browse_user(
    limit: Optional[int] = DEFAULT_LIMIT,
    page: Optional[int] = 1,
    sort_str: Optional[Literal['asc', 'desc']] = DEFAULT_SORT
):
    if limit and limit > LIMIT_THRESHOLD:
        limit = LIMIT_THRESHOLD

    stmt = select(User).order_by(
        getattr(User.id, sort_str)()
    )

    users = db.paginate(
        stmt,
        page = page,
        per_page = limit
    )

    return users

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

    user.name = name
    user.mail = mail
    user.password = set_password(password)
    user.avatar_name = avatar

    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError as exc:
        # User's name & e-mail can raise this.
        db.session.rollback()

        return None

    return user

def check_password(password: bytes, other_password: str) -> bool:
    """
    Checks whether the input password is the one stored.

    Args:
        other_password: The password

    Returns:
        bool: Whether the password is correct
    """
    return bcrypt.check_password_hash(password, other_password)

def get_user(user_id: int) -> Optional[User]:
    """
    Returns user from given user ID which can also be the user's username.

    Args:
        user_id: User's unique ID or username

    Returns:
        User: Found user, if any
    """
    return db.session.scalar(
        select(User).where(
            or_(
                User.id.is_(user_id),
                User.name.is_(user_id)
            )
        )
    )

def set_password(password: str) -> bytes:
    """
    Sets and returns password in hashed form.

    Args:
        password: The password to assign
    
    Returns:
        bytes: Hashed password
    """
    hashed_password = bcrypt.generate_password_hash(password)

    return hashed_password
