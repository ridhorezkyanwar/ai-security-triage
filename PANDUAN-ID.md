# Panduan AI Security Triage Agent (Groq)

Versi ini memakai **Groq API**, bukan Ollama lokal. Karena model berjalan di cloud Groq, kamu tidak perlu mengunduh model beberapa GB atau menyediakan RAM besar. Sebagai gantinya, kamu perlu internet, API key Groq, dan harus memerhatikan batas penggunaan akun. Mode demo tetap bisa dipakai tanpa API key.

## 1. Cara termudah di Windows

1. Unduh dan ekstrak ZIP proyek.
2. Pastikan Python 3.11 atau lebih baru sudah terpasang.
3. Klik dua kali `run-windows.bat`.
4. Tunggu sampai dependensi terpasang dan server berjalan.
5. Buka `http://127.0.0.1:8000`.

Script akan membuat virtual environment `.venv` dan menyalin `.env.example` menjadi `.env` jika file `.env` belum ada.

## 2. Jalankan demo tanpa API key

Pilih **Rule-based demo — offline, not AI**, klik **Load sample**, kemudian **Analyze report**. Mode ini hanya memakai aturan kata sederhana untuk menunjukkan alur aplikasi. Ini bukan prediksi AI, bukan pemindai keamanan, dan tidak mengirim laporan ke penyedia layanan.

## 3. Siapkan API key Groq

