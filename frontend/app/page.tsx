"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import BudgetModule from "@/components/modules/BudgetModule";
import StudyModule from "@/components/modules/StudyModule";
import SleepModule from "@/components/modules/SleepModule";
import HabitModule from "@/components/modules/HabitModule";
import GoalsModule from "@/components/modules/GoalsModule";
import IncomeModule from "@/components/modules/IncomeModule";
import SocialModule from "@/components/modules/SocialModule";
import DailyPlanModule from "@/components/modules/DailyPlanModule";

export default function Home() {
  const [time, setTime] = useState(new Date());
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/dashboard/`)
      .then((r) => r.json())
      .then((d) => setSummary(d.summary))
      .catch(() => {});
  }, []);

  const greeting = time.getHours() < 6 ? "İyi geceler" : time.getHours() < 12 ? "Günaydın" : time.getHours() < 18 ? "İyi günler" : "İyi akşamlar";

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
              <p className="text-sm text-gray-500 mt-1">
                {time.toLocaleDateString("tr-TR", {
                  weekday: "long",
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </p>
            </div>
            <div className="text-right">
              <div className="mono text-2xl text-neon">
                {time.toLocaleTimeString("tr-TR")}
              </div>
            </div>
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
              <span>📚 {(summary.study_minutes / 60).toFixed(1)} saat çalışma</span>
              <span>✅ {summary.habits_completed}/{summary.habits_total} alışkanlık</span>
              {summary.sleep && (
                <span>😴 {summary.sleep.sleep_time} → {summary.sleep.wake_time}</span>
              )}
            </motion.div>
          )}
        </motion.header>

        {/* Module Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <DailyPlanModule />
          <BudgetModule />
          <StudyModule />
          <SleepModule />
          <HabitModule />
          <GoalsModule />
          <IncomeModule />
          <SocialModule />
        </div>

        {/* Footer */}
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
