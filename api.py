from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
import httpx
import json
import os
from contextlib import asynccontextmanager
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BookResponse(BaseModel):
    
    title: str
    author: str
    isbn: str
    
    class Config:
        from_attributes = True

class BookCreate(BaseModel):
    
    isbn: str = Field(..., min_length=10, max_length=17, description="ISBN numarasi")

class ErrorResponse(BaseModel):
    
    detail: str


class Book:
    
    
    def __init__(self, title: str, author: str, isbn: str):
        self.title = title
        self.author = author
        self.isbn = isbn
    
    def __str__(self) -> str:
        
        return f"{self.title} yazari {self.author} (ISBN: {self.isbn})"
    
    def to_dict(self) -> dict:
        
        return {
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        
        return cls(data["title"], data["author"], data["isbn"])


class Library:
    
    def __init__(self, filename: str = "library.json"):
        self.filename = filename
        self.books: List[Book] = []
        self.load_books()
    
    def add_book(self, book: Book) -> None:
        
        if self.find_book(book.isbn):
            raise ValueError(f"ISBN {book.isbn} zaten var")
        
        self.books.append(book)
        self.save_books()
    
    def remove_book(self, isbn: str) -> bool:
        
        for i, book in enumerate(self.books):
            if book.isbn == isbn:
                self.books.pop(i)
                self.save_books()
                return True
        return False
    
    def list_books(self) -> List[Book]:
        
        return self.books.copy()
    
    def find_book(self, isbn: str) -> Optional[Book]:
        
        for book in self.books:
            if book.isbn == isbn:
                return book
        return None
    
    def load_books(self) -> None:
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.books = [Book.from_dict(book_data) for book_data in data]
        except FileNotFoundError:
            logger.info(f"{self.filename} bulunamadi Yeni dosya oluşturalim.")
            self.books = []
        except json.JSONDecodeError:
            logger.warning(f"{self.filename} geçersiz JSON formatında Yeni dosya oluşturulim")
            self.books = []
        except Exception as e:
            logger.error(f"Dosya yüklenirken hata: {e}")
            self.books = []
    
    def save_books(self) -> None:
        
        try:
            with open(self.filename, 'w', encoding='utf-8') as file:
                books_data = [book.to_dict() for book in self.books]
                json.dump(books_data, file, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Dosya kaydedilirkenki hatası {e}")
            raise

    async def add_book_by_isbn(self, isbn: str) -> Book:
        
        try:
            
            url = f"https://openlibrary.org/isbn/{isbn}.json"
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                
                if response.status_code == 404:
                    raise ValueError("Kitap yok api'de böyle bir ISBN yok.")
                
                response.raise_for_status()
                data = response.json()
                
               
                title = data.get('title', 'Bilinmeyen Başlık')
                
               
                authors = []
                if 'authors' in data:
                    for author_data in data['authors']:
                        if 'key' in author_data:
                            
                            author_key = author_data['key']
                            author_url = f"https://openlibrary.org{author_key}.json"
                            author_response = await client.get(author_url, timeout=10)
                            if author_response.status_code == 200:
                                author_info = author_response.json()
                                author_name = author_info.get('name', 'Bilinmeyen Yazar')
                                authors.append(author_name)
                
                author = ', '.join(authors) if authors else 'Bilinmeyen Yazar'
                
                
                book = Book(title, author, isbn)
                self.add_book(book)
                return book
                
        except httpx.TimeoutException:
            raise ValueError("API isteki zaman aşımı uğradi.")
        except httpx.RequestError as e:
            raise ValueError(f"İnternet bağlantı hatası: {e}")
        except httpx.HTTPStatusError as e:
            raise ValueError(f"API hatasi: {e.response.status_code}")
        except ValueError:
            raise  
        except Exception as e:
            raise ValueError(f"beklenmeyen hata: {e}")


library = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    global library
    logger.info("FastAPI Library Management System başlatıl")
    
    library = Library("library.json")
    logger.info(f"Kütüphane yüklendi Toplam {len(library.books)} kitap ")
    
    yield  
    logger.info("FastAPI Library Management System kapatıldi")


app = FastAPI(
    title="Library Management API",
    description="kütüphane yönetim sistem için FastAPI  web servis",
    version="1.0.0",
    lifespan=lifespan
)



@app.get("/")
async def root():
    
    return {
        "message": "Kütüphane Yönetim Sistemi API'si",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    
    return {
        "status": "healthy",
        "total_books": len(library.books) if library else 0
    }

@app.get("/books", response_model=List[BookResponse])
async def get_all_books():
    
    try:
        books = library.list_books()
        return [BookResponse(**book.to_dict()) for book in books]
    except Exception as e:
        logger.error(f"Kitapları listelerkenki hata: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kitaplar listelenirken hata "
        )

@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def add_book_by_isbn(book_data: BookCreate):
    
    try:
        
        isbn = book_data.isbn.strip().replace("-", "").replace(" ", "")
        
        if not isbn:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ISBN boş olamazki"
            )
        
       
        book = await library.add_book_by_isbn(isbn)
        
        logger.info(f"Yeni kitap eklendik: {book.title}")
        return BookResponse(**book.to_dict())
        
    except ValueError as e:
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"kitap eklenirken beklenmeyen hata oldu  {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="kitap eklenirken bir hata oluştu"
        )

@app.delete("/books/{isbn}", status_code=status.HTTP_200_OK)
async def delete_book(isbn: str):
    
    try:
        
        isbn = isbn.strip().replace("-", "").replace(" ", "")
        
        
        book = library.find_book(isbn)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ISBN {isbn} ile kitap bulunamadı"
            )
        
        
        success = library.remove_book(isbn)
        
        if success:
            logger.info(f"kitap silindi: {book.title}")
            return {
                "message": "Kitap başarıyla silindi",
                "deleted_book": BookResponse(**book.to_dict())
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Kitap silinemedi"
            )
            
    except HTTPException:
        raise  
    except Exception as e:
        logger.error(f"Kitap silinirken hata: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kitap silinirken bir hata oluştu"
        )

@app.get("/books/{isbn}", response_model=BookResponse)
async def get_book_by_isbn(isbn: str):
   
    try:
       
        isbn = isbn.strip().replace("-", "").replace(" ", "")
        
        book = library.find_book(isbn)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ISBN {isbn} ile kitap bulunamadı"
            )
        
        return BookResponse(**book.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Kitap aranırken hata: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kitap aranırken bir hata oluştu"
        )

@app.get("/stats")
async def get_library_stats():
   
    try:
        books = library.list_books()
        authors = set(book.author for book in books)
        
        return {
            "total_books": len(books),
            "total_authors": len(authors),
            "books_by_author": {author: sum(1 for book in books if book.author == author) 
                              for author in authors}
        }
    except Exception as e:
        logger.error(f"istatistikler alınırken hata: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="istatistikler alınırken bir hata oluştu"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)