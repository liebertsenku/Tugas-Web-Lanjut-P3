# 🚀 FastAPI Items API - Tugas Web Lanjutan

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

Repositori ini berisi implementasi RESTful API sederhana menggunakan **FastAPI**, **SQLAlchemy**, dan **SQLite** untuk memenuhi Tugas Individu 2 pada mata kuliah Pemrograman Web Lanjutan B.

##  Deskripsi Proyek
Proyek ini mengimplementasikan endpoint API untuk mengelola entitas `Item`. API ini dirancang dengan struktur yang bersih, menggunakan ORM untuk interaksi database, dan memastikan validasi input/output yang ketat.

### Fitur Utama
* **Create & Read Operations:** Mendukung penambahan data (POST) dan pengambilan data (GET).
* **ORM Integration:** Menggunakan SQLAlchemy untuk berinteraksi dengan database SQLite tanpa menulis query SQL manual.
* **Data Validation:** Memastikan tipe data yang masuk dan keluar sesuai standar menggunakan skema Pydantic.
* **Auto-generated Docs:** Menyediakan dokumentasi API interaktif secara otomatis menggunakan antarmuka Swagger UI.

##  Teknologi yang Digunakan
* [FastAPI](https://fastapi.tiangolo.com/) - Framework web modern dan cepat untuk membangun API dengan Python.
* [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit dan Object-Relational Mapping (ORM) untuk Python.
* [Pydantic](https://docs.pydantic.dev/) - Validasi data menggunakan *type hints* Python.
* [Uvicorn](https://www.uvicorn.org/) - ASGI web server untuk menjalankan aplikasi web Python.

##  Cara Menjalankan Proyek Secara Lokal

Ikuti langkah-langkah di bawah ini untuk menjalankan API ini di komputermu:

### 1. Clone Repositori
```bash
git clone [https://github.com/liebertsenku/tugas-web-lanjutan-2.git](https://github.com/liebertsenku/tugas-web-lanjutan-2.git)
cd tugas-web-lanjutan-2
```

### 2. Siapkan Virtual Environment (Direkomendasikan)
```bash
python -m venv venv

# Aktivasi di Windows:
venv\Scripts\activate

# Aktivasi di Mac/Linux:
source venv/bin/activate
```

### 3. Instal Dependensi
```bash
pip install fastapi[all] sqlalchemy
```

### 4. Jalankan Server Uvicorn
```bash
uvicorn main:app --reload
```

### 5. Akses Dokumentasi API
Buka browser dan kunjungi tautan berikut untuk membuka Swagger UI:
👉 **`http://127.0.0.1:8000/docs`**

---

## 📡 Daftar Endpoint API

Berikut adalah daftar endpoint yang tersedia dalam aplikasi ini:

| Method | Endpoint | Deskripsi | Respons |
| :--- | :--- | :--- | :--- |
| `POST` | `/items/` | Menambahkan item baru ke database. | Mengembalikan objek item yang baru dibuat. |
| `GET` | `/items/` | Mengambil daftar semua item. | Mengembalikan *array* berisi seluruh item. |
| `GET` | `/items/{item_id}`| Mengambil detail satu item berdasarkan ID. | Mengembalikan satu objek item spesifik atau error 404 jika tidak ditemukan. |

---

## 👨‍💻 Penulis
**Ahmad Farel Algifhari**
* GitHub: [@liebertsenku](https://github.com/liebertsenku)