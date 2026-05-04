# Koperasi KKS Landing Page

Landing page statis untuk Koperasi Konsumen Karya Tunggal Sejahtera, siap deploy ke Cloudflare Pages.

## Quick Start

1. Ganti placeholder di `index.html` dengan data koperasi Anda (alamat, telepon, email, nomor badan hukum, dll).
2. Ganti area visual di bagian Tentang: tambahkan berkas misalnya `assets/images/about-hero.jpg` lalu ganti `div.about-visual.placeholder` dengan:
   ```html
   <img src="assets/images/about-hero.jpg" alt="Kantor atau kegiatan Koperasi KKS" width="640" height="480" loading="lazy" class="about-photo">
   ```
   (sesuaikan nama berkas dan teks `alt`.)
3. Opsional: ganti `assets/images/og-share.svg` dengan grafik 1200×630 raster (PNG/JPEG) untuk pratinjau tautan sosial yang lebih konsisten.
4. Sesuaikan warna brand di `css/base.css` bagian `:root`.
5. Sesuaikan poin di bagian "Tentang Kami" (tiga pilar layanan) dengan wording resmi koperasi.

## Kontak

Pilih salah satu:

- **Google Forms** (paling mudah): Ganti link di tombol "Kirim pesan melalui form".
- **Custom API**: Uncomment form HTML di `index.html` dan uncomment handler di `js/main.js`.

## Deploy

Lihat panduan lengkap di [`subprojects/DEPLOY.md`](../DEPLOY.md) (dari folder ini: `../DEPLOY.md`).
