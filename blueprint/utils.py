from logging import getLogger
from math import floor
from typing import Optional, Protocol

from flask import request, flash, url_for
from flask_login import current_user
from flask_wtf import FlaskForm

PAGINATION_DEPTH = 5

class LoggerCallable(Protocol):
    def __call__(self, message: str) -> None:
        ...

logger = getLogger('app_logger')

def create_pagination_bar(
        current_page: int,
        total_pages: int,
        endpoint: str,
        USE_DISPLAY_VALUE: Optional[bool] = True,
        **kwargs
    ) -> list[dict]:
    bar = list()

    def add_item(page: int, display_value: Optional[str] = None) -> None:
        bar.append({
            'page': display_value if\
                display_value and USE_DISPLAY_VALUE else page,
            'url': url_for(endpoint, page = page, **kwargs)
        })

    if current_page > 1:
        if current_page - 1 > PAGINATION_DEPTH:
            add_item(1, '<<')

        add_item(current_page - 1, '<')

        # Count pages backwards.
        for index, page in enumerate(
            range(
                max(current_page - PAGINATION_DEPTH, 1),
                current_page
            )
        ):
            add_item(page)

    add_item(current_page)

    if current_page < total_pages:
        # Now forwards.
        for index, page in enumerate(range(current_page + 1, total_pages + 1)):
            if index == PAGINATION_DEPTH:
                break

            add_item(page)

        add_item(current_page + 1, '>')

        if current_page < total_pages - floor(PAGINATION_DEPTH):
            add_item(total_pages, '>>')

    return bar

def flash_errors(form: FlaskForm) -> None:
    for field in form.errors.values():
        for error in field:
            flash(error)
            log_anon_activity(logger.error, f'Received error: {error}')

def get_ip() -> str:
    """ Returns request IP address. """
    return request.headers.get('X-Forwarded-For') or\
    request.headers.get('X-Real-IP') or\
    request.remote_addr

def get_username() -> str:
    """ Returns request username. """
    return str(current_user.id) if current_user.is_authenticated else None

def log_anon_activity(log_fn: LoggerCallable, message: str) -> None:
    """
    Wrapper function for a logging method that
    signals an anonymous user's action.
    """
    log_fn(f'{get_ip()}: {message}')

def log_user_activity(log_fn: LoggerCallable, message: str) -> None:
    """
    Wrapper function for a logging method that
    signals a logged in user's action.
    """
    log_fn(f'{get_ip()} [{get_username()}]: {message}')