1. Buka [Groq Console — API Keys](https://console.groq.com/keys).
2. Buat akun/key hanya jika opsi itu tersedia untuk akunmu. Groq menyediakan Free Plan dengan batas pemakaian, tetapi akses model, limit, dan ketentuan dapat berubah. Cek [rate limits resmi](https://console.groq.com/docs/rate-limits). Jangan menambahkan saldo atau memilih paket berbayar hanya demi mencoba proyek ini.
3. Kalau layar meminta detail pembayaran dan tujuanmu harus tetap Rp0, jangan lanjutkan sebelum memastikan ketentuannya. Pakai demo offline untuk sementara.
4. Buka file `.env` dalam folder proyek dan isi:

   ```dotenv
   GROQ_API_KEY=MASUKKAN_API_KEY_DI_SINI
   GROQ_MODEL=openai/gpt-oss-20b
   ```

5. Simpan file, hentikan server dengan `Ctrl+C`, lalu jalankan `run-windows.bat` lagi.
6. Di web, pilih **Groq cloud AI**, muat contoh, kemudian tekan **Analyze report**.

Model default `openai/gpt-oss-20b` tercantum di dokumentasi model dan mendukung structured outputs menurut dokumentasi Groq saat proyek ini diperbarui. Kalau model tidak tersedia untuk akunmu atau API menolak permintaan, cek [model yang tersedia](https://console.groq.com/docs/models). Kamu bisa mengganti `GROQ_MODEL` dengan model ID yang tersedia untuk key-mu.

## 4. Apakah Groq gratis?

Groq mendokumentasikan Free Plan, tetapi bukan berarti penggunaan tanpa batas. Batas request dan token dapat berbeda menurut model, akun, dan plan. Saat mencapai batas, API dapat mengembalikan `429` dan aplikasi menampilkan pesan error. Aplikasi tidak akan otomatis melakukan upgrade berbayar.

Referensi:
- [Groq Console](https://console.groq.com/)
- [API reference](https://console.groq.com/docs/api-reference)
- [Model yang didukung](https://console.groq.com/docs/models)
- [Rate limits](https://console.groq.com/docs/rate-limits)

## 5. Keamanan API key dan data

- Jangan kirim key ke chat atau tempel di kode frontend.
- Key hanya boleh disimpan di `.env` lokal atau secret setting di hosting.
- Jangan upload `.env` ke GitHub; file tersebut sudah masuk `.gitignore`, tetapi tetap cek `git status` sebelum commit.
- Groq mode mengirim isi laporan ke layanan Groq. Gunakan data sintetis atau laporan yang disamarkan. Jangan masukkan password, cookie, token, data pribadi, source code privat, atau detail program rahasia.
- Jangan menggunakan output untuk menutup laporan atau menjalankan exploit secara otomatis. Semua hasil harus ditinjau manusia.

## 6. Tes offline

```bash
python -m pytest
```

Tes memakai respons tiruan, tidak butuh API key dan tidak mengirim data ke Groq.

## 7. Benchmark (menggunakan kuota API)

Ada 36 contoh sintetis. Coba lima kasus terlebih dahulu:

```bash
python scripts/evaluate.py --live --limit 5
```

Perintah ini melakukan permintaan live dan memakai kuota Groq. Untuk semua kasus, hapus `--limit 5` hanya setelah kamu memeriksa batas akunmu. Tambahkan `--delay 2` untuk memberi jeda antarpermintaan. Hasil JSON/CSV dibuat di folder `reports/`. Jangan mengklaim akurasi sebelum benar-benar menjalankan evaluasi.

## 8. Deployment yang aman

Untuk deployment publik, gunakan secret environment berikut di dashboard hosting:

```dotenv
REQUIRE_AUTH=true
APP_ACCESS_USERNAME=analyst
APP_ACCESS_PASSWORD=GANTI_DENGAN_PASSWORD_PANJANG_UNIK
GROQ_API_KEY=ISI_DI_SECRET_HOSTING
```

Jangan commit password atau API key. Blueprint Render dan Dockerfile proyek ini mengaktifkan autentikasi secara default. Jika `REQUIRE_AUTH=true` tetapi password belum diisi, halaman dan API utama akan menolak akses dengan HTTP 503; endpoint `/health` tetap tersedia untuk pemeriksaan hosting. Jangan menonaktifkan autentikasi pada instance yang dapat diakses publik.

## 9. Deployment Vercel

Jika Render meminta kartu pembayaran, jangan lanjutkan di Render. Vercel sudah mendukung FastAPI dari entry point `app.py`. Hubungkan repository ini sebagai project Vercel di plan Hobby, lalu masukkan environment variable berikut pada Production:

```dotenv
REQUIRE_AUTH=true
APP_ACCESS_USERNAME=analyst
APP_ACCESS_PASSWORD=PASSWORD_UNIK_YANG_PANJANG
GROQ_MODEL=openai/gpt-oss-20b
GROQ_API_KEY=API_KEY_GROQ_MILIKMU
```

Masukkan password dan API key langsung pada dashboard Vercel sebagai secret, bukan ke file repo. Aplikasi sekarang terkunci secara default bila `REQUIRE_AUTH` tidak diatur; jika password belum terisi, halaman akan mengembalikan HTTP 503. Jangan aktifkan resource berbayar. Setelah mengatur environment variables, redeploy, lalu uji login Basic Auth dan mode demo dengan laporan sintetis.

## 10. Status teknis

- Aplikasi sudah dideploy ke Vercel: https://ai-security-triage.vercel.app
- Gunakan domain alias di atas untuk versi terbaru. URL dengan hash deployment lama tetap menunjuk ke build lama.
- Deployment versi terbaru pada commit `7f44aa1ae7befd13d80744309dbeb00fd6749e5b` berstatus READY. Build warning pengumpulan CSS yang muncul sebelumnya sudah tidak muncul setelah aset CSS dipindahkan ke `public/static/styles.css` dan dependensi Python dideklarasikan eksplisit di `pyproject.toml`.
- Akses aplikasi memakai HTTP Basic Auth dengan username `analyst`. Password disimpan sebagai environment variable sensitif di Vercel; jangan commit ke GitHub.
- `GROQ_API_KEY` sudah dikonfigurasi di Vercel sebagai secret sensitif untuk Production dan Preview. Namun, permintaan Groq live belum diuji, jadi keberhasilan model/API belum terkonfirmasi.
- GitHub Actions `pytest` lulus untuk perbaikan CSS dan metadata dependensi. Ini tidak membuktikan alur login browser atau inferensi Groq secara live.
- Branch protection untuk `main` masih belum aktif. Integrasi GitHub di sesi ini tidak menyediakan operasi tulis untuk aturan branch; endpoint proteksi juga ditolak karena izin integrasi. Buka [GitHub Settings → Rules](https://github.com/ridhorezkyanwar/ai-security-triage/settings/rules), buat ruleset untuk `main`, wajibkan pull request dan status check `pytest`, lalu blokir force push serta penghapusan branch.
- Render meminta informasi pembayaran (HTTP 402); tidak ada kartu atau paket berbayar yang ditambahkan.
