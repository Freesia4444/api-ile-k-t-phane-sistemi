from dataclasses import dataclass, field
from typing import List
from pydantic import BaseModel, Field, ValidationError


class Book:
   
    def __init__(self, title: str, author: str, isbn: str):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.is_borrowed = False

    def borrow_book(self):
        
        if not self.is_borrowed:
            self.is_borrowed = True
        else:
           
            raise ValueError(f"'{self.title}' ODUNC alindi")

    def return_book(self):
      
        if self.is_borrowed:
            self.is_borrowed = False
        else:
            raise ValueError(f"'{self.title}' odunc alýnmadi.")

    def display_info(self) -> str:
        return f"'{self.title}' yazarý {self.author}"


class EBook(Book):
    
    def __init__(self, title: str, author: str, isbn: str, file_format: str):
        super().__init__(title, author, isbn)
        self.file_format = file_format

    def display_info(self) -> str:
        return f"{super().display_info()} [Formatý: {self.file_format}]"


class AudioBook(Book):
    
    def __init__(self, title: str, author: str, isbn: str, duration_in_minutes: int):
        super().__init__(title, author, isbn)
        self.duration = duration_in_minutes

    def display_info(self) -> str:
        return f"{super().display_info()} [süre: {self.duration} dakika]"


class Library:
    
    def __init__(self, name: str):
        self.name = name
        
        self._books = []

    def add_book(self, book: Book):
        self._books.append(book)

    def find_book(self, title: str) -> Book | None:
        for book in self._books:
            if book.title.lower() == title.lower():
                return book
        return None

    @property
    def total_books(self) -> int:
        return len(self._books)


@dataclass
class Member:
   
    name: str
    member_id: int
    borrowed_books: List[Book] = field(default_factory=list)


class PydanticBook(BaseModel):
    
    title: str
    author: str
    isbn: str = Field(..., min_length=10, max_length=13)
    publication_year: int = Field(..., gt=1400)  


