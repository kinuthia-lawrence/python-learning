from fastapi import FastAPI, HTTPException
from app.models.book import Book
from app.services.book_service import get_book_by_id, get_all_books


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/health")
def read_health():
    return {"status": "healthy"}



@app.get("/books", response_model=list[Book])
def read_books():
    return get_all_books()

@app.get("/books", response_model=list[Book])
def read_books(limit: int = 10):
    return get_all_books()[:limit]


@app.get("/books/{book_id}", response_model=Book)
def read_book(book_id: int):
    book = get_book_by_id(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book