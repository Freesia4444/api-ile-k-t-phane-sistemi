📚 Kütüphane Yönetim Sistemi

Bu proje, Python ve FastAPI kullanılarak geliştirilmiş modern bir kütüphane yönetim sistemidir.
Proje hem konsol uygulaması hem de web API olarak çalışabilir.

🚀 Özellikler

Kitap ekleme (ISBN ile otomatik veri çekme - Open Library API)

Kitap arama ve listeleme

Kitap silme (ISBN ile)

JSON dosyasında kalıcı veri saklama

Web API üzerinden kitap yönetimi

Testler ile güvenli geliştirme

🛠️ Gereksinimler

Python 3.9+

İnternet bağlantısı (ISBN API entegrasyonu için)

📥 Kurulum
1️⃣ Projeyi Klonlayın
git clone <repo-link>
cd kutuphane-yonetim-sistemi

2️⃣ Sanal Ortam Oluşturma
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

3️⃣ Gerekli Paketleri Yükleyin
pip install -r requirements.txt

🖥️ Konsol Uygulaması Kullanımı

Klasik kütüphane yönetim uygulamasını çalıştırmak için:

python main.py

Menü Seçenekleri:

Kitap Ekle (ISBN ile) - Open Library API'sinden otomatik veri çekme

Kitap Ekle (Manuel) - Manuel kitap bilgisi girme

Kitap Sil - ISBN ile kitap silme

Kitapları Listele - Tüm kitapları görüntüleme

Kitap Ara - ISBN ile kitap arama

Çıkış - Uygulamadan çıkış

🌐 API Endpoints
HTTP Metodu	Endpoint	Açıklama
GET	/	Ana sayfa ve sistem bilgileri
GET	/health	Sistem sağlık durumu
GET	/books	Tüm kitapları listele
POST	/books	ISBN ile yeni kitap ekle
GET	/books/{isbn}	Belirli ISBN ile kitap getir
DELETE	/books/{isbn}	Belirli ISBN ile kitap sil
GET	/stats	Kütüphane istatistikleri
🧪 Testler

Tüm testleri çalıştırmak için:

pytest


Detaylı test çıktısı için:

pytest -v


Belirli bir test dosyasını çalıştırmak için:

pytest test_api.py -v

⚙️ Kullanılan Teknolojiler

Python

FastAPI - Modern, hızlı web framework

httpx - Async HTTP client (Open Library API için)

pytest - Test framework

🧱 Programlama Prensipleri

OOP (Object-Oriented Programming) – Book ve Library sınıfları

Error Handling – Kapsamlı hata yönetimi

Data Persistence – JSON dosyasında veri saklama

Async Programming – API çağrıları için async/await

Test-Driven Development – Kapsamlı unit testler

📦 Veri Modeli
Book Sınıfı
class Book:
    def __init__(self, title: str, author: str, isbn: str):
        self.title = title
        self.author = author
        self.isbn = isbn

API Response Modeli
from pydantic import BaseModel

class BookResponse(BaseModel):
    title: str
    author: str
    isbn: str

❗ Hata Yönetimi

Network Hataları: İnternet bağlantısı problemleri

API Hataları: Open Library API'sinden 404/500 hataları

Veri Hataları: Geçersiz JSON, eksik alanlar

İş Mantığı Hataları: Duplicate ISBN, bulunamayan kitap

Dosya Hataları: library.json okuma/yazma hataları

📖 Lisans

Bu proje eğitim ve öğrenme amaçlı geliştirilmiştir.
Geliştirme sürecinde zaman zaman yapay zekadan destek alınmış, ancak proje  tarafımca hazırlanmıştır.
