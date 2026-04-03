"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import ModuleCard from "@/components/ModuleCard";

export default function SleepModule({ date }: { date?: string }) {
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.sleepSummary(date).then((s) => {
      setSummary(s);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [date]);

  if (loading) return <ModuleCard title="Uyku" emoji="😴" value="..." />;

  return (
    <ModuleCard
      title="Uyku"
      emoji="😴"
      value={`${summary?.avg_sleep_hours || 0} saat`}
      subtitle={`Kalite: ${summary?.avg_quality || 0}/10`}
      size="sm"
      accentColor="neon-purple"
    >
      {summary?.recent?.length > 0 && (
        <div className="mt-3 space-y-1">
          {summary.recent.slice(0, 5).map((s: any, i: number) => (
            <div key={i} className="flex justify-between text-xs py-1 border-b border-gray-800">
              <span className="text-gray-400">{s.date}</span>
              <span className="mono text-neon-purple">{s.sleep_time} → {s.wake_time} {s.quality ? `(${s.quality}/10)` : ""}</span>
            </div>
          ))}
        </div>
      )}
    </ModuleCard>
  );
}
