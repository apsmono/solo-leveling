# Deploy Sub-Projects ke Cloudflare Pages

Panduan step-by-step deploy dua sub-project (`wedding-invitation` dan `koperasi-landing`) dari monorepo ini ke Cloudflare Pages menggunakan subdomain `*.pages.dev`.

> **Struktur terbaru:** `subprojects/dashboard/`, `subprojects/wedding-invitation/`, dan `subprojects/koperasi-landing/` berisi file aktif di monorepo. Setiap push ke `main` akan otomatis mensinkronkan ke repo eksternal masing-masing via `.github/workflows/sync-subprojects.yml`. Lihat juga `docs/subproject-linking-workflow.md`.

---

## Prasyarat

- Akun Cloudflare (gratis): https://dash.cloudflare.com/sign-up
- Repo ini sudah di-push ke GitHub

---

## Step 1 — Commit & Push ke GitHub

```bash
git add subprojects/wedding-invitation/ subprojects/koperasi-landing/
git commit -m "feat: add wedding invitation and koperasi landing page subprojects"
git push origin agent/claude/subprojects-wedding-koperasi/frontend
```

Setelah di-review, merge ke branch `development` atau `main`.

---

## Step 2 — Buat Project Cloudflare Pages (Wedding Invitation)

1. Login ke [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Klik **Pages** di sidebar kiri
3. Klik **Create a project**
4. Pilih **Connect to Git**
5. Pilih repo `solo-leveling` (authorize Cloudflare ke GitHub jika belum)
6. Klik **Begin setup**
7. Isi konfigurasi build:

   | Field | Value |
   |-------|-------|
   | Project name | `wedding-invitation` (hasil: `wedding-invitation.pages.dev`) |
   | Production branch | `main` (atau `development` jika deploy dari situ) |
   | Build command | *(kosongkan — static HTML)* |
   | Build output directory | `subprojects/wedding-invitation` |

8. Klik **Save and Deploy**
9. Tunggu 1-2 menit. Cloudflare akan memberikan URL: `https://wedding-invitation.pages.dev`

---

## Step 3 — Buat Project Cloudflare Pages (Koperasi Landing)

Ulangi Step 2 dengan data berikut:

| Field | Value |
|-------|-------|
| Project name | `koperasi-kks-landing` |
| Production branch | `main` (atau `development`) |
| Build command | *(kosongkan)* |
| Build output directory | `subprojects/koperasi-landing` |

URL hasil: `https://koperasi-kks-landing.pages.dev`

---

## Step 4 — Update Custom Content

Edit file-file berikut **langsung di repo**, lalu push. Cloudflare akan auto-redeploy.

### Wedding Invitation

- `subprojects/wedding-invitation/index.html`
  - Ganti "Nama & Nama" dengan nama mempelai
  - Ganti tanggal dan lokasi
  - Ganti link Google Forms (atau aktifkan custom form)
- `subprojects/wedding-invitation/css/base.css`
  - Sesuaikan `:root` warna tema (primary, accent, dll)
- `subprojects/wedding-invitation/js/main.js`
  - Ganti `WEDDING_DATE`
- `subprojects/wedding-invitation/assets/images/`
  - Ganti foto placeholder

### Koperasi Landing

- `subprojects/koperasi-landing/index.html`
  - Ganti data koperasi (alamat, telepon, email, badan hukum)
  - Ganti link Google Forms (atau aktifkan custom form)
- `subprojects/koperasi-landing/css/base.css`
  - Sesuaikan `:root` warna brand
- `subprojects/koperasi-landing/assets/images/`
  - Ganti foto/ilustrasi placeholder

---

## Step 5 — Tambahkan Custom Domain (Opsional, Nanti)

Jika suatu saat ingin pindah dari `*.pages.dev` ke domain sendiri:

1. Di dashboard Cloudflare Pages project, klik **Custom domains**
2. Klik **Set up a custom domain**
3. Masukkan domain (misal: `arif-wedding.com`)
4. Ikuti instruksi DNS dari Cloudflare
5. Tidak perlu beli domain di Cloudflare (bisa di registrar mana saja), tapi jika beli di Cloudflare registrar, langkah DNS-nya otomatis.

---

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| Halaman kosong setelah deploy | Pastikan `index.html` ada langsung di `subprojects/NAMA_PROJECT/`, bukan di sub-folder. |
| CSS/JS tidak load | Cek path relatif di `<link>` dan `<script>`. Harusnya `./css/base.css` dan `./js/main.js`. |
| Update tidak muncul | Clear browser cache atau buka URL dengan `?nocache=1`. Cloudflare deploy biasanya 30-60 detik. |
| Form RSVP tidak kirim | Jika pakai custom API, pastikan CORS di `src/app.py` sudah include domain `*.pages.dev` atau domain custom Anda. |

---

## Ringkasan URL Setelah Deploy

| Project | URL Sementara (pages.dev) | URL Custom (nanti) |
|---------|---------------------------|--------------------|
| Wedding Invitation | `https://wedding-invitation.pages.dev` | TBD |
| Koperasi KKS Landing | `https://koperasi-kks-landing.pages.dev` | TBD |

---

*Deploy ke Cloudflare Pages = gratis, unlimited bandwidth, dan auto-SSL. Tidak perlu beli domain untuk mulai.*
