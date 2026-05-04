# Wedding Invitation

Undangan pernikahan digital dengan React, TypeScript, dan Tailwind CSS. Deploy ke Cloudflare Pages.

## Fitur

- **Halaman Pembuka** dengan nama tamu personal dari URL (`?to=NamaTamu`)
- **Musik Latar** dengan tombol mengambang
- **Galeri Foto** dengan lightbox
- **Formulir RSVP** dengan validasi dan auto-save
- **Buku Ucapan** untuk doa dan pesan dari tamu
- **Hitung Mundur** menuju hari pernikahan
- **Desain Responsif** untuk desktop dan mobile

## Tech Stack

- React 19 + TypeScript
- Vite
- Tailwind CSS v3
- Framer Motion
- Zustand
- Lucide React

## Cara Pakai

### Development

```bash
npm install
npm run dev
```

Buka `http://localhost:5173/?to=Bapak%20Joko` untuk melihat halaman pembuka dengan nama tamu.

### Build

```bash
npm run build
```

Output ada di folder `dist/`.

### Customisasi

1. **Ganti data pasangan**: Edit file di `src/components/sections/`
2. **Ganti foto galeri**: Tambahkan foto ke `public/images/gallery/`
3. **Ganti tanggal**: Edit `WEDDING_DATE` di `src/lib/constants.ts`
4. **Ganti musik**: Ganti file `public/music/background.mp3`
5. **Ganti warna tema**: Edit `tailwind.config.js`

### Share Link ke Tamu

```
https://your-domain.com/?to=Bapak%20Joko%20Widodo
```

Nama tamu akan muncul di halaman pembuka.

## Deploy

Lihat panduan lengkap di `DEPLOY.md` di root repo.
