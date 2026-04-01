# Joshua Dashboard V2 — Kişisel Yaşam Takip Sistemi

Kişisel yaşamını takip eden, web dashboard'dan görüntülenebilen ve Telegram üzerinden doğal dille güncellenebilen sistem.

## Özellikler

- 💰 **Bütçe** — Gelir/gider takibi, kategori bazlı özet
- 💻 **Online Gelir** — Clickworker, Outlier vb. platform kazançları
- 📚 **Ders Çalışma** — Süre, konu, YKS net takibi
- 😴 **Uyku** — Yatış/kalkış saati, kalite puanı
- ✅ **Alışkanlıklar** — Günlük takip, streak
- 🎯 **Hedefler** — İlerleme çubukları, kategoriler
- 👥 **Sosyal Notlar** — Kişi bazlı notlar, etiketler
- 📋 **Günlük Plan** — Görev listesi, ruh hali takibi
- 📊 **Grafikler** — Uyku, çalışma, TYT/AYT net grafikleri
- 🔌 **Dinamik Modüller** — AI ile yeni modül ekleme
- ⏰ **Hatırlatmalar** — Zamanlı Telegram bildirimleri
- 🔒 **Şifre Koruması** — Site ve ayarlar ayrı şifreli
- 📅 **Tarih Navigasyonu** — Geçmiş gün verilerini görüntüle
- 🗑️ **Veri Silme** — Telegram'dan "son kaydı sil"
- 🧠 **Uzun Süreli Bellek** — Markdown tabanlı profil, bilgi bankası, konuşma geçmişi
- 👁️ **Görüntü Analizi** — Fotoğraf gönder, AI analiz etsin
- 🤖 **Proaktif Watcher** — Saat başı durum analizi, otomatik mesaj

## Teknoloji Stack

| Katman | Teknoloji |
|---|---|
| Frontend | Next.js 14 + Tailwind CSS + Framer Motion + Recharts |
| Backend | FastAPI (Python) |
| Veritabanı | Supabase (PostgreSQL) |
| Telegram Bot | aiogram 3 |
| AI | Groq — llama-3.3-70b-versatile |
| Backend Hosting | Render |
| Frontend Hosting | Vercel (free tier) |

## Kurulum

### 1. Supabase

