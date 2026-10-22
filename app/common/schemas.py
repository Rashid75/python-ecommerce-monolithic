"""Shapes shared by more than one module."""

from pydantic import BaseModel


class Page[T](BaseModel):
    """One page of results, plus what the client needs to ask for the next.

    `Page[T]` means "a page of some type T". Write `Page[ProductRead]` or
    `Page[CategoryRead]` and `items` becomes a list of that type. One
    definition instead of a near-identical copy in every module.
    """

    items: list[T]
    # How many match the filters in total, not how many are in items.
    total: int
    limit: int
    offset: int
