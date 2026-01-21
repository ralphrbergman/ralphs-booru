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
    element,
    extra_fn: Optional[Callable[[Select[T]], Select[T]]] = None,
    direction: Optional[Literal['asc', 'desc']] = DEFAULT_SORT_DIR,
    limit: Optional[int] = DEFAULT_LIMIT,
    page: Optional[int] = 1,
    sort: Optional[str] = DEFAULT_SORT
    ) -> SelectPagination:
    """
    Selects given element and creates a pagination for it.
    Allows to implement further selection by extra_fn parameter.

    Args:
        element: Database element to select
        extra_fn: Function that receives statement for additional selecting
        limit: How many elements to show per page
        page: Page number
        sort_str: Sort direction, default is descending ('desc')

    Returns:
        SelectPagination: Pagination object
    """
    if limit and limit > LIMIT_THRESHOLD:
        limit = LIMIT_THRESHOLD

    column = getattr(element, sort)

    if not column:
        column = getattr(element, DEFAULT_SORT)

    stmt = select(element).order_by(
        getattr(column, direction)()
    )

    if extra_fn:
        stmt = extra_fn(stmt)

    elements = db.paginate(
        stmt,
        page = page,
        per_page = limit
    )

    return elements
