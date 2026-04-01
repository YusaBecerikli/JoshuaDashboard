"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine
} from "recharts";
import { api } from "@/lib/api";

export default function ChartsPage() {
  const [sleepData, setSleepData] = useState<any[]>([]);
  const [studyData, setStudyData] = useState<any[]>([]);
  const [tytScores, setTytScores] = useState<any[]>([]);
  const [aytScores, setAytScores] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.chartSleep(),
      api.chartStudy(),
      api.tytScores(),
      api.aytScores(),
    ]).then(([sleep, study, tyt, ayt]) => {
      setSleepData(sleep || []);
      setStudyData(study || []);
      setTytScores(tyt || []);
      setAytScores(ayt || []);
      setLoading(false);
    });
  }, []);

  const formatChartDate = (d: string) => {
    if (!d) return "";
    const parts = d.split("-");
    return `${parts[1]}/${parts[2]}`;
  };

  const processTytChart = () => {
    const byDate: any = {};
    tytScores.forEach((s: any) => {
      if (!byDate[s.date]) byDate[s.date] = { date: formatChartDate(s.date) };
      byDate[s.date][s.subject] = s.net_score;
    });
    return Object.values(byDate);
  };

  const processAytChart = () => {
    const byDate: any = {};
    aytScores.forEach((s: any) => {
      if (!byDate[s.date]) byDate[s.date] = { date: formatChartDate(s.date) };
      byDate[s.date][s.subject] = s.net_score;
    });
    return Object.values(byDate);
  };

  const sleepAvg = sleepData.length > 0
    ? (sleepData.filter((d: any) => d.duration_hours).reduce((s: number, d: any) => s + d.duration_hours, 0) / sleepData.filter((d: any) => d.duration_hours).length).toFixed(1)
    : 0;

  if (loading) return <div className="min-h-screen flex items-center justify-center text-gray-500">Yükleniyor...</div>;

  return (
    <div className="min-h-screen relative">
      <div className="gradient-bg" />
      <div className="noise" />

      <main className="relative z-10 max-w-7xl mx-auto px-4 py-8">
        <motion.header initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent mb-4">
            Grafikler
          </h1>
          <div className="flex gap-2">
            <Link href="/" className="px-4 py-2 rounded-lg glass text-gray-400 text-sm hover:text-white transition-colors">
              Dashboard
            </Link>
            <Link href="/charts" className="px-4 py-2 rounded-lg bg-accent/20 text-accent text-sm font-medium border border-accent/30">
              Grafikler
            </Link>
            <Link href="/settings" className="px-4 py-2 rounded-lg glass text-gray-400 text-sm hover:text-white transition-colors">
              Ayarlar
            </Link>
          </div>
        </motion.header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Uyku Grafiği */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass p-5">
            <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">😴 Uyku (Son 30 gün)</h3>
            <p className="text-xs text-gray-500 mb-4">Ortalama: {sleepAvg} saat</p>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={sleepData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
                <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#6b7280" }} />
                <YAxis tick={{ fontSize: 10, fill: "#6b7280" }} domain={[0, 12]} />
                <Tooltip contentStyle={{ background: "#12121a", border: "1px solid #2a2a3e", borderRadius: "8px" }} />
                <ReferenceLine y={parseFloat(sleepAvg)} stroke="#b44aff" strokeDasharray="3 3" label={{ value: `Ort: ${sleepAvg}`, fill: "#b44aff", fontSize: 10 }} />
                <Line type="monotone" dataKey="duration_hours" stroke="#b44aff" strokeWidth={2} dot={{ fill: "#b44aff", r: 3 }} name="Saat" />
              </LineChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Çalışma Grafiği */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass p-5">
            <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">📚 Günlük Çalışma (dakika)</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={studyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
                <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#6b7280" }} />
                <YAxis tick={{ fontSize: 10, fill: "#6b7280" }} />
                <Tooltip contentStyle={{ background: "#12121a", border: "1px solid #2a2a3e", borderRadius: "8px" }} />
                <Bar dataKey="total_minutes" fill="#00f0ff" radius={[4, 4, 0, 0]} name="Dakika" />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>

          {/* TYT Net Grafiği */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass p-5">
            <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">📝 TYT Netleri</h3>
            {processTytChart().length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={processTytChart()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
                  <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#6b7280" }} />
                  <YAxis tick={{ fontSize: 10, fill: "#6b7280" }} domain={[0, 40]} />
                  <Tooltip contentStyle={{ background: "#12121a", border: "1px solid #2a2a3e", borderRadius: "8px" }} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Line type="monotone" dataKey="Türkçe" stroke="#6366f1" strokeWidth={2} dot={{ r: 3 }} />
                  <Line type="monotone" dataKey="Matematik" stroke="#00f0ff" strokeWidth={2} dot={{ r: 3 }} />
                  <Line type="monotone" dataKey="Fen Bilimleri" stroke="#00ff88" strokeWidth={2} dot={{ r: 3 }} />
                  <Line type="monotone" dataKey="Sosyal Bilimler" stroke="#ff8c00" strokeWidth={2} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-center text-gray-600 py-12 text-sm">Henüz TYT net kaydı yok. Telegram'dan ekle!</p>
            )}
          </motion.div>

          {/* AYT Net Grafiği */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="glass p-5">
            <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">📝 AYT Netleri</h3>
            {processAytChart().length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={processAytChart()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
                  <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#6b7280" }} />
                  <YAxis tick={{ fontSize: 10, fill: "#6b7280" }} domain={[0, 40]} />
                  <Tooltip contentStyle={{ background: "#12121a", border: "1px solid #2a2a3e", borderRadius: "8px" }} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Line type="monotone" dataKey="Matematik" stroke="#6366f1" strokeWidth={2} dot={{ r: 3 }} />
                  <Line type="monotone" dataKey="Fizik" stroke="#b44aff" strokeWidth={2} dot={{ r: 3 }} />
                  <Line type="monotone" dataKey="Kimya" stroke="#ff006e" strokeWidth={2} dot={{ r: 3 }} />
                  <Line type="monotone" dataKey="Biyoloji" stroke="#00ff88" strokeWidth={2} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-center text-gray-600 py-12 text-sm">Henüz AYT net kaydı yok. Telegram'dan ekle!</p>
            )}
          </motion.div>
        </div>
      </main>
    </div>
  );
}
