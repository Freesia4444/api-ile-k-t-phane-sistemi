

import json
import httpx
import sys
import os
from typing import List, Optional

class Book:
    
    def __init__(self, title: str, author: str, isbn: str):
        self.title = title
        self.author = author
        self.isbn = isbn
    
    def __str__(self) -> str:
       
        return f"{self.title} yazarı {self.author} (ISBN: {self.isbn})"
    
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
            print(f" {self.filename} bulunamadı. Yeni dosya oluşturaca.")
            self.books = []
        except json.JSONDecodeError:
            print(f"{self.filename} geçersiz JSON formatında. Yeni dosya oluşturulacak.")
            self.books = []
        except Exception as e:
            print(f" Dosya yüklenirken hata: {e}")
            self.books = []
    
    def save_books(self) -> None:
        
        try:
            with open(self.filename, 'w', encoding='utf-8') as file:
                books_data = [book.to_dict() for book in self.books]
                json.dump(books_data, file, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f" Dosya kaydedilirken hata: {e}")

    def add_book_by_isbn(self, isbn: str) -> bool:
       
        try:
            
            url = f"https://openlibrary.org/isbn/{isbn}.json"
            response = httpx.get(url, timeout=10)
            
            if response.status_code == 404:
                print("❌ Kitap bulunamadı. API'de böyle bir ISBN yok.")
                return False
            
            response.raise_for_status()
            data = response.json()
            
            
            title = data.get('title', 'Bilinmeyen Başlık')
            
           
            authors = []
            if 'authors' in data:
                for author_data in data['authors']:
                    if 'key' in author_data:
                        
                        author_key = author_data['key']
                        author_url = f"https://openlibrary.org{author_key}.json"
                        author_response = httpx.get(author_url, timeout=10)
                        if author_response.status_code == 200:
                            author_info = author_response.json()
                            author_name = author_info.get('name', 'Bilinmeyen Yazar')
                            authors.append(author_name)
            
            author = ', '.join(authors) if authors else 'Bilinmeyen Yazar'
            
           
            book = Book(title, author, isbn)
            self.add_book(book)
            print(f" API'den kitap eklendi: {book}")
            return True
            
        except httpx.TimeoutException:
            print(" API isteği zaman aşımına uğradı.")
            return False
        except httpx.RequestError as e:
            print(f" İnternet bağlantı hatası: {e}")
            return False
        except httpx.HTTPStatusError as e:
            print(f" API hatası: {e.response.status_code}")
            return False
        except Exception as e:
            print(f" Beklenmeyen hata: {e}")
            return False

def clear_screen():
    
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
   
    print("\n" + "="*50)
    print(" KÜTÜPHANе YÖNETIM SISTEM")
    print("="*50)
    print("1. Kitap Ekle (ISBN ile - APi)")
    print("2. Kitap Ekle (Manuel)")
    print("3 Kitap Sil")
    print("4. Kitapları Listele")
    print("5 Kitap Ara")
    print("6. Çıkış")
    print("="*50)

def add_book_api_menu(library: Library):
    
    print("\n-- API İLE KITAP EKLEME ---")
    
    isbn = input("Kitabın ISBN numarasını girin: ").strip()
    
    if not isbn:
        print(" ISBN boş olamaz ki")
        input("Devam etmek için Enter tuşuna bas.")
        return
    
    print(" API'den kitap bilgileri alın.")
    success = library.add_book_by_isbn(isbn)
    
    if not success:
        print("Manuel olarak kitap bilgilerini girebilirsiniz.")
        choice = input("Manuel girişe geçmek ister sen (e/h): ").strip().lower()
        if choice == 'e':
            add_book_manual_with_isbn(library, isbn)
    
    input("Devam etmek için Enter tuşuna bas")

def add_book_manual_with_isbn(library: Library, isbn: str):
   
    print("\n- MANUEL KITAP EKLEME ---")
    
    title = input("Kitap başlığı: ").strip()
    author = input("Yazar adı: ").strip()
    
    if not title or not author:
        print(" Başlık ve yazar adı boş olamazzzz")
        return
    
    try:
        book = Book(title, author, isbn)
        library.add_book(book)
        print(f"Kitap başarıyla eklendi: {book}")
    except ValueError as e:
        print(f" Hata: {e}")
    except Exception as e:
        print(f" Beklenmeyen hata: {e}")

