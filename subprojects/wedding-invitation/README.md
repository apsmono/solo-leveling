# Undangan Pernikahan Digital

Undangan pernikahan digital **mobile-first**, nuansa **modern minimalist** (serif judul + sans isi), mirip alur undangan minimalist seperti Goodchoice: sampul → beranda → informasi → kisah & galeri → lokasi → konfirmasi → hadiah.

Semua label UI berbahasa **Indonesia**.

## Rekomendasi stack

Proyek ini memakai **Vite + React 19 + TypeScript + Tailwind CSS**, bukan Next.js.

**Alasan singkat:** undangan ini sebagian besar statis (satu halaman, Tanpa routing server), butuh skor performa tinggi (Lighthouse), dan deployment statis (Cloudflare Pages / Vercel / Netlify / GitHub Pages). Vite menghasilkan bundle kecil, lazy-loading gambar mudah dikontrol, dan tidak memerlukan runtime Node untuk halaman tamu. Next.js sangat berguna jika Anda butuh SSR, banyak rute, atau API Routes — untuk satu landing undangan, biaya kompleksitasnya jarang sebanding.

## Struktur folder

```
wedding-invitation/
├── index.html
├── package.json
├── vite.config.ts          # base: /wedding-invitation/ (sesuaikan jika deploy di root domain)
├── tailwind.config.js
├── public/
│   ├── favicon.svg
│   ├── music/README.txt
│   └── images/gallery/     # placeholder SVG / foto Anda
├── CONTENT_GUIDE.md        # cara mengganti nama, tanggal, peta, WA, bank
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── index.css
│   ├── lib/
│   │   ├── constants.ts    # **pusat pengaturan konten**
│   │   ├── rsvpWhatsApp.ts
│   │   └── utils.ts
│   ├── store/
│   │   └── useInvitationStore.ts
│   ├── hooks/
│   ├── types/
│   └── components/
│       ├── layout/         # Navbar, Footer, MusicPlayer
│       ├── sections/       # setiap blok halaman
│       └── ui/
└── dist/                   # output build
```

## Fitur

- Parameter **`?to=NamaTamu`** untuk nama di sampul.
- **Navigasi menempel** setelah undangan dibuka, anchor ke `#beranda` `#ayatsuci` `#acara` `#kisah` `#galeri` `#lokasi` `#rsvp` `#hadiah`.
- Hitung mundur dengan label **Hari, Jam, Menit, Detik**.
- **RSVP** → membuka **WhatsApp** dengan pesan terisi + ringkasan tersimpan di perangkat.
- **Kirim Hadiah**: salin rekening + opsi **QRIS**.
- **Musik** setelah klik *Buka Undangan* (bukan autoplay paksa).
- Galeri dengan **lazy loading** pada gambar.

## Development

```bash
npm install
npm run dev
```

Contoh: `http://localhost:5173/wedding-invitation/?to=Mba%20Amal` (sesuaikan port dan base path).

## Build

```bash
npm run build
```

Output: `dist/`.

## Deployment — checklist

1. Isi **`src/lib/constants.ts`** dan **`index.html`** (judul/OG) mengikuti `CONTENT_GUIDE.md`.
2. Unggah **`public/music/background.mp3`** jika ingin musik (opsional).
3. Ganti foto galeri dan (opsional) `COVER_IMAGE_SRC`.
4. Periksa **`vite.config.ts` → `base`**:  
   - Subpath (`/wedding-invitation/`) untuk hosting di bawah path monorepo/GitHub Pages.  
   - `'/'` jika domain khusus hanya untuk undangan ini.
5. **Cloudflare Pages / Netlify / Vercel**: root build = `subprojects/wedding-invitation`, perintah build `npm run build`, folder output `dist`.
6. **GitHub Pages / statis**: unggah isi `dist/` atau gunakan workflow yang mem-build subproject tersebut.
7. Uji di lebar **360–414px**, Safari/Chrome, dan satu perangkat WhatsApp (RSVP).
8. Jalankan Lighthouse (mobile) — optimalkan ukuran gambar jika skor turun.

## Lisensi / privasi

Repositori monorepo ini bersifat pribadi; jangan menyimpan API key atau data sensitif tamu di dalam kode.
