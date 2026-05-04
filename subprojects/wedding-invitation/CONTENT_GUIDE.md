# Panduan Konten Undangan

Semua teks yang bisa diganti tanpa menyentuh komponen UI berada di **`src/lib/constants.ts`**.

## Nama pasangan

- `GROOM_NAME` — nama mempelai pria (placeholder: `[PRIA]`).
- `BRIDE_NAME` — nama mempelai wanita (placeholder: `[WANITA]`).

Judul HTML/meta ada di `index.html` (sesuaikan `<title>` dan Open Graph).

## Tanggal dan hitung mundur

- `WEDDING_DATE_ISO` — tanggal acara (`YYYY-MM-DD`).
- `WEDDING_DATE` — gabungan tanggal + jam WIB untuk timer (edit jam di string ISO jika perlu).
- `WEDDING_DATE_LABEL_LONG` — kalimat tanggal Indonesia untuk hero dan kartu undangan (harus selaras dengan hari tanggal sebenarnya).

## Foto sampul / hero

- `COVER_IMAGE_SRC` — path ke file di folder `public/`, contoh `/images/cover.jpg`.
- Kosongkan (`''`) untuk hanya memakai latar gradien.

Rekomendasi: rasio potret, kompres WebP/JPG, lebar 1200–1600px.

## Akad & resepsi

- `VENUE_AKAD` dan `VENUE_RESEPSI` — masing-masing:
  - `title`, `scheduleLabel`, `addressLine` (bisa beberapa baris),
  - `directionsUrl` — link **Google Maps** untuk tombol *Petunjuk Lokasi* (buka tab baru),
  - `embedUrl` — kode *Embed a map* dari Google Maps (iframe `src`).

## Lokasi peta (embed)

1. Buka Google Maps → pilih tempat → **Share** → **Embed a map** → salin `src` iframe ke `embedUrl`.
2. Untuk link tombol arah, gunakan **Share** → salin link atau `https://www.google.com/maps/search/?api=1&query=...`.

## RSVP WhatsApp

- `WHATSAPP_RSVP_E164` — nomor **tanpa tanda +**, contoh `6281234567890`.
- Formulir membangun teks Indonesia lalu membuka `wa.me` di tab baru. Simpan ringkasan tetap di perangkat (Zustand persist).

## Hadiah & QRIS

- `BANK_DISPLAY_LINE` — teks lengkap yang terbaca tamu, contoh: `BCA — 1234567890 — a.n. Nama`.
- `BANK_COPY_TEXT` — **hanya** nomor rekening (atau teks yang ingin disalin) untuk tombol *Salin Nomor Rekening*.
- `QRIS_IMAGE_SRC` — path gambar QRIS di `public/`, contoh `/images/qris.png`. Kosongkan untuk menyembunyikan blok QR.

## Ayat

- `AYAT_ARABIC` dan `AYAT_TRANSLATION` — ganti dengan ayat dan terjemahan pilihan Anda (jika diperlukan jangan lupa sumber terjemahan yang Anda pakai).

## Galeri

- Daftar `galleryImages` di `constants.ts`: `src`, `alt` (Bahasa Indonesia), `caption`.
- Letakkan file di `public/` sesuai path, atau ganti `src` ke URL/CDN (tetap gunakan `loading="lazy"` pada `<img>`).
- Saat ini disertakan placeholder SVG di `public/images/gallery/` — ganti dengan foto JPG/WebP Anda.

## Musik

- Letakkan `background.mp3` di `public/music/` (lihat `public/music/README.txt`).
- Pemutaran **tidak** otomatis sampai tamu mengetuk *Buka Undangan*.

## Parameter URL tamu

Tautan berbagi:

`https://domain-anda.com/wedding-invitation/?to=Nama%20Tamu`

Parameter `to` mengisi salam di halaman sampul (sudah di-decode, termasuk `+` sebagai spasi).
