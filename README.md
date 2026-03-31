# Joshua Dashboard — Kişisel Yaşam Takip Sistemi

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
- 🔌 **Dinamik Modüller** — Yeni modül ekleme (veritabanı üzerinden)

## Teknoloji Stack

| Katman | Teknoloji |
|---|---|
| Frontend | Next.js 14 + Tailwind CSS + Framer Motion |
| Backend | FastAPI (Python) |
| Veritabanı | Supabase (PostgreSQL) |
| Telegram Bot | aiogram 3 |
| AI | Groq — llama-3.3-70b-versatile |
| Backend Hosting | Koyeb (free tier) |
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

### 5. Backend — Koyeb Deploy

1. Projeyi GitHub'a push et
2. [koyeb.com](https://koyeb.com) → ücretsiz hesap → **Create Service**
3. GitHub repo seç
4. Build komutu: `pip install -r backend/requirements.txt`
5. Run komutu: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Environment variables ekle:
   ```
   SUPABASE_URL=...
   SUPABASE_KEY=...
   GROQ_API_KEY=...
   TELEGRAM_TOKEN=...
   TELEGRAM_USER_ID=...
   ```

### 6. Frontend — Yerel Geliştirme

```bash
cd frontend
npm install
# .env.local oluştur:
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

### 7. Frontend — Vercel Deploy

1. [vercel.com](https://vercel.com) → GitHub'dan import
2. Environment variable ekle:
   ```
   NEXT_PUBLIC_API_URL=https://[koyeb-url]
   ```
3. Deploy

## Klasör Yapısı

```
dashboard-agent/
├── frontend/                  # Next.js uygulaması
│   ├── app/
│   │   ├── page.tsx           # Ana dashboard
│   │   ├── layout.tsx
│   │   └── globals.css
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
│   │   └── ModuleCard.tsx     # Ortak kart bileşeni
│   ├── lib/
│   │   └── api.ts             # Backend API çağrıları
│   └── package.json
│
├── backend/                   # FastAPI + Telegram Bot
│   ├── main.py                # FastAPI giriş noktası
│   ├── bot.py                 # Telegram bot
│   ├── ai.py                  # Groq entegrasyonu
│   ├── database.py            # Supabase bağlantısı
│   ├── routes/                # API endpoint'leri
│   │   ├── budget.py
│   │   ├── study.py
│   │   ├── sleep.py
│   │   ├── habits.py
│   │   ├── goals.py
│   │   ├── income.py
│   │   ├── social.py
│   │   ├── daily.py
│   │   ├── modules.py         # Dinamik modül yönetimi
│   │   └── dashboard.py       # Toplu özet endpoint
│   ├── requirements.txt
│   └── .env.example
│
└── supabase/
    └── schema.sql             # Tüm tablolar
```

## Telegram Bot Kullanımı

Bot ile arkadaşınla konuşur gibi yaz:

```
"bugün 3 saat matematik çalıştım, 45 net yaptım"
"dün gece 01:30'da yattım 09:00'da kalktım"
"clickworker'dan bu ay 1200 tl kazandım"
"bugün 50 lira yemek yedim"
"kitap okuma alışkanlığı ekle"
"bakiyem ne kadar"
"yarın dişçi randevum var, plana ekle"
```

**Bot komutları:**
- `/start` — Botu başlat
- `/durum` — Bugünkü özet
- `/yardim` — Yardım

## API Endpoint'leri

```
GET    /api/budget              → Son 100 bütçe kaydı
GET    /api/budget/summary      → Özet (bakiye, kategoriler)
POST   /api/budget              → Yeni kayıt

GET    /api/study               → Son 100 çalışma oturumu
GET    /api/study/summary       → Özet (toplam saat, ortalama net)
POST   /api/study               → Oturum ekle

GET    /api/sleep               → Son 30 uyku kaydı
GET    /api/sleep/summary       → Özet (ortalama süre, kalite)
POST   /api/sleep               → Uyku kaydı ekle

GET    /api/habits              → Tüm alışkanlıklar + bugünkü durum
POST   /api/habits              → Yeni alışkanlık ekle
POST   /api/habits/{id}/log     → Alışkanlık işaretle

GET    /api/goals               → Tüm hedefler
POST   /api/goals               → Yeni hedef ekle
PATCH  /api/goals/{id}          → Hedef güncelle

GET    /api/income              → Online gelir kayıtları
GET    /api/income/summary      → Platform bazlı özet
POST   /api/income              → Gelir kaydı ekle

GET    /api/social              → Sosyal notlar
POST   /api/social              → Not ekle

GET    /api/daily               → Bugünün planı
POST   /api/daily               → Plan güncelle

GET    /api/modules             → Aktif dinamik modüller
POST   /api/modules             → Yeni modül ekle
GET    /api/modules/{key}/data  → Modül verileri
POST   /api/modules/{key}/data  → Modüle veri ekle

GET    /api/dashboard           → Tüm modüllerin özet verisi (tek istek)
```

## Güvenlik

- `TELEGRAM_USER_ID` ile sadece senin hesabın botu kullanabilir
- `.env` dosyasını asla commit etme
- Supabase Row Level Security (RLS) eklemek için `schema.sql`'e policy ekle

## Genişletme

Yeni modül eklemek için kod değiştirmeye gerek yok:

1. Supabase `custom_modules` tablosuna kayıt ekle
2. Frontend'de `ModuleGrid` otomatik render eder
3. Telegram bot `module_add` aksiyonunu destekler
