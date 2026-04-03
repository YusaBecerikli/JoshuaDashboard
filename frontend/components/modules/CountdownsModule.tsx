"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import ModuleCard from "@/components/ModuleCard";

export default function CountdownsModule() {
  const [countdowns, setCountdowns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.countdowns().then((c) => {
      setCountdowns(Array.isArray(c) ? c : []);
      setLoading(false);
    }).catch(() => {
      setCountdowns([]);
      setLoading(false);
    });
  }, []);

  if (loading) return <ModuleCard title="Geri Sayım" emoji="⏳" value="..." />;

  return (
    <ModuleCard
      title="Geri Sayım"
      emoji="⏳"
      value={`${countdowns.length} aktif`}
      size="sm"
      accentColor="neon-orange"
    >
      <div className="mt-3 space-y-2">
        {countdowns.map((c) => {
          const days = Math.ceil((new Date(c.target_date).getTime() - Date.now()) / 86400000);
          const isPast = days < 0;
          return (
            <div key={c.id} className="flex justify-between text-xs py-1 border-b border-gray-800">
              <span className="text-gray-300">{c.emoji} {c.title}</span>
              <span className={`mono ${isPast ? "text-gray-600" : days <= 7 ? "text-neon-pink" : days <= 30 ? "text-neon-yellow" : "text-neon-green"}`}>
                {isPast ? "Tamamlandı" : `${days} gün`}
              </span>
            </div>
          );
        })}
        {countdowns.length === 0 && (
          <p className="text-xs text-gray-600 text-center py-4">Geri sayım yok. Telegram'dan ekle!</p>
        )}
      </div>
    </ModuleCard>
  );
}
