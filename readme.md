# 🤖 AI Product Review Analyzer

![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB?logo=react)
![Python](https://img.shields.io/badge/Backend-Pyramid%20Framework-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql)
![Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini-8E75B2)
![Hugging Face](https://img.shields.io/badge/AI-Hugging%20Face-FFD21E)

Aplikasi web cerdas untuk menganalisis ulasan produk secara otomatis. Aplikasi ini menggabungkan kekuatan **Google Gemini AI** (untuk ringkasan poin penting) dan **Hugging Face** (untuk analisis sentimen) guna memberikan wawasan mendalam dari teks ulasan konsumen.

---

## 🌟 Fitur Utama

* **Sentiment Analysis:** Mengklasifikasikan ulasan menjadi *Positive*, *Negative*, atau *Neutral* menggunakan model NLP (RoBERTa).
* **Key Point Extraction:** Meringkas paragraf ulasan panjang menjadi poin-poin kunci (bullet points) menggunakan Gemini 1.5 Flash.
* **Smart Caching:** Menyimpan hasil analisis ke database PostgreSQL. Jika ulasan yang sama diinput ulang, sistem mengambil data dari database untuk menghemat kuota API dan mempercepat respon.
* **Modern UI:** Antarmuka *Glassmorphism* (Dark Mode) yang responsif dan elegan.
* **History Log:** Menampilkan riwayat analisis sebelumnya secara real-time.

---

## 🛠️ Teknologi yang Digunakan

### Frontend
* **React.js (Vite)**: Untuk antarmuka pengguna yang cepat.
* **Axios**: Untuk komunikasi HTTP ke backend.
* **CSS Modules**: Styling modern dengan efek glassmorphism.

### Backend
* **Python (Pyramid Framework)**: Framework web yang digunakan (menggantikan Flask/Django).
* **SQLAlchemy**: ORM untuk interaksi dengan database.
* **PostgreSQL**: Database relasional utama.
* **Google Generative AI SDK**: Integrasi Gemini.

---

## 📋 Prasyarat Sistem

Sebelum menjalankan, pastikan Anda memiliki:
1.  **Node.js & npm** (untuk Frontend).
2.  **Python 3.9+** (untuk Backend).
3.  **PostgreSQL** (sudah terinstall dan berjalan).
4.  **API Keys:**
    * Google Gemini API Key ([Dapatkan di sini](https://aistudio.google.com/)).
    * Hugging Face Access Token ([Dapatkan di sini](https://huggingface.co/settings/tokens)).

---

## 🚀 Panduan Instalasi (Step-by-Step)

### 1. Clone Repository
    ```bash
    git clone [https://github.com/username-anda/product-review-analyzer.git](https://github.com/username-anda/product-review-analyzer.git)
    cd product-review-analyzer

### 2. Setup Database (PostgreSQL)
    ```bash
     Buka terminal SQL atau pgAdmin, lalu jalankan perintah:

    CREATE DATABASE product_review_db;

### 3. Setup Backend
    Masuk ke folder backend dan install dependencies.

    ```bash
    cd backend
    python -m venv venv
    # Aktifkan Venv
    # Windows:
    venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    # Install Library
    pip install pyramid pyramid_tm sqlalchemy zope.sqlalchemy psycopg2-binary requests google-generativeai python-dotenv waitress
    Konfigurasi Environment (.env): Buat file bernama .env di dalam folder backend/. Isi dengan konfigurasi berikut:
    # Masukkan API Key Anda (Jangan pakai tanda kutip)
    UGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
    GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    Jalankan Server Backend:
    ```Bash
    python main.py
    (Server akan berjalan di http://0.0.0.0:6543)

### 4. Setup Frontend
    Buka terminal baru, masuk ke folder frontend.
    ```bash
    cd ../frontend
    # Install paket Node.js
    npm install
    # Jalankan Frontend
    npm run dev
    (Akses aplikasi di http://localhost:5173)

