
from pydantic import BaseModel, Field


class Book(BaseModel):
    id: int = Field(gt=0)
    author: str
    title: str
    description: str
    thumbnail_url: str