def add_book_manual_menu(library: Library):
    
    print("\n--- MANUEL KITAP EKLEME --")
    
    isbn = input("Kitabın ISBN numarasını girin: ").strip()
    title = input("Kitap başlığı: ").strip()
    author = input("Yazar adı: ").strip()
    
    if not isbn or not title or not author:
        print(" Tüm alanlar doldurulmalı!")
        input("Devam etmek için Enter tuşuna bas")
        return
    
    try:
        book = Book(title, author, isbn)
        library.add_book(book)
        print(f"Kitap başarıyla eklendi: {book}")
    except ValueError as e:
        print(f" Hata: {e}")
    except Exception as e:
        print(f" Beklenmeyen hata: {e}")
    
    input("Devam etmek için Enter tuşuna bas.")

def remove_book_menu(library: Library):
    
    print("\n--- KITAP SILME ")
    
    isbn = input("Silinecek kitabın ISBN numarasını girin: ").strip()
    
    if not isbn:
        print("ISBN boş olamaz!")
        input("Devam etmek için Enter tuşuna bas")
        return
    
    try:
        book = library.find_book(isbn)
        if book:
            print(f"Silinecek kitap: {book}")
            confirm = input("Bu kitabı silmek istediğinizden emin misiniz? (e/h): ").strip().lower()
            
            if confirm == 'e':
                if library.remove_book(isbn):
                    print("Kitap başarıyla silindi!")
                else:
                    print("Kitap silinemedi!")
            else:
                print("Silme işlemi iptal edildi.")
        else:
            print(" Belirtilen ISBN ile kitap bulunamadı!")
    
    except Exception as e:
        print(f"Hata: {e}")
    
    input("Devam etmek için Enter tuşuna basın...")

def list_books_menu(library: Library):
    
    print("\n--- KÜTÜPHANE KİTAP LİSTESİ --")
    
    books = library.list_books()
    
    if not books:
        print("Kütüphanede henüz kitap bulunmamaktadır.")
    else:
        print(f"Toplam {len(books)} kitap bulunmaktadır:")
        for i, book in enumerate(books, 1):
            print(f"{i:2d}. {book}")
    
    input("Devam etmek için Enter tuşuna bas.")

def search_book_menu(library: Library):
    
    print("--- KITAP ARAMA ---")
    
    isbn = input("Aranacak kitabın ISBN numarasını gir ").strip()
    
    if not isbn:
        print(" ISBN boş olamaz!")
        input("Devam etmek için Enter tuşuna bas.")
        return
    
    try:
        book = library.find_book(isbn)
        if book:
            print(f"\n Kitap bulundu: {book}")
        else:
            print(" Belirtilen ISBN ile kitap bulunamadı")
    
    except Exception as e:
        print(f" Hata: {e}")
    
    input("Devam etmek için Enter tuşuna bas")

def main():
    
    print("Kütüphane Yönetim Sistemi başlatılıy")
    
    
    try:
        library = Library("library.json")
        print("Kütüphane verileri yüklendi.")
    except Exception as e:
        print(f"Veri yükleme hatası: {e}")
        print("Yeni bir kütüphane oluşturulacak.")
        library = Library("library.json")
    
    while True:
        try:
            clear_screen()
            show_menu()
            
            choice = input("Seçiminizi yapın (1-6): ").strip()
            
            if choice == "1":
                add_book_api_menu(library)
            elif choice == "2":
                add_book_manual_menu(library)
            elif choice == "3":
                remove_book_menu(library)
            elif choice == "4":
                list_books_menu(library)
            elif choice == "5":
                search_book_menu(library)
            elif choice == "6":
                print("\n Kütüphane Yönetim Sistemi kapatılıyor...")
                print("Verileriniz kaydedi.")
                sys.exit(0)
            else:
                print("\nGeçersiz seçim! Lütfen 1-6 arasında bir sayı girin.")
                input("Devam etmek için Enter tuşuna bas..")
        
        except KeyboardInterrupt:
            print("\n\n Program Ctrl+C ile sonlandırılıyor...")
            print("Veri kaydedildi")
            sys.exit(0)
        except Exception as e:
            print(f"\n Beklenmeyen hata: {e}")
            input("Devam etmek için Enter tuşuna bas")

if __name__ == "__main__":
    main()