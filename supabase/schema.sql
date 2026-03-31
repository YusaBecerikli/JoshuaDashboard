-- BÜTÇE
CREATE TABLE IF NOT EXISTS budget (
  id SERIAL PRIMARY KEY,
  type VARCHAR(10) NOT NULL,
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
  date DATE DEFAULT CURRENT_DATE
);

-- DERS ÇALIŞMA
CREATE TABLE IF NOT EXISTS study_sessions (
  id SERIAL PRIMARY KEY,
  subject VARCHAR(100),
  topic VARCHAR(200),
  duration_minutes INTEGER,
  net_count DECIMAL(5,2),
  notes TEXT,
  date DATE DEFAULT CURRENT_DATE
);

-- UYKU
CREATE TABLE IF NOT EXISTS sleep_logs (
  id SERIAL PRIMARY KEY,
  sleep_time TIME,
  wake_time TIME,
  quality INTEGER CHECK (quality BETWEEN 1 AND 10),
  notes TEXT,
  date DATE DEFAULT CURRENT_DATE
);

-- ALIŞKANLIKLAR
CREATE TABLE IF NOT EXISTS habits (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE,
  emoji VARCHAR(10),
  frequency VARCHAR(20) DEFAULT 'daily',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS habit_logs (
  id SERIAL PRIMARY KEY,
  habit_id INTEGER REFERENCES habits(id),
  completed BOOLEAN DEFAULT TRUE,
  date DATE DEFAULT CURRENT_DATE
);

-- HEDEFLER
CREATE TABLE IF NOT EXISTS goals (
  id SERIAL PRIMARY KEY,
  title VARCHAR(200),
  description TEXT,
  category VARCHAR(50),
  deadline DATE,
  progress INTEGER DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
  status VARCHAR(20) DEFAULT 'active',
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
  mood INTEGER CHECK (mood BETWEEN 1 AND 10)
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
  module_key VARCHAR(50) REFERENCES custom_modules(module_key),
  data JSONB,
  date DATE DEFAULT CURRENT_DATE,
  created_at TIMESTAMP DEFAULT NOW()
);
