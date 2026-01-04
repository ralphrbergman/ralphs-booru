from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError

from db import db, User
from encryption import bcrypt
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
