# pdfEngine

Layanan **PDF Engine** berbasis Python untuk membuat dan mengelola dokumen PDF, lengkap dengan dukungan Docker agar mudah dijalankan di environment mana pun.

> ⚠️ Catatan: bagian yang bertanda `TODO` perlu disesuaikan dengan implementasi aktual di kode (nama framework, endpoint, variabel environment, dll).

## Fitur

- Pembuatan dokumen PDF secara terstruktur
- Penyimpanan hasil file di folder `storage/`
- Konfigurasi lewat environment variable (`.env`)
- Siap dijalankan dengan Docker & Docker Compose
- Dilengkapi folder `tests/` untuk pengujian

## Struktur Proyek

```
pdfEngine/
├── app/                 # Kode utama aplikasi
├── storage/             # Penyimpanan file PDF (input/output)
├── tests/               # Unit test
├── .env.example         # Contoh konfigurasi environment
├── .gitignore
├── Dockerfile           # Image Docker aplikasi
├── docker-compose.yml   # Orkestrasi container
├── requirements.txt     # Dependensi Python
└── README.md
```

## Prasyarat

- Python 3.10+ (jika dijalankan tanpa Docker)
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose (opsional, direkomendasikan)

## Instalasi

### 1. Clone repository

```bash
git clone https://github.com/Tonyprasteyo2/pdfEngine.git
cd pdfEngine
```

### 2. Siapkan environment

```bash
cp .env.example .env
```

Lalu sesuaikan nilai di dalam `.env`.

### 3a. Jalankan dengan Docker (direkomendasikan)

```bash
docker compose up --build
```

### 3b. Jalankan secara lokal

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Jalankan aplikasi:

```bash
# TODO: sesuaikan dengan entry point proyek, contoh:
# uvicorn app.main:app --reload
```

## Konfigurasi

Semua konfigurasi diatur lewat file `.env`. Lihat `.env.example` untuk daftar variabel yang tersedia.

| Variabel | Deskripsi |
|----------|-----------|
| `TODO`   | Isi sesuai isi `.env.example` |

## Penggunaan

```bash
# TODO: tambahkan contoh pemakaian, misalnya request ke endpoint:
# curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -d '{...}'
```

File hasil akan tersimpan di folder `storage/`.

## Testing

```bash
pip install pytest
pytest tests/
```

## Kontribusi

Kontribusi sangat diterima!

1. Fork repository ini
2. Buat branch baru: `git checkout -b fitur-baru`
3. Commit perubahan: `git commit -m "Tambah fitur baru"`
4. Push ke branch: `git push origin fitur-baru`
5. Buat Pull Request


---

Jika proyek ini bermanfaat, jangan lupa beri ⭐ di GitHub!
