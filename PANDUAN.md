# Panduan UnduhKu

by Saiful Arif

UnduhKu terdiri dari tiga bagian yang masing-masing gratis:

1. `index.html`, aplikasi satu file untuk Blogger atau hosting statis apa saja.
2. `github-engine/`, mesin unduh (yt-dlp + ffmpeg) yang jalan di GitHub Actions.
3. Firebase (Firestore dan Authentication), tempat pengaturan, log, dan akun admin.

Pengunjung tidak perlu login. Hanya panel admin yang memakai Firebase Authentication.

## Coba dulu tanpa apa-apa

Buka `index.html` di browser. Saklar `IS_PREVIEW` masih `true`, jadi semua data disimpan di browser dan tombol unduh menghasilkan berkas contoh (mode demo). Panel admin bisa dibuka lewat tautan "Panel Admin" di sidebar dengan akun demo `admin@unduhku.app` dan sandi `admin123`.

## Langkah 1: Pasang mesin unduh di GitHub

1. Buat repo baru di GitHub. Atur ke **Public**. Ini perlu supaya berkas hasil unduhan bisa diambil pengunjung tanpa login, dan menit GitHub Actions untuk repo publik tidak dibatasi.
2. Unggah seluruh isi folder `github-engine/` ke repo itu. Pastikan folder `.github/workflows/` ikut terunggah. Folder ini tersembunyi di beberapa file manager, jadi cek di halaman repo.
3. Buka Settings > Actions > General, turun ke Workflow permissions, pilih **Read and write permissions**, lalu simpan.
4. Buka tab Actions dan aktifkan workflow bila GitHub memintanya.
5. Buat token: Settings akun > Developer settings > Personal access tokens > Fine-grained tokens > Generate new token.
   - Repository access: Only select repositories, pilih repo tadi saja.
   - Permissions: Actions = Read and write. Metadata = Read-only (otomatis).
   - Atur masa berlaku (misalnya 1 tahun) dan salin tokennya. Token hanya tampil sekali.
6. Opsional untuk YouTube, lihat bagian "Batasan" di bawah tentang secret `COOKIES_TXT`.

Berkas hasil unduhan disimpan sebagai aset di release bertag `dl`, lalu dihapus otomatis oleh workflow `Bersihkan Berkas Lama` setelah sekitar 90 menit.

## Langkah 2: Siapkan Firebase

1. Buat project di console.firebase.google.com.
2. Build > Firestore Database > Create database (mode production, pilih lokasi terdekat misalnya `asia-southeast2`).
3. Build > Authentication > Get started > aktifkan **Email/Password**.
4. Tab Users > Add user, daftarkan **satu** akun admin (email dan sandi yang kuat). Cukup satu.
5. Buka Firestore > Rules, tempel isi `firestore.rules`, **ganti `GANTI_DENGAN_EMAIL_ADMIN` dengan email admin tadi**, lalu Publish.
6. Project settings > Your apps > tambahkan app Web, lalu salin objek `firebaseConfig`.

## Langkah 3: Pasang aplikasinya

1. Buka `index.html` dengan editor teks. Tempel `firebaseConfig` kamu di bagian KONFIGURASI APLIKASI, lalu ubah `IS_PREVIEW` menjadi `false`.
2. Blogger: buat Halaman baru, pilih mode HTML, tempel seluruh isi `index.html`, lalu terbitkan. Aplikasi menutupi seluruh layar dengan sendirinya, jadi tema Blogger tidak perlu diedit. Hosting lain (GitHub Pages, Netlify, Cloudflare Pages): unggah `index.html` apa adanya.
3. Buka aplikasinya, klik "Panel Admin" di sidebar, lalu masuk dengan akun admin Firebase. Saat pertama kali admin masuk, fungsi `autoSetupDatabase()` mengisi database sendiri: daftar platform, pengaturan awal, dan beberapa log contoh. Kamu tidak perlu input apa pun secara manual.
4. Buka Pengaturan Engine, pilih mode **GitHub Actions**, isi pemilik repo, nama repo, dan token. Klik Simpan, lalu Tes koneksi.
5. Kembali ke beranda, tempel satu link, pilih format, lalu Unduh Sekarang. Biasanya butuh 30 detik sampai 2 menit karena runner GitHub harus menyala dulu.