1. [supabase.com](https://supabase.com) → ücretsiz hesap oluştur
2. Yeni proje oluştur
3. SQL Editor → `supabase/schema.sql` dosyasının içeriğini yapıştır ve çalıştır
4. Settings → API → **Project URL** ve **anon public key** kopyala

### 2. Groq API Key

1. [console.groq.com](https://console.groq.com) → ücretsiz hesap oluştur
2. API Keys → yeni key oluştur

### 3. Telegram Bot Token

1. Telegram'da `@BotFather` aç
2. `/newbot` komutunu gönder
3. Bot ismini belirle
4. Token'ı kopyala
5. Telegram ID'ni öğrenmek için `@userinfobot` yaz

### 4. Backend — Yerel Geliştirme

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# .env dosyasını doldur
uvicorn main:app --reload
```

### 5. Backend — Render Deploy

1. Projeyi GitHub'a push et
2. [render.com](https://render.com) → ücretsiz hesap → **New Web Service**
3. GitHub repo seç
4. Build komutu: `cd backend && pip install -r requirements.txt`
5. Start komutu: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Environment variables ekle:
   ```
   SUPABASE_URL=...
   SUPABASE_KEY=...
   GROQ_API_KEY=...
   TELEGRAM_TOKEN=...
   TELEGRAM_USER_ID=...
   DASHBOARD_PASSWORD=istedigin_sifre
   SETTINGS_PASSWORD=ayarlar_sifresi
   ```

### 6. Frontend — Yerel Geliştirme

```bash
cd frontend
npm install
# .env.local oluştur:
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_DASHBOARD_PASSWORD=istedigin_sifre" >> .env.local
echo "NEXT_PUBLIC_SETTINGS_PASSWORD=ayarlar_sifresi" >> .env.local
npm run dev
```

### 7. Frontend — Vercel Deploy

1. [vercel.com](https://vercel.com) → GitHub'dan import
2. Environment variables ekle:
   ```
   NEXT_PUBLIC_API_URL=https://[render-url]
   NEXT_PUBLIC_DASHBOARD_PASSWORD=istedigin_sifre
   NEXT_PUBLIC_SETTINGS_PASSWORD=ayarlar_sifresi
   ```
3. Deploy

## Klasör Yapısı

```
JoshuaDashboard/
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Dashboard + şifre + tarih seçici
│   │   ├── layout.tsx
│   │   ├── globals.css
│   │   ├── charts/page.tsx    # Grafikler sayfası
│   │   └── settings/page.tsx  # Ayarlar sayfası
│   ├── components/
│   │   ├── modules/           # Her modül ayrı component
│   │   │   ├── BudgetModule.tsx
│   │   │   ├── StudyModule.tsx
│   │   │   ├── SleepModule.tsx
│   │   │   ├── HabitModule.tsx
│   │   │   ├── GoalsModule.tsx
│   │   │   ├── IncomeModule.tsx
│   │   │   ├── SocialModule.tsx
│   │   │   └── DailyPlanModule.tsx
│   │   ├── ModuleCard.tsx
│   │   └── CustomModuleCard.tsx  # Dinamik modüller
│   ├── lib/
│   │   └── api.ts
│   └── package.json
│
├── backend/
│   ├── main.py                # FastAPI + bot başlatma
│   ├── bot.py                 # Telegram bot + hatırlatma
│   ├── ai.py                  # Groq (Supabase'den prompt çeker)
│   ├── database.py
│   ├── routes/
│   │   ├── budget.py          # + date param, DELETE
│   │   ├── study.py           # + date param, DELETE
│   │   ├── sleep.py           # + date param, DELETE
│   │   ├── habits.py          # + date param, DELETE
│   │   ├── goals.py           # + DELETE
│   │   ├── income.py          # + DELETE
│   │   ├── social.py          # + DELETE
│   │   ├── daily.py
│   │   ├── modules.py
│   │   ├── dashboard.py       # + date param
│   │   ├── scores.py          # TYT/AYT netleri (YENİ)
│   │   ├── reminders.py       # Hatırlatmalar (YENİ)
│   │   ├── settings.py        # Sistem promptu (YENİ)
│   │   └── charts.py          # Grafik verileri (YENİ)
│   ├── requirements.txt
│   └── .env.example
│
└── supabase/
    └── schema.sql             # Tüm tablolar (settings, exam_scores, reminders)
```

## Telegram Bot Kullanımı

Bot ile arkadaşınla konuşur gibi yaz:

```
"bugün 3 saat matematik çalıştım, 45 net yaptım"
"dün gece 01:30'da yattım 09:00'da kalktım"
"clickworker'dan bu ay 1200 tl kazandım"
"bugün 50 lira yemek yedim"
"kitap okuma alışkanlığı ekle"
"TYT matematik 28.5 net"
"AYT fizik 20 net"
"yarın 09:00'da matematik çalışmayı hatırlat"
"son kaydı sil"
"son bütçe kaydını sil"
"her gün su içme takibi ekle"
```

**Bot komutları:**
- `/start` — Botu başlat
- `/durum` — Bugünkü özet
- `/yardim` — Yardım

## API Endpoint'leri

```
# Mevcut endpoint'ler (hepsine ?date=YYYY-MM-DD eklenebilir)
GET    /api/budget              → Bütçe kayıtları
GET    /api/budget/summary      → Özet
POST   /api/budget              → Yeni kayıt
DELETE /api/budget/{id}         → Kayıt sil

GET    /api/study               → Çalışma oturumları
GET    /api/study/summary       → Özet
POST   /api/study               → Oturum ekle
DELETE /api/study/{id}          → Kayıt sil

GET    /api/sleep               → Uyku kayıtları
GET    /api/sleep/summary       → Özet
POST   /api/sleep               → Uyku kaydı ekle
DELETE /api/sleep/{id}          → Kayıt sil

GET    /api/habits              → Alışkanlıklar
POST   /api/habits              → Yeni alışkanlık
POST   /api/habits/{id}/log     → İşaretle
DELETE /api/habits/{id}         → Alışkanlık sil

GET    /api/goals               → Hedefler
POST   /api/goals               → Yeni hedef
PATCH  /api/goals/{id}          → Güncelle
DELETE /api/goals/{id}          → Sil

GET    /api/income              → Online gelir
GET    /api/income/summary      → Özet
POST   /api/income              → Gelir ekle
DELETE /api/income/{id}         → Sil

GET    /api/social              → Sosyal notlar
POST   /api/social              → Not ekle
DELETE /api/social/{id}         → Sil

GET    /api/daily               → Günlük plan
POST   /api/daily               → Plan güncelle

# Yeni endpoint'ler
GET    /api/scores/tyt          → TYT netleri
POST   /api/scores/tyt          → TYT neti ekle
GET    /api/scores/ayt          → AYT netleri
POST   /api/scores/ayt          → AYT neti ekle
DELETE /api/scores/{id}         → Net sil

GET    /api/charts/sleep        → Son 30 gün uyku verisi
GET    /api/charts/study        → Son 30 gün çalışma verisi

GET    /api/reminders           → Aktif hatırlatmalar
POST   /api/reminders           → Hatırlatma ekle
DELETE /api/reminders/{id}      → Hatırlatma sil

GET    /api/settings            → Tüm ayarlar
POST   /api/settings            → Ayar güncelle

GET    /api/modules             → Dinamik modüller
POST   /api/modules             → Modül ekle
GET    /api/modules/{key}/data  → Modül verileri
POST   /api/modules/{key}/data  → Veri ekle

GET    /api/dashboard?date=     → Tüm özet (date param ile)
```

## Güvenlik

- `TELEGRAM_USER_ID` ile sadece senin hesabın botu kullanabilir
- Site giriş şifresi: `DASHBOARD_PASSWORD` env variable
- Ayarlar sayfası şifresi: `SETTINGS_PASSWORD` env variable
- `.env` dosyasını asla commit etme
- Supabase Row Level Security (RLS) eklemek için `schema.sql`'e policy ekle

## Yeni V2 Özellikleri Detay

### Şifre Koruması
- Site açılınca şifre ekranı gelir
- Şifre doğruysa localStorage'da tutulur, tarayıcı kapanınca silinir
- Ayarlar sayfası için ayrı şifre

### Tarih Navigasyonu
- Dashboard üstünde ← → okları ile gün değiştir
- Bugünden ileri gidemez
- Tüm modüller seçili güne göre veri gösterir

### Grafikler Sayfası (`/charts`)
- Uyku: Son 30 gün çizgi grafik, ortalama çizgisi
- Çalışma: Günlük bar chart
- TYT Netleri: 4 ders ayrı çizgi
- AYT Netleri: 4 ders ayrı çizgi

### Hatırlatma Sistemi
- Backend'de 60 saniyede bir kontrol
- Zamanı gelen hatırlatma Telegram'dan gönderilir
- "sent" flag'i TRUE olur

### Sistem Promptu Yönetimi
- `/settings` sayfasından düzenlenebilir
- Supabase `settings` tablosunda saklanır
- Bot her mesajda güncel promptu çeker

### Veri Silme
- Her modül için DELETE endpoint
- Telegram'dan "son kaydı sil" komutu

### Dinamik Modüller
- AI ile yeni modül eklenebilir
- Frontend'de `CustomModuleCard` otomatik render eder
- Counter, text, checkbox tipleri desteklenir

## Render Environment Variables

```
SUPABASE_URL=...
SUPABASE_KEY=...
GROQ_API_KEY=...
TELEGRAM_TOKEN=...
TELEGRAM_USER_ID=...
DASHBOARD_PASSWORD=istedigin_sifre
SETTINGS_PASSWORD=ayarlar_sifresi
```
