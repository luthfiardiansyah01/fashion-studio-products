# 🛒 Fashion Studio - ETL Pipeline

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-Web%20Scraping-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-336791.svg)
![Google Sheets](https://img.shields.io/badge/Google%20Sheets-API-34A853.svg)
![Testing](https://img.shields.io/badge/Test%20Coverage-90%25+-brightgreen.svg)

## 📖 Deskripsi Proyek
Proyek ini merupakan pipeline ETL (Extract, Transform, Load) yang dirancang untuk mengambil data produk fashion dari kompetitor ("Fashion Studio"). Pipeline ini secara otomatis mengekstrak data mentah dari 50 halaman website, membersihkan dan memformatnya sesuai standar analisis data, serta memuatnya ke dalam 3 repositori data tujuan secara paralel.

## ⚙️ Fitur Utama (Advanced Level)
Proyek ini dibangun dengan prinsip **Modular Code** untuk memudahkan unit testing dan maintenance:

- **Extract (`utils/extract.py`)** 
  - Web scraping multi-halaman (50 halaman, ~1000 data mentah).
  - Penambahan kolom `timestamp` secara otomatis saat proses ekstraksi.
  - Mekanisme *error handling* untuk timeout, koneksi gagal, dan error tak terduga.

- **Transform (`utils/transform.py`)**
  - Konversi mata uang USD ke IDR (Rate: Rp16.000).
  - Parsing kolom `Rating` menjadi tipe `float`.
  - Parsing kolom `Colors` menjadi tipe `int` (angka saja).
  - Penghapusan prefix teks pada kolom `Size` dan `Gender`.
  - Penghapusan data invalid (`Unknown Product`, `Invalid Rating`, `Not Rated`).
  - Penghapusan data duplikat dan nilai NULL.

- **Load (`utils/load.py`)**
  - Ekspor data bersih ke **Flat File (CSV)**.
  - Ekspor data bersih ke **Google Sheets API** (Update data tanpa membuat file baru berulang kali).
  - Ekspor data bersih ke **PostgreSQL / Supabase** (Cloud Database).
  - Setiap fungsi penyimpanan dilengkapi *error handling* spesifik.
