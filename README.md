# UnduhKu

Aplikasi web untuk mengunduh video sampai 4K dan audio MP3, WAV dari YouTube, TikTok, Instagram, Facebook, Shopee Video, Snack Video, dan situs lain. Dibuat oleh Saiful Arif.

Isi repo ini:

- `index.html` adalah aplikasinya, satu file. Dilayani lewat GitHub Pages.
- `.github/workflows/download.yml` dan `scripts/download.py` adalah mesin unduh (yt-dlp + ffmpeg) yang dipanggil aplikasi.
- `.github/workflows/cleanup.yml` menghapus berkas hasil unduhan yang sudah lebih dari 90 menit.
- `firestore.rules` adalah Security Rules untuk Firebase.
- `PANDUAN.md` berisi langkah pemasangan lengkap. Di repo ini folder `github-engine/` yang disebut di panduan sudah ada di akar repo.

Repo ini harus tetap publik supaya berkas hasil unduhan bisa diambil pengunjung.
