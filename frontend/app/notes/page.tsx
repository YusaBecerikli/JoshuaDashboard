"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { api } from "@/lib/api";

export default function NotesPage() {
  const [authenticated, setAuthenticated] = useState(false);
  const [notes, setNotes] = useState<any[]>([]);
  const [newNote, setNewNote] = useState("");
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (localStorage.getItem("dashboard_unlocked") === "true") {
      setAuthenticated(true);
    }
  }, []);

  useEffect(() => {
    if (!authenticated) return;
    api.notes().then((n) => {
      setNotes(Array.isArray(n) ? n : []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [authenticated]);

  const addNote = async () => {
    if (!newNote.trim()) return;
    try {
      const created = await api.addNote({ content: newNote });
      setNotes((prev) => [created, ...prev]);
      setNewNote("");
    } catch (err) {
      console.error(err);
    }
  };

  const deleteNote = async (id: number) => {
    try {
      await api.deleteNote(id);
      setNotes((prev) => prev.filter((n) => n.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const filtered = notes.filter(
    (n) =>
      (n.content || "").toLowerCase().includes(search.toLowerCase()) ||
      (n.tags || []).some((t: string) => t.toLowerCase().includes(search.toLowerCase()))
  );

  if (!authenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-500">
        <div className="text-center">
          <p className="mb-4">Notları görmek için önce giriş yapın.</p>
          <Link href="/" className="text-accent hover:underline">← Dashboard&apos;a dön</Link>
        </div>
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
            📝 Notlar
          </h1>
          <div className="flex gap-2">
            <Link href="/" className="px-4 py-2 rounded-lg glass text-gray-400 text-sm hover:text-white transition-colors">
              Dashboard
            </Link>
            <Link href="/charts" className="px-4 py-2 rounded-lg glass text-gray-400 text-sm hover:text-white transition-colors">
              Grafikler
            </Link>
            <Link href="/notes" className="px-4 py-2 rounded-lg bg-accent/20 text-accent text-sm font-medium border border-accent/30">
              Notlar
            </Link>
            <Link href="/settings" className="px-4 py-2 rounded-lg glass text-gray-400 text-sm hover:text-white transition-colors">
              Ayarlar
            </Link>
          </div>
        </motion.header>

        {/* Add Note */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass p-4 mb-6">
          <div className="flex gap-2">
            <input
              value={newNote}
              onChange={(e) => setNewNote(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && addNote()}
              placeholder="Yeni not..."
              className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-accent"
            />
            <button
              onClick={addNote}
              className="bg-accent hover:bg-accent-light text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              Ekle
            </button>
          </div>
        </motion.div>

        {/* Search */}
        <div className="mb-4">
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Notlarda ara..."
            className="w-full bg-gray-900/50 border border-gray-800 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-accent"
          />
        </div>

        {/* Notes List */}
        {loading ? (
          <p className="text-gray-500 text-center">Yükleniyor...</p>
        ) : filtered.length === 0 ? (
          <p className="text-gray-600 text-center py-8 text-sm">
            {search ? "Sonuç bulunamadı" : "Henüz not yok. Telegram'dan /not komutuyla veya yukarıdan ekle."}
          </p>
        ) : (
          <div className="space-y-3">
            {filtered.map((note, i) => (
              <motion.div
                key={note.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="glass p-4 group"
              >
                <p className="text-sm text-gray-300">{note.content}</p>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs text-gray-600">{note.created_at?.slice(0, 10)}</span>
                  <button
                    onClick={() => deleteNote(note.id)}
                    className="text-xs text-gray-600 hover:text-neon-pink transition-colors opacity-0 group-hover:opacity-100"
                  >
                    Sil
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
