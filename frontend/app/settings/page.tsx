"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { api } from "@/lib/api";

export default function SettingsPage() {
  const [authenticated, setAuthenticated] = useState(false);
  const [password, setPassword] = useState("");
  const [error, setError] = useState(false);
  const [systemPrompt, setSystemPrompt] = useState("");
  const [aiModel, setAiModel] = useState("llama-3.3-70b-versatile");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const models = [
    { value: "llama-3.3-70b-versatile", label: "Llama 3.3 70B (Varsayılan)" },
    { value: "llama-3.1-8b-instant", label: "Llama 3.1 8B (Hızlı)" },
    { value: "mixtral-8x7b-32768", label: "Mixtral 8x7B" },
    { value: "gemma2-9b-it", label: "Gemma 2 9B" },
    { value: "deepseek-r1-distill-llama-70b", label: "DeepSeek R1 Distill 70B" },
  ];

  useEffect(() => {
    if (localStorage.getItem("settings_unlocked") === "true") {
      setAuthenticated(true);
    }
  }, []);

  useEffect(() => {
    if (authenticated) {
      api.settings().then((s) => {
        setSystemPrompt(s.system_prompt || "");
        setAiModel(s.ai_model || "llama-3.3-70b-versatile");
      });
    }
  }, [authenticated]);

  const handlePassword = (e: React.FormEvent) => {
    e.preventDefault();
    if (password === process.env.NEXT_PUBLIC_SETTINGS_PASSWORD) {
      localStorage.setItem("settings_unlocked", "true");
      setAuthenticated(true);
    } else {
      setError(true);
      setTimeout(() => setError(false), 1000);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    await api.updateSetting({ key: "system_prompt", value: systemPrompt });
    await api.updateSetting({ key: "ai_model", value: aiModel });
    setSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  if (!authenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center relative">
        <div className="gradient-bg" />
        <div className="noise" />
        <motion.form
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          onSubmit={handlePassword}
          className="glass p-8 w-full max-w-sm relative z-10"
        >
          <h2 className="text-xl font-bold mb-4 text-center">⚙️ Ayarlar</h2>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Ayarlar şifresi..."
            autoFocus
            className={`w-full bg-gray-900 border ${error ? "border-neon-pink" : "border-gray-700"} rounded-lg px-4 py-3 text-white text-center mono focus:outline-none focus:border-accent transition-colors`}
          />
          {error && <p className="text-neon-pink text-xs mt-2 text-center">Yanlış şifre</p>}
          <button type="submit" className="w-full mt-4 bg-accent hover:bg-accent-light text-white py-3 rounded-lg font-medium transition-colors">
            Giriş
          </button>
          <Link href="/" className="block text-center text-xs text-gray-500 mt-4 hover:text-gray-300">
            ← Dashboard'a dön
          </Link>
        </motion.form>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative">
      <div className="gradient-bg" />
      <div className="noise" />

      <main className="relative z-10 max-w-3xl mx-auto px-4 py-8">
        <motion.header initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent mb-4">
            ⚙️ Ayarlar
          </h1>
          <div className="flex gap-2">
            <Link href="/" className="px-4 py-2 rounded-lg glass text-gray-400 text-sm hover:text-white transition-colors">
              Dashboard
            </Link>
            <Link href="/charts" className="px-4 py-2 rounded-lg glass text-gray-400 text-sm hover:text-white transition-colors">
              Grafikler
            </Link>
            <Link href="/settings" className="px-4 py-2 rounded-lg bg-accent/20 text-accent text-sm font-medium border border-accent/30">
              Ayarlar
            </Link>
          </div>
        </motion.header>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass p-6 mb-6">
          <h2 className="text-lg font-semibold mb-2">AI Modeli</h2>
          <p className="text-xs text-gray-500 mb-4">
            Botun kullandığı yapay zeka modeli. Değişiklikler anında uygulanır.
          </p>
          <select
            value={aiModel}
            onChange={(e) => setAiModel(e.target.value)}
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-sm text-white focus:outline-none focus:border-accent"
          >
            {models.map((m) => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass p-6">
          <h2 className="text-lg font-semibold mb-2">Sistem Promptu</h2>
          <p className="text-xs text-gray-500 mb-4">
            Telegram botunun AI davranışını belirler. Değişiklikler anında uygulanır.
          </p>
          <textarea
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            rows={20}
            className="w-full bg-gray-900 border border-gray-700 rounded-lg p-4 text-sm text-gray-300 mono focus:outline-none focus:border-accent resize-y"
            spellCheck={false}
          />
          <div className="flex items-center justify-between mt-4">
            <p className="text-xs text-gray-600">
              Supabase settings tablosuna kaydedilir
            </p>
            <button
              onClick={handleSave}
              disabled={saving}
              className={`px-6 py-2 rounded-lg font-medium transition-all ${
                saved
                  ? "bg-neon-green/20 text-neon-green"
                  : "bg-accent hover:bg-accent-light text-white"
              }`}
            >
              {saving ? "Kaydediliyor..." : saved ? "Kaydedildi ✓" : "Kaydet"}
            </button>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
