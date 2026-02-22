from functools import wraps
from logging import getLogger
from os import getenv
from typing import Any, Callable, ParamSpec, TypeVar

from apiflask import abort as api_abort
from flask import request, abort
from flask_babel import gettext
from flask_login import current_user
from sqlalchemy import select

from db import db

ALLOW_USERS = getenv('ALLOW_USERS') == 'true'
ALLOW_POSTS = getenv('ALLOW_POSTS') == 'true'

P = ParamSpec('P')
R = TypeVar('R')
View = Callable[P, R]

logger = getLogger('app_logger')

def _get_entity(model_class: Any):
    """
    Gets entity from given class and ID passed in request arguments.
    """
    v_args = request.view_args

    try:
        entity_id = list(v_args.values())[-1]
        entity_name = list(v_args.keys())[-1].strip('_id')
    except IndexError as exception:
        return

    entity = db.session.scalars(
        select(model_class)
        .where(model_class.id == entity_id)
    ).first()

    return entity, entity_name

def _level_required(LEVEL: int, model_class: Any, abort_fn: Callable[..., None], *abort_args):
    """
    Restricts callback from users below a given level or 
    who aren't moderators, or who aren't the author of a given entity.
    """
    def decorator(callback: View) -> View:
        @wraps(callback)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            view = callback.__name__

            entity = _get_entity(model_class)
            owner = getattr(entity, 'author', getattr(entity, 'user_id', None))
            is_owner = owner in (current_user or current_user.id)

            if (current_user.level >= LEVEL or
            current_user.is_moderator or is_owner):
                logger.debug(
                    f'Allowing {current_user.name} to view: {view} '\
                    f'(level required view: {LEVEL})'
                )
                return callback(*args, **kwargs)

            logger.debug(
                f'Disallowing {current_user.name} from view: {view} '\
                f'(level required view: {LEVEL})'
            )
            return abort_fn(*abort_args)

        return wrapper

    return decorator

def admin_only(callback: View) -> View:
    """
    Restricts callback from users who aren't an admin.
    """
    @wraps(callback)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        view = callback.__name__

        if current_user.is_admin:
            logger.info(
                f'Allowed {current_user.name} on admin restricted '\
                f'view: {view}'
            )
            return callback(*args, **kwargs)
        else:
            logger.warning(
                f'Disallowed {current_user.name} '\
                f'access to admin restricted view: {view}'
            )
            return abort(403)

    return wrapper

def api_level_required(LEVEL: int, model_class: Any):
    """
    Restricts API endpoint from people who are below the level,
    or who aren't moderators and don't own the resource.

    Args:
        LEVEL: Minimum level required
        model_class: Model to query for ownership attainment
    """
    return _level_required(
        LEVEL,
        model_class,
        api_abort,
        401,
        gettext('Can\'t access this party yet boss.')
    )

def anonymous_only(callback: View) -> View:
    """
    Restricts view for anonymous users only.

    Args:
        callback: Route to restrict
    """
    @wraps(callback)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        view = callback.__name__

        if current_user.is_anonymous:
            return callback(*args, **kwargs)
        else:
            logger.debug(
                f'Disallowing {current_user.name} from accessing '\
                f'an anonymous only view: {view}'
            )
            return abort(403)

    return wrapper

def level_required(LEVEL: int, model_class: Any):
    """
    Restricts frontend endpoint from users who aren't of level,
    or who don't own the resource nor aren't moderators.

    Args:
        LEVEL: Minimum required level
        model_class: Model to query for ownership attainment
    """
    return _level_required(LEVEL, model_class, abort, 403)

def moderator_only(callback: View) -> View:
    """
    Restricts view for users marked as moderator and up.

    Args:
        callback: Route to restrict
    """
    @wraps(callback)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        view = callback.__name__

        if current_user.is_moderator:
            logger.info(
                f'Allowing {current_user.name} to moderator only view: {view}'
            )
            return callback(*args, **kwargs)
        else:
            logger.warning(
                f'Disallowing {current_user.name} from accessing'\
                f'moderator only view: {view}'
            )
            return abort(403)

    return wrapper

def owner_only(model_class: Any):
    """
    Restricts view for users that own a resource or are moderators.

    Args:
        model_class: Model to query for ownership attainment
    """
    def decorator(callback: View) -> View:
        @wraps(callback)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            view = callback.__name__

            entity, entity_name = _get_entity(model_class)
            kwargs[entity_name] = entity

            owner = getattr(entity, 'author', getattr('user_id', None))

            if (owner == current_user or
            owner == current_user.id or
            current_user.is_moderator):
                logger.debug(
                    f'Allowing {current_user.name} to owner-only view: {view}'
                )
                return callback(*args, **kwargs)

            logger.debug(
                f'Disallowing {current_user.name} from owner-only '\
                f'view: {view}'
            )
            return abort(403)

        return wrapper
    return decorator

def owner_or_perm_required(model_class: Any, slug: str):
    """
    Restricts view to users owning the resource or
    having a permission slip.

    Args:
        model_class: Model to query for ownership attainment
        slug: Permission name
    """
    def decorator(callback: View) -> View:
        @wraps(callback)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            view = callback.__name__

            entity, entity_name = _get_entity(model_class)
            owner = getattr(entity, 'author', getattr(entity, 'user_id', None))
            kwargs[entity_name] = entity

            if (owner == current_user or
                owner == current_user.id or
                current_user.has_permission(slug)):
                logger.debug(
                    f'Allowing {current_user.name} on owner-only/permission '\
                    f'restricted view: {view}; Permission: {slug}'
                )
                return callback(*args, **kwargs)

            logger.debug(
                f'Disallowed {current_user.name} from owner-only/permission '\
                f'restricted view: {view}; Permission: {slug}'
            )
            return abort(403)

        return wrapper

    return decorator

def post_protect(callback: View) -> View:
    """
    Restricts view if post management is not possible at the moment.

    Args:
        callback: Route to restrict
    """
    @wraps(callback)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        view = callback.__name__

        if ALLOW_POSTS or current_user.is_moderator:
            logger.debug(
                f'Allowed {current_user.name} on post protected view: {view}'
            )
            return callback(*args, **kwargs)
        else:
            logger.debug(
                f'Disallowed {current_user.name} from post protected '\
                f'view: {view}'
            )
            abort(403)

    return wrapper

def perm_required(slug: str):
    """
    Restricts view to users who have specified permission.

    Args:
        slug: Permission name
    """
    def decorator(callback: View) -> View:
        @wraps(callback)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            view = callback.__name__

            if current_user.has_permission(slug):
                logger.debug(
                    f'Allowed {current_user.name} on permission restricted '\
                    f'view: {view}; Permission: {slug}'
                )
                return callback(*args, **kwargs)
            else:
                logger.debug(
                    f'Disallowed {current_user.name} from permission '\
                    f'restricted view: {view}; Permission {slug}'
                )
                return abort(403)

        return wrapper

    return decorator

def user_protect(callback: View) -> View:
    """
    Restricts view if user account management is not possible at the moment.

    Args:
        callback: Route to restrict
    """
    @wraps(callback)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        view = callback.__name__

        if ALLOW_USERS:
            logger.debug(
                f'Allowing access to user protected view: {view}'
            )
            return callback(*args, **kwargs)
        else:
            logger.debug(
                f'Disallowing access to user protected view: {view}'
            )
            return abort(403)

    return wrapper
