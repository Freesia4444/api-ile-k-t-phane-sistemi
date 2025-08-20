import pytest
import json
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import httpx


from api import app, Library, Book


client = TestClient(app)


TEST_LIBRARY_FILE = "test_library.json"

@pytest.fixture(autouse=True)
def setup_and_teardown():
    if os.path.exists(TEST_LIBRARY_FILE):
        os.remove(TEST_LIBRARY_FILE)
    
    yield 
    
   
    if os.path.exists(TEST_LIBRARY_FILE):
        os.remove(TEST_LIBRARY_FILE)

@pytest.fixture
def sample_library():
    library = Library(TEST_LIBRARY_FILE)
    book1 = Book("Test Kitap 1", "Test Yazar 1", "1234567890")
    book2 = Book("Test Kitap 2", "Test Yazar 2", "0987654321")
    library.add_book(book1)
    library.add_book(book2)
    return library

class TestAPIEndpoints:
    def test_root_endpoint(self):
        
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data
        assert "version" in data

    def test_health_check(self):
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "total_books" in data

    def test_get_all_books_empty(self):
       
        response = client.get("/books")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @patch('api.library')
    def test_get_all_books_with_data(self, mock_library):
       
        
        mock_books = [
            Book("Test Kitap", "Test Yazar", "1234567890")
        ]
        mock_library.list_books.return_value = mock_books
        
        response = client.get("/books")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Test Kitap"
        assert data[0]["author"] == "Test Yazar"
        assert data[0]["isbn"] == "1234567890"

    @pytest.mark.asyncio
    async def test_add_book_success(self):
        
        mock_response_data = {
            "title": "The Great Gatsby",
            "authors": [{"key": "/authors/OL26783A"}]
        }
        
        mock_author_data = {
            "name": "F. Scott Fitzgerald"
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            
            mock_response1 = AsyncMock()
            mock_response1.status_code = 200
            mock_response1.json.return_value = mock_response_data
            mock_response1.raise_for_status.return_value = None
            
          
            mock_response2 = AsyncMock()
            mock_response2.status_code = 200
            mock_response2.json.return_value = mock_author_data
            
            mock_instance.get.side_effect = [mock_response1, mock_response2]
            
            response = client.post("/books", json={"isbn": "9780743273565"})
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "The Great Gatsby"
            assert data["author"] == "F. Scott Fitzgerald"

    def test_add_book_invalid_isbn(self):
        
        response = client.post("/books", json={"isbn": ""})
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_add_book_api_not_found(self):
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            mock_response = AsyncMock()
            mock_response.status_code = 404
            mock_instance.get.return_value = mock_response
            
            response = client.post("/books", json={"isbn": "9999999999"})
            assert response.status_code == 400

    @patch('api.library')
    def test_get_book_by_isbn_success(self, mock_library):
        
        mock_book = Book("Test Kitap", "Test Yazar", "1234567890")
        mock_library.find_book.return_value = mock_book
        
        response = client.get("/books/1234567890")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Kitap"
        assert data["isbn"] == "1234567890"

    @patch('api.library')
    def test_get_book_by_isbn_not_found(self, mock_library):
      
        mock_library.find_book.return_value = None
        
        response = client.get("/books/9999999999")
        assert response.status_code == 404

    @patch('api.library')
    def test_delete_book_success(self, mock_library):
      
        mock_book = Book("Test Kitap", "Test Yazar", "1234567890")
        mock_library.find_book.return_value = mock_book
        mock_library.remove_book.return_value = True
        
        response = client.delete("/books/1234567890")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "deleted_book" in data
        assert data["deleted_book"]["title"] == "Test Kitap"

    @patch('api.library')
    def test_delete_book_not_found(self, mock_library):
        
        mock_library.find_book.return_value = None
        
        response = client.delete("/books/9999999999")
        assert response.status_code == 404

    @patch('api.library')
    def test_get_stats(self, mock_library):
        
        mock_books = [
            Book("Kitap 1", "Yazar A", "1111111111"),
            Book("Kitap 2", "Yazar A", "2222222222"),
            Book("Kitap 3", "Yazar B", "3333333333")
        ]
        mock_library.list_books.return_value = mock_books
        
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_books"] == 3
        assert data["total_authors"] == 2
        assert "books_by_author" in data


class TestLibraryClass:
    
    
    def test_library_initialization(self):
        
        library = Library(TEST_LIBRARY_FILE)
        assert library.filename == TEST_LIBRARY_FILE
        assert isinstance(library.books, list)

    def test_add_book(self):
       
        library = Library(TEST_LIBRARY_FILE)
        book = Book("Test Kitap", "Test Yazar", "1234567890")
        
        library.add_book(book)
        assert len(library.books) == 1
        assert library.books[0].title == "Test Kitap"

    def test_add_duplicate_isbn(self):
       
        library = Library(TEST_LIBRARY_FILE)
        book1 = Book("Kitap 1", "Yazar 1", "1234567890")
        book2 = Book("Kitap 2", "Yazar 2", "1234567890")  
        
        library.add_book(book1)
        
        with pytest.raises(ValueError):
            library.add_book(book2)

    def test_find_book(self):
        
        library = Library(TEST_LIBRARY_FILE)
        book = Book("Test Kitap", "Test Yazar", "1234567890")
        library.add_book(book)
        
        found_book = library.find_book("1234567890")
        assert found_book is not None
        assert found_book.title == "Test Kitap"
        
        not_found = library.find_book("9999999999")
        assert not_found is None

    def test_remove_book(self):
        
        library = Library(TEST_LIBRARY_FILE)
        book = Book("Test Kitap", "Test Yazar", "1234567890")
        library.add_book(book)
        
        assert len(library.books) == 1
        success = library.remove_book("1234567890")
        assert success is True
        assert len(library.books) == 0
        
       
        success = library.remove_book("9999999999")
        assert success is False

    def test_list_books(self):
        
        library = Library(TEST_LIBRARY_FILE)
        book1 = Book("Kitap 1", "Yazar 1", "1111111111")
        book2 = Book("Kitap 2", "Yazar 2", "2222222222")
        
        library.add_book(book1)
        library.add_book(book2)
        
        books = library.list_books()
        assert len(books) == 2
        assert isinstance(books, list)


class TestBookClass:
    
    def test_book_creation(self):
      
        book = Book("Test Kitap", "Test Yazar", "1234567890")
        assert book.title == "Test Kitap"
        assert book.author == "Test Yazar"
        assert book.isbn == "1234567890"

    def test_book_str_representation(self):
        
        book = Book("Test Kitap", "Test Yazar", "1234567890")
        expected = "Test Kitap by Test Yazar (ISBN: 1234567890)"
        assert str(book) == expected

    def test_book_to_dict(self):
       
        book = Book("Test Kitap", "Test Yazar", "1234567890")
        book_dict = book.to_dict()
        
        assert book_dict == {
            "title": "Test Kitap",
            "author": "Test Yazar",
            "isbn": "1234567890"
        }

    def test_book_from_dict(self):
        
        book_dict = {
            "title": "Test Kitap",
            "author": "Test Yazar", 
            "isbn": "1234567890"
        }
        
        book = Book.from_dict(book_dict)
        assert book.title == "Test Kitap"
        assert book.author == "Test Yazar"
        assert book.isbn == "1234567890"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
