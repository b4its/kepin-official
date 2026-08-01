# KePin Frontend

SvelteKit + Svelte 5 UI untuk aplikasi KePin (ERP multi-tenant).

Lihat README di root repo untuk gambaran arsitektur, Docker Compose,
dan dokumentasi lengkap. Ringkasan perintah:

```sh
npm install        # instal dependensi
npm run dev        # dev server (http://localhost:5173)
npm run build      # production build
npm run preview    # serve hasil build
npx playwright test         # E2E suite penuh (API + browser)
npx playwright test --headed
npx playwright test e2e/client/owner/ui-interaction.spec.ts
```

Catatan penting:

- **Stack Docker memakai production build** (`node build/index.js`),
  bukan dev server. Perubahan pada source frontend tidak tampak sampai
  container di-rebuild:
  `docker compose build frontend && docker compose up -d frontend`.
- Kontainer menyimpan state login Playwright di `e2e/.auth/` (di-commit).
  Setelah mengubah kredensial demo atau helper auth, jalankan suite lalu
  commit hasil refresh state tersebut.
