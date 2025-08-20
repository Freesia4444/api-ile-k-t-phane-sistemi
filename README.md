Kütüphane Yönetim Sistemi
Bu proje, Python ve FastAPI kullanılarak gelistirilmis modern bir kutuphane yonetim sistemidir. Proje hem konsol uygulamasi hemde web API olarak calisabilir.
Ozellikler:

Kitap ekleme (ISBN ile otomatik veri cekme)

Kitap arama ve listeleme

Kitap silme

JSON dosyasinda kalici veri saklama


Gereksinimler:

Python 
internet

Projeyi klonlayinnn:

git clone <repository-url>
cd kutuphane-yonetim-sistemi


Sanal ortam olusturma:

python -m venv venv

venv\Scripts\activate    


Gerekli paketleri yüklen:

pip install -r requirements.txt


Kullanım:

Konsol Uygulaması:
Terminalde klasik kutuphane yonetim uygulamasini çalıştırmak icin:

python main.py


Menü Secenekleri:

Kitap Ekle (ISBN ile - API) - Open Library API'sinden otomatik veri cekme

Kitap Ekle (Manuel) - Manuel kitap bilgisi girme

Kitap Sil - ISBN ile kitap silme

Kitaplari Listele - Tum kitaplari goruntuleme

Kitap Ara - ISBN ile kitap arama

Cikis - Uygulamadan cikis


API Endpoints:

GET / - Ana sayfa ve sistem bilgileri

GET /health - Sistem saglik durumu

GET /books - Tum kitaplari listele

POST /books - ISBN ile yeni kitap ekle

GET /books/{isbn} - Belirli ISBN ile kitap getir

DELETE /books/{isbn} - Belirli ISBN ile kitap sil

GET /stats - Kutuphane istatistikleri


Test Etme:
Tum testleri calistir:

pytest


Detayli test ciktisi icin:

pytest -v




Belirli bir test dosyasini calistir:

pytest test_api.py -v







Ozellikler ve Teknolojiler:
Kullanilan Teknoloji

Python 

FastAPI - Modern, hizli web framework

httpx - Async HTTP client (Open Library API icin)

pytest - Test framework


Programlama Prensipleri:

Object-Oriented Programming (OOP) - Book ve Library siniflari



Error Handling - Kapsamli hata yonetimi

Data Persistence - JSON dosyasinda veri saklama

Async Programming - API cagriilari icin async/await

Test-Driven Development - Kapsamli unit testler



Hata yonetimi - Network ve API hatalar

Veri Modeli:
Book Sinifi:

class Book:
    def __init__(self, title: str, author: str, isbn: str):
        self.title = title   
        self.author = author  
        self.isbn = isbn     


API Response Modelleri:

class BookResponse(BaseModel):
    title: str
    author: str
    isbn: str


Hata Yönetimi:
uygun hata mesajlari nedeni

Network Hatalari: Internet baglantisi problemi

API Hatalari: Open Library API'sinden 404/500 hatalari

Veri Hatalari: Gecersiz JSON, eksik alanlar

Is Mantigi Hatalari: Duplicate ISBN, bulunamayan kitap

Dosya Hatalari: library.json okuma/yazma hatalari


Bu proje egitim amacli gelistirilmisdir ve fast api ve api yi python olraka ogrenirken yapay zekadan ayrdim alindi.



