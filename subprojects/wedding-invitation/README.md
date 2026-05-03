# Wedding Invitation

Undangan pernikahan statis untuk deploy ke Cloudflare Pages.

## Quick Start

1. Ganti placeholder di `index.html` dengan data Anda (nama, tanggal, lokasi, dll).
2. Ganti foto placeholder di `assets/images/`.
3. Sesuaikan warna tema di `css/base.css` bagian `:root`.
4. Sesuaikan tanggal hitung mundur di `js/main.js` (`WEDDING_DATE`).

## RSVP

Pilih salah satu:

- **Google Forms** (paling mudah): Ganti link di tombol "Isi Form RSVP".
- **Custom API**: Uncomment form HTML di `index.html` dan uncomment handler di `js/main.js`. Pastikan endpoint FastAPI Anda sudah tersedia dan CORS diizinkan.

## Deploy

Lihat panduan lengkap di `DEPLOY.md` di root repo.