Sebelum admin pertama kali masuk, pengunjung tetap bisa membuka aplikasi. Daftar platform dan pengaturan memakai nilai bawaan di dalam kode.

## Mode lain

- API generik: isi alamat endpoint yang menerima POST JSON ala Cobalt (`url`, `downloadMode`, `videoQuality`, `audioFormat`). Cocok kalau suatu saat kamu punya server sendiri.
- Demo: berkas contoh, untuk uji tampilan.

## Batasan yang perlu kamu tahu

- **YouTube sering memblokir IP GitHub.** Runner GitHub berasal dari datacenter, dan YouTube cenderung menampilkan pemeriksaan "Sign in to confirm you're not a bot" untuk IP seperti itu. TikTok, Instagram publik, dan Facebook publik biasanya lebih lancar. Kalau YouTube gagal, tambahkan cookies: ekspor cookies YouTube dalam format Netscape (`cookies.txt`) dari browser yang sedang login, lalu simpan isinya sebagai secret repo bernama `COOKIES_TXT` (Settings > Secrets and variables > Actions). Pakai akun cadangan, bukan akun utama, karena akun yang cookies-nya dipakai di server bisa kena pembatasan.
- **Token GitHub terlihat di browser.** Tanpa backend, token harus ikut dikirim ke browser pengunjung. Karena itu token dibuat fine-grained dan hanya untuk satu repo dengan izin Actions. Risikonya sebatas ada orang yang memicu workflow berulang kali. Kuota harian per perangkat membantu, tapi pengunjung yang menghapus data browsernya bisa mengulang dari nol. Kalau jadi ramai, pindah ke mode API generik dengan server sendiri.
- **Berkas hasil bersifat publik sementara.** Siapa pun yang tahu link-nya bisa mengambil berkas selama masih ada, sekitar 90 menit.
- **Batas ukuran 1,9 GB per berkas.** Video 4K yang panjang bisa melewati batas ini dan akan gagal dengan pesan yang jelas. Pengunjung bisa memilih resolusi lebih rendah.
- **Shopee Video dan Snack Video berstatus Beta.** Dukungannya bergantung pada yt-dlp dan sering berubah. Admin bisa menonaktifkannya di Kelola Platform.
- **Resolusi mengikuti video asli.** Video yang hanya ada 1080p tidak bisa dijadikan 4K.
- **Workflow terjadwal bisa mati sendiri.** GitHub menonaktifkan workflow terjadwal di repo publik yang tidak ada aktivitas selama 60 hari. Kalau pembersihan berhenti, buka tab Actions dan aktifkan lagi.
- **Service worker PWA.** Browser tertentu menolak service worker yang dibuat dari Blob. Aplikasinya tetap jalan normal, hanya fitur offline dan pemasangan sebagai aplikasi yang bisa tidak tersedia.
- **Hukum dan ketentuan platform.** Mengunduh konten orang lain tanpa izin bisa melanggar hak cipta dan syarat layanan platform. Aplikasi ini menampilkan pengingat soal itu, dan penggunaannya tetap tanggung jawab pemakainya.

## Kalau ada masalah

| Gejala | Penyebab umum |
|---|---|
| "Layanan belum aktif" | Pengaturan Engine belum diisi atau belum disimpan |
| "Token GitHub tidak valid" | Token salah ketik, kedaluwarsa, atau bukan untuk repo yang benar |
| "Repo atau nama file workflow tidak ditemukan" | Nama repo salah, repo masih private, atau folder `.github/workflows` belum terunggah |
| Menunggu runner lebih dari 3 menit | Cek tab Actions di repo, kadang antre atau workflow nonaktif |
| "YouTube memblokir server GitHub" | Tambahkan secret `COOKIES_TXT`, lihat bagian Batasan |
| Log atau dasbor kosong dan muncul "Cek Security Rules" | Email admin di rules belum sama dengan email akun yang dipakai login |
| Login admin gagal | Akun belum didaftarkan di Authentication, atau `IS_PREVIEW` masih `true` |
