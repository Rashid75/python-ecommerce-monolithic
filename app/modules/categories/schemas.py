"""What the categories API accepts and returns."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class CategoryUpdate(BaseModel):
    """Partial update. The only field there is, but still optional, so a
    PATCH with an empty body is valid and changes nothing."""

    name: str | None = Field(default=None, min_length=1, max_length=100)


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime
