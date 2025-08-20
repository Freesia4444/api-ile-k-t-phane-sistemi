
import asyncio
from enum import IntEnum
from typing import Annotated
import logging
from contextlib import asynccontextmanager
from fastapi import (
    FastAPI,
    Body,
    Query,
    Path,
    Security,
    Depends,
    HTTPException,
    BackgroundTasks,
    status,
    Request
)
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


limiter = Limiter(key_func=get_remote_address)


books_db = []
book_id_counter = 1

@asynccontextmanager
async def lifespan(app: FastAPI):
   
    
    logger.info("FastAPI basliyo.")

    
    sample_books = [
        {"id": 1, "title": "The Hobbit", "author": "J.R.R. Tolkien", "publication_year": 1937},
        {"id": 2, "title": "1984", "author": "George Orwell", "publication_year": 1949},
        {"id": 3, "title": "Dune", "author": "Frank Herbert", "publication_year": 1965}
    ]

    books_db.extend(sample_books)
    global book_id_counter
    book_id_counter = 4

    logger.info(f"yuklendi {len(sample_books)} ")

    yield  

    
    logger.info("FastAPI kapatidi")


app = FastAPI(
    title="Library Management API",
    description="fastapi uygulamasý",
    version="1.0.0",
    lifespan=lifespan
)


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

class Book(BaseModel):
    
    title: str = Field(..., min_length=3, description="kitap baþlýðý")
    author: str
    publication_year: int | None = Field(default=None, gt=1400)

class BookCreate(BaseModel):
    
    title: str = Field(..., min_length=3)
    author: str
    publication_year: int | None = Field(default=None, gt=1400)

class BookResponse(BaseModel):
    
    id: int
    title: str
    author: str
    publication_year: int | None = None

class HTTPStatusCodes(IntEnum):
   
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    UNPROCESSABLE_ENTITY = 422


API_KEY = "SECRET_API_KEY_12345"
API_KEY_NAME = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="onaylanmadi"
        )
async def slow_db_call():
    
    await asyncio.sleep(1)  
    return {"status": "done"}
def write_notification(email: str, message=""):
   
    try:
        with open("log.txt", mode="a") as email_file:
            content = f"bildirim {email}: {message}\n"
            email_file.write(content)
        logger.info(f"bildirim yazýldý {email}")
    except Exception as e:
        logger.error(f"baþarýýz bildirim: {e}")

@app.get("/")
async def root():
    
    return {"message": "FastAPI Library Management System"}

@app.get("/health")
async def health_check():
   
    return {"status": "healthy", "timestamp": "2025-07-30"}


@app.get("/slow-endpoint")
async def handle_slow_request():
    
    logger.info("Ýstek alýndý.")
    result = await slow_db_call()
    logger.info("Yavaþ iþlem tamamland")
    return result

@app.post("/books/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate):
    
    global book_id_counter

    new_book = BookResponse(
        id=book_id_counter,
        title=book.title,
        author=book.author,
        publication_year=book.publication_year
    )

    books_db.append(new_book.model_dump())
    book_id_counter += 1

    logger.info(f"yeni kitap: {new_book.title}")
    return new_book

@app.get("/books/", response_model=list[BookResponse])
async def list_books(
    skip: Annotated[int, Query(description="atlanan kitaop", ge=0)] = 0,
    limit: Annotated[int, Query(description="kitap sayýsý", ge=1, le=100)] = 10
):
    
    return books_db[skip:skip + limit]

@app.get("/books/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: Annotated[int, Path(title="Book ID", ge=1)]
):
    
    for book in books_db:
        if book["id"] == book_id:
            return book

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"bu ýd ile  {book_id} yok"
    )

@app.put("/books/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: Annotated[int, Path(title="Kitap ID'si", ge=1)],
    book: Book,
    version: Annotated[int | None, Query(title="versiyon no", ge=1)] = None
):
    
    for i, existing_book in enumerate(books_db):
        if existing_book["id"] == book_id:
            updated_book = {
                "id": book_id,
                "title": book.title,
                "author": book.author,
                "publication_year": book.publication_year
            }
            books_db[i] = updated_book

            logger.info(f"Updated book {book_id}, version: {version}")
            return updated_book

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{book_id} bulunmuyoki"
    )

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: Annotated[int, Path(title="Book ID", ge=1)]
):
    
    for i, book in enumerate(books_db):
        if book["id"] == book_id:
            deleted_book = books_db.pop(i)
            logger.info(f"silinen kitap: {deleted_book['title']}")
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f" {book_id} bulunmadý"
    )


@app.get("/secure")
async def secure_endpoint(api_key: str = Depends(get_api_key)):
   
    return {"message":" API anahtari geçerlidi"}

@app.get("/secure/books", response_model=list[BookResponse])
async def secure_list_books(api_key: str = Depends(get_api_key)):
    
    return books_db

@app.post("/send-notification/{email}")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks,
    message: str = "kitap bildiimi"
):
    

    background_tasks.add_task(write_notification, email, message=message)
    return {"message": "bildirim yazildi"}


@app.get("/limited")
@limiter.limit("5/minute")
async def limited_endpoint(request: Request):
   
    return {"message": " endpoint dakikada maksimum 5 istek alir."}

@app.get("/limited-strict")
@limiter.limit("2/minute")
async def strict_limited_endpoint(request: Request):
    
    return {"message": "endpoint dakikada maksimum 2 istek kabul etti."}

@app.get("/limited-books")
@limiter.limit("10/minute")
async def rate_limited_books(request: Request):
    
    return {
        "message": "enpoint rate i ",
        "total_books": len(books_db),
        "books": books_db[:5]  
    }


@app.get("/api/v1/books", response_model=list[BookResponse])
async def list_books_v1():
    
    return books_db

@app.get("/api/v2/books")
async def list_books_v2():
    
    return {
        "version": "2.0",
        "total_books": len(books_db),
        "books": books_db
    }


@app.get("/error-demo")
async def error_demo():
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="demo erroru"
    )

if __name__ == "__main__":
    import uvicorn

    
    uvicorn.run(
        "fastapi_main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
