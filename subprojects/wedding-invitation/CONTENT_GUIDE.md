# Panduan Konten Undangan

Semua teks yang bisa diganti tanpa menyentuh komponen UI berada di **`src/lib/constants.ts`**.

## Nama pasangan

- `GROOM_NAME` — nama mempelai pria (tampil di sampul, hero, footer, dll.).
- `BRIDE_NAME` — nama mempelai wanita.

Judul HTML dan meta Open Graph ada di `index.html` — **sesuaikan juga** jika mengganti nama (WhatsApp/preview link membaca meta itu).

## Tanggal dan hitung mundur

- `WEDDING_DATE_ISO` — tanggal acara saja (`YYYY-MM-DD`).
- `WEDDING_DATE` — dipakai untuk hitung mundur (jam default 08:00 WIB; ubah di definisi jika perlu).
- `WEDDING_DATE_LABEL_LONG` — **otomatis**: `formatDateId(WEDDING_DATE)` (`Intl` bahasa Indonesia) + ` · InsyaAllah`. Tidak perlu mengedit manual selama `WEDDING_DATE_ISO` benar.

## Foto sampul

- `COVER_IMAGE_SRC` — path ke file di folder `public/`, contoh `/images/cover.jpg` (hanya di **halaman sampul** sebelum *Buka Undangan*; bagian beranda setelahnya memakai tipografi tanpa duplikasi foto agar LCP tetap ringan).
- Kosongkan (`''`) untuk hanya memakai latar gradien.

Rekomendasi: rasio potret, kompres WebP/JPG, lebar 1200–1600px.

## Akad & resepsi

- `VENUE_AKAD` dan `VENUE_RESEPSI` — masing-masing:
  - `title`, `scheduleLabel`, `addressLine` (bisa beberapa baris),
  - `directionsUrl` — link **Google Maps** untuk tombol *Petunjuk Lokasi* (buka tab baru),
  - `embedUrl` — kode *Embed a map* dari Google Maps (iframe `src`).

### Cara mengisi alamat lengkap dan pin di peta (Google Maps)

1. **Tulis alamat di undangan**  
   Di `src/lib/constants.ts`, isi `addressLine` untuk akad dan/atau resepsi dengan alamat lengkap (jalan, RT/RW, kelurahan, kota, kode pos). Boleh beberapa baris dengan `\n` jika ingin turun baris.

2. **Dapatkan pin yang tepat di Google Maps**  
   - Buka [Google Maps](https://www.google.com/maps).  
   - Cari venue (nama gedung / alamat) sampai muncul pin di lokasi yang benar.  
   - Klik pin atau hasil pencarian → pastikan titik di peta sesuai titik jemput/turun tamu.

3. **Link untuk tombol “Petunjuk Lokasi” (`directionsUrl`)**  
   - Klik **Bagikan** (*Share*) → salin **link** → tempel ke `directionsUrl`.  
   - Alternatif: dari URL browser saat peta sudah fokus ke pin, salin seluruh URL (biasanya panjang dan sudah berisi koordinat).  
   - Tamu akan dibuka di tab baru dan bisa langsung pakai navigasi Google Maps.

4. **Peta embed di halaman undangan (`embedUrl`)**  
   - Masih di tempat yang sama di Maps → **Bagikan** → tab **Sematkan peta** (*Embed a map*).  
   - Pilih ukuran (Medium biasanya cukup) → salin kode HTML → dari tag `<iframe ... src="HTTPS://..." ...>`, ambil **hanya isi atribut `src`** (URL yang diawali `https://www.google.com/maps/embed?...`).  
   - Tempel URL itu ke `embedUrl` di `VENUE_AKAD` atau `VENUE_RESEPSI`.  
   - **Penting:** akad dan resepsi bisa beda venue → isi `embedUrl` dan `directionsUrl` masing-masing.

5. **Cek setelah deploy**  
   Buka halaman **Lokasi** di HP: tombol harus membuka Maps ke pin yang benar, dan iframe harus menampilkan peta (bukan error).

## Lokasi peta (embed) — ringkas

1. **Embed:** Maps → **Bagikan** → **Sematkan peta** → salin `src` iframe → `embedUrl`.  
2. **Tombol arah:** **Bagikan** → salin link → `directionsUrl`, atau pakai URL dari bilah alamat saat pin sudah tepat.

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
