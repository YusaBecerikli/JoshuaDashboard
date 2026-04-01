"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import BudgetModule from "@/components/modules/BudgetModule";
import StudyModule from "@/components/modules/StudyModule";
import SleepModule from "@/components/modules/SleepModule";
import HabitModule from "@/components/modules/HabitModule";
import GoalsModule from "@/components/modules/GoalsModule";
import IncomeModule from "@/components/modules/IncomeModule";
import SocialModule from "@/components/modules/SocialModule";
import DailyPlanModule from "@/components/modules/DailyPlanModule";
import CustomModuleCard from "@/components/CustomModuleCard";

function PasswordGate({ onUnlock }: { onUnlock: () => void }) {
  const [password, setPassword] = useState("");
  const [error, setError] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (password === process.env.NEXT_PUBLIC_DASHBOARD_PASSWORD) {
      localStorage.setItem("dashboard_unlocked", "true");
      onUnlock();
    } else {
      setError(true);
      setTimeout(() => setError(false), 1000);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative">
      <div className="gradient-bg" />
      <div className="noise" />
      <motion.form
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        onSubmit={handleSubmit}
        className="glass p-8 w-full max-w-sm relative z-10"
      >
        <h2 className="text-xl font-bold mb-4 text-center">🔒 Joshua Dashboard</h2>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Şifre..."
          autoFocus
          className={`w-full bg-gray-900 border ${error ? "border-neon-pink" : "border-gray-700"} rounded-lg px-4 py-3 text-white text-center mono focus:outline-none focus:border-accent transition-colors`}
        />
        {error && <p className="text-neon-pink text-xs mt-2 text-center">Yanlış şifre</p>}
        <button type="submit" className="w-full mt-4 bg-accent hover:bg-accent-light text-white py-3 rounded-lg font-medium transition-colors">
          Giriş
        </button>
      </motion.form>
    </div>
  );
}

export default function Home() {
  const [unlocked, setUnlocked] = useState(false);
  const [time, setTime] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(() => {
    const now = new Date();
    return now.toISOString().split("T")[0];
  });
  const [summary, setSummary] = useState<any>(null);
  const [customModules, setCustomModules] = useState<any[]>([]);

  useEffect(() => {
    if (localStorage.getItem("dashboard_unlocked") === "true") {
      setUnlocked(true);
    }
  }, []);

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    Promise.all([
      fetch(`${apiUrl}/api/dashboard/?date=${selectedDate}`).then((r) => r.json()),
      fetch(`${apiUrl}/api/modules/`).then((r) => r.json()),
    ]).then(([d, m]) => {
      setSummary(d.summary);
      setCustomModules(m);
    }).catch(() => {});
  }, [selectedDate]);

  const changeDate = (days: number) => {
    const d = new Date(selectedDate);
    d.setDate(d.getDate() + days);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (d <= today) {
      setSelectedDate(d.toISOString().split("T")[0]);
    }
  };

  const greeting = time.getHours() < 6 ? "İyi geceler" : time.getHours() < 12 ? "Günaydın" : time.getHours() < 18 ? "İyi günler" : "İyi akşamlar";

  const dateLabel = new Date(selectedDate).toLocaleDateString("tr-TR", {
    day: "numeric",
    month: "long",
    year: "numeric",
    weekday: "long",
  });

  const isToday = selectedDate === new Date().toISOString().split("T")[0];

  if (!unlocked) {
    return <PasswordGate onUnlock={() => setUnlocked(true)} />;
  }

  return (
    <div className="min-h-screen relative">
      <div className="gradient-bg" />
      <div className="noise" />

      <main className="relative z-10 max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-2">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">
                {greeting}, Joshua
              </h1>
            </div>
            <div className="text-right">
              <div className="mono text-2xl text-neon">
                {time.toLocaleTimeString("tr-TR")}
              </div>
            </div>
          </div>

          {/* Date Navigator */}
          <div className="flex items-center justify-between mt-4 mb-4">
            <button
              onClick={() => changeDate(-1)}
              className="glass px-4 py-2 text-sm hover:bg-surface-light transition-colors"
            >
              ← Önceki
            </button>
            <div className="text-center">
              <span className="text-lg font-medium">{dateLabel}</span>
              {!isToday && (
                <button
                  onClick={() => setSelectedDate(new Date().toISOString().split("T")[0])}
                  className="block text-xs text-accent mt-1 hover:underline"
                >
                  Bugüne dön
                </button>
              )}
            </div>
            <button
              onClick={() => changeDate(1)}
              disabled={isToday}
              className="glass px-4 py-2 text-sm hover:bg-surface-light transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            >
              Sonraki →
            </button>
          </div>

          {/* Tab Navigation */}
          <div className="flex gap-2 mt-4">
            <Link href="/" className="px-4 py-2 rounded-lg bg-accent/20 text-accent text-sm font-medium border border-accent/30">
              Dashboard
            </Link>
            <Link href="/charts" className="px-4 py-2 rounded-lg glass text-gray-400 text-sm hover:text-white transition-colors">
              Grafikler
            </Link>
            <Link href="/settings" className="px-4 py-2 rounded-lg glass text-gray-400 text-sm hover:text-white transition-colors">
              Ayarlar
            </Link>
          </div>

          {/* Quick Stats */}
          {summary && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="flex gap-6 mt-4 text-xs mono text-gray-500"
            >
              <span>💰 {summary.balance} TL</span>
              <span>📚 {(summary.study_minutes / 60).toFixed(1)} saat</span>
              <span>✅ {summary.habits_completed}/{summary.habits_total}</span>
              {summary.sleep && (
                <span>😴 {summary.sleep.sleep_time} → {summary.sleep.wake_time}</span>
              )}
            </motion.div>
          )}
        </motion.header>

        {/* Module Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <DailyPlanModule date={selectedDate} />
          <BudgetModule date={selectedDate} />
          <StudyModule date={selectedDate} />
          <SleepModule date={selectedDate} />
          <HabitModule date={selectedDate} />
          <GoalsModule />
          <IncomeModule />
          <SocialModule />
          {customModules.map((mod) => (
            <CustomModuleCard key={mod.module_key} module={mod} />
          ))}
        </div>

        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-12 text-center text-xs text-gray-700"
        >
          Telegram botu ile güncelle · Veriler Supabase'de saklanır
        </motion.footer>
      </main>
    </div>
  );
}
