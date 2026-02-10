from typing import Literal, TypeVar

from sqlalchemy import Select, inspect

T = TypeVar('T')

class SortableMixin:
    @classmethod
    def get_sortable_columns(cls) -> tuple[str]:
        return ( c.key for c in inspect(cls).mapper.column_attrs )

    @classmethod
    def apply_sort(cls, stmt: Select[T], key: str, direction: Literal['asc', 'desc']) -> Select[T]:
        valid_columns = cls.get_sortable_columns()

        if key not in valid_columns:
            key = 'id'

        column = getattr(cls, key)
        sort_method = getattr(column, direction)

        return stmt.order_by(sort_method())
