from app.models.book import Book

books = [
        Book(
            id=1,
            author="George Orwell",
            title="1984",
            description="A dystopian novel set in a totalitarian society.",
            thumbnail_url="https://example.com/thumbnails/1984.jpg"
        ),
        Book(
            id=2,
            author="Harper Lee",
            title="To Kill a Mockingbird",
            description="A novel about racial injustice in the Deep South.",
            thumbnail_url="https://example.com/thumbnails/mockingbird.jpg"
        ),
        Book(
            id=3,
            author="J.R.R. Tolkien",
            title="The Hobbit",
            description="A fantasy novel about the adventures of Bilbo Baggins.",
            thumbnail_url="https://example.com/thumbnails/hobbit.jpg"
        )
]

def get_book_by_id(book_id: int) -> Book | None:
    return next((book for book in books if book.id == book_id), None)

def get_all_books() -> list[Book]:
    return books