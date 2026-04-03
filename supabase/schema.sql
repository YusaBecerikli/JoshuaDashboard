-- BÜTÇE
CREATE TABLE IF NOT EXISTS budget (
  id SERIAL PRIMARY KEY,
  type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
  category VARCHAR(100),
  amount DECIMAL(10,2),
  description TEXT,
  date DATE DEFAULT CURRENT_DATE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- ONLİNE GELİR
CREATE TABLE IF NOT EXISTS online_income (
  id SERIAL PRIMARY KEY,
  platform VARCHAR(100),
  amount DECIMAL(10,2),
  month VARCHAR(7),
  monthly_target DECIMAL(10,2),
  notes TEXT,
  date DATE DEFAULT CURRENT_DATE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- DERS ÇALIŞMA
CREATE TABLE IF NOT EXISTS study_sessions (
  id SERIAL PRIMARY KEY,
  subject VARCHAR(100),
  topic VARCHAR(200),
  duration_minutes INTEGER,
  net_count DECIMAL(5,2),
  notes TEXT,
  date DATE DEFAULT CURRENT_DATE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- UYKU
CREATE TABLE IF NOT EXISTS sleep_logs (
  id SERIAL PRIMARY KEY,
  sleep_time TIME,
  wake_time TIME,
  quality INTEGER CHECK (quality BETWEEN 1 AND 10),
  notes TEXT,
  date DATE DEFAULT CURRENT_DATE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- ALIŞKANLIKLAR
CREATE TABLE IF NOT EXISTS habits (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE,
  emoji VARCHAR(10),
  frequency VARCHAR(20) DEFAULT 'daily' CHECK (frequency IN ('daily', 'weekly')),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS habit_logs (
  id SERIAL PRIMARY KEY,
  habit_id INTEGER REFERENCES habits(id) ON DELETE CASCADE,
  completed BOOLEAN DEFAULT TRUE,
  date DATE DEFAULT CURRENT_DATE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- HEDEFLER
CREATE TABLE IF NOT EXISTS goals (
  id SERIAL PRIMARY KEY,
  title VARCHAR(200),
  description TEXT,
  category VARCHAR(50),
  deadline DATE,
  progress INTEGER DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
  status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'archived', 'cancelled')),
  created_at TIMESTAMP DEFAULT NOW()
);

-- SOSYAL NOTLAR
CREATE TABLE IF NOT EXISTS social_notes (
  id SERIAL PRIMARY KEY,
  person_name VARCHAR(100),
  relationship VARCHAR(50),
  note TEXT,
  tags TEXT[],
  date DATE DEFAULT CURRENT_DATE,
  updated_at TIMESTAMP DEFAULT NOW()
);

-- GÜNLÜK PLANLAR
CREATE TABLE IF NOT EXISTS daily_plans (
  id SERIAL PRIMARY KEY,
  date DATE DEFAULT CURRENT_DATE UNIQUE,
  tasks JSONB DEFAULT '[]',
  notes TEXT,
  mood INTEGER CHECK (mood BETWEEN 1 AND 10),
  created_at TIMESTAMP DEFAULT NOW()
);

-- DİNAMİK MODÜLLER
CREATE TABLE IF NOT EXISTS custom_modules (
  id SERIAL PRIMARY KEY,
  module_key VARCHAR(50) UNIQUE,
  title VARCHAR(100),
  description TEXT,
  schema JSONB,
  component_code TEXT,
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS custom_module_data (
  id SERIAL PRIMARY KEY,
  module_key VARCHAR(50) REFERENCES custom_modules(module_key) ON DELETE CASCADE,
  data JSONB,
  date DATE DEFAULT CURRENT_DATE,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS settings (
  key VARCHAR(100) PRIMARY KEY,
  value TEXT,
  updated_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO settings (key, value) VALUES
('system_prompt', 'Sen Joshua''nın kişisel asistanısın. Arkadaş gibi konuş. Türkçe. Kısa ve direkt.'),
('dashboard_version', '2'),
('ai_model', 'llama-3.3-70b-versatile'),
('vision_model', 'llama-4-maverick-17b-128e-instruct')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;

-- SINAV NETLERİ
CREATE TABLE IF NOT EXISTS exam_scores (
  id SERIAL PRIMARY KEY,
  exam_type VARCHAR(10) CHECK (exam_type IN ('TYT', 'AYT')),
  subject VARCHAR(50),
  net_score DECIMAL(5,2),
  date DATE DEFAULT CURRENT_DATE,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- HATIRLATMALAR
CREATE TABLE IF NOT EXISTS reminders (
  id SERIAL PRIMARY KEY,
  message TEXT,
  remind_at TIMESTAMP,
  sent BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- BELLEK
CREATE TABLE IF NOT EXISTS memory (
  key VARCHAR(50) PRIMARY KEY,
  content TEXT,
  updated_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO memory (key, content) VALUES
('profile', '# Joshua — Profil

## Kişisel Bilgiler
- Ad: Muhammed Yuşa Becerikli (Joshua)
- Yaş: 17
- Konum: Bingöl
- Hedef: Sabancı Üniversitesi Bilgisayar Mühendisliği
- Sınav: YKS (Haziran 2026)

## Tercihler


## Öğrenme Stili


## Güçlü/Zayıf Yönler


## Notlar
'),
('knowledge', '# Bilgi Bankası

## Konu Bilgileri


## Pratik Bilgiler


## Keşfedilen Kaynaklar


## Notlar
'),
('history_summary', '# Konuşma Özeti

## Son Önemli Etkileşimler


## Gelişmeler


## Açık Konular

')
ON CONFLICT (key) DO NOTHING;

-- NOTLAR
CREATE TABLE IF NOT EXISTS notes (
  id SERIAL PRIMARY KEY,
  content TEXT,
  tags TEXT[],
  created_at TIMESTAMP DEFAULT NOW()
);

-- GERİ SAYIMLAR
CREATE TABLE IF NOT EXISTS countdowns (
  id SERIAL PRIMARY KEY,
  title VARCHAR(200),
  target_date DATE,
  emoji VARCHAR(10) DEFAULT '⏳',
  created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO countdowns (title, target_date, emoji) VALUES
('YKS 2026', '2026-06-20', '🎓')
ON CONFLICT DO NOTHING;

-- PERFORMANS İÇİN İNDEKSLER
CREATE INDEX IF NOT EXISTS idx_budget_date ON budget(date);
CREATE INDEX IF NOT EXISTS idx_budget_type ON budget(type);
CREATE INDEX IF NOT EXISTS idx_study_sessions_date ON study_sessions(date);
CREATE INDEX IF NOT EXISTS idx_sleep_logs_date ON sleep_logs(date);
CREATE INDEX IF NOT EXISTS idx_habit_logs_date ON habit_logs(date);
CREATE INDEX IF NOT EXISTS idx_habit_logs_habit_id ON habit_logs(habit_id);
CREATE INDEX IF NOT EXISTS idx_exam_scores_date ON exam_scores(date);
CREATE INDEX IF NOT EXISTS idx_exam_scores_type ON exam_scores(exam_type);
CREATE INDEX IF NOT EXISTS idx_reminders_sent ON reminders(sent);
CREATE INDEX IF NOT EXISTS idx_reminders_remind_at ON reminders(remind_at);
CREATE INDEX IF NOT EXISTS idx_custom_module_data_key ON custom_module_data(module_key);
CREATE INDEX IF NOT EXISTS idx_custom_module_data_date ON custom_module_data(date);
CREATE INDEX IF NOT EXISTS idx_online_income_date ON online_income(date);
CREATE INDEX IF NOT EXISTS idx_social_notes_date ON social_notes(date);

-- RLS POLİTİKALARI (Supabase anon key kullanılıyorsa)
ALTER TABLE budget ENABLE ROW LEVEL SECURITY;
ALTER TABLE online_income ENABLE ROW LEVEL SECURITY;
ALTER TABLE study_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE sleep_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE habits ENABLE ROW LEVEL SECURITY;
ALTER TABLE habit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE custom_modules ENABLE ROW LEVEL SECURITY;
ALTER TABLE custom_module_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE exam_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE reminders ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE countdowns ENABLE ROW LEVEL SECURITY;

-- Backend service role ile tüm erişim serbest
CREATE POLICY "Allow all for service role" ON budget FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON online_income FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON study_sessions FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON sleep_logs FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON habits FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON habit_logs FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON goals FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON social_notes FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON daily_plans FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON custom_modules FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON custom_module_data FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON settings FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON exam_scores FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON reminders FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON memory FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON notes FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON countdowns FOR ALL USING (true);
