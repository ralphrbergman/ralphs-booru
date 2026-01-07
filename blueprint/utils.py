from math import floor
from typing import Optional

from flask import flash, url_for
from flask_wtf import FlaskForm

PAGINATION_DEPTH = 5

def create_pagination_bar(current_page: int, total_pages: int, endpoint: str, USE_DISPLAY_VALUE: Optional[bool] = True, **kwargs) -> list[dict]:
    bar = list()

    def add_item(page: int, display_value: Optional[str] = None) -> None:
        bar.append({
            'page': display_value if display_value and USE_DISPLAY_VALUE else page,
            'url': url_for(endpoint, page = page, **kwargs)
        })

    if current_page > 1:
        if current_page - 1 > PAGINATION_DEPTH:
            add_item(1, '<<')

        add_item(current_page - 1, '<')

        # Count pages backwards.
        for index, page in enumerate(range(max(current_page - PAGINATION_DEPTH, 1), current_page)):
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
