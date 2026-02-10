from os import getenv
from typing import Callable, Literal, Optional, TypeVar

from flask_sqlalchemy.pagination import SelectPagination
from sqlalchemy import Select, select

from db import db

DEFAULT_LIMIT = 20
DEFAULT_SORT = 'id'
DEFAULT_SORT_DIR = 'desc'
LIMIT_THRESHOLD = 100

T = TypeVar('T')

def browse_element(
    element: T,
    extra_fn: Optional[Callable[[Select[T]], Select[T]]] = None,
    direction: Optional[Literal['asc', 'desc']] = DEFAULT_SORT_DIR,
    limit: Optional[int] = DEFAULT_LIMIT,
    page: Optional[int] = 1,
    sort: Optional[str] = DEFAULT_SORT,
    terms: Optional[str] = None
    ) -> SelectPagination:
    """
    Paginates element.

    Args:
        element: Element to select
        extra_fn: Function that receives statement for additional selecting
        direction: Sort direction, default is descending ('desc')
        Must be between 'desc' and 'asc' (ascending)
        limit: How many elements per page
        page: Page
        sort: What column to sort
        terms: Searching terms
    """
    if limit and limit > LIMIT_THRESHOLD:
        limit = LIMIT_THRESHOLD

    if direction not in ('asc', 'desc'):
        direction = DEFAULT_SORT_DIR

    stmt = element.apply_sort(select(element), sort, direction)

    if extra_fn:
        stmt = extra_fn(stmt)

    elements = db.paginate(
        stmt,
        page = page,
        per_page = limit
    )

    return elements
