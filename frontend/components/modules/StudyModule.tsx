"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import ModuleCard from "@/components/ModuleCard";

export default function StudyModule({ date }: { date?: string }) {
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.studySummary(date).then((s) => {
      setSummary(s);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [date]);

  if (loading) return <ModuleCard title="Çalışma" emoji="📚" value="..." />;

  return (
    <ModuleCard
      title="Çalışma"
      emoji="📚"
      value={`${summary?.total_hours || 0} saat`}
      subtitle={`Ortalama net: ${summary?.avg_net || 0}`}
      size="md"
      accentColor="neon"
    >
      <div className="space-y-2 mt-3">
        {summary?.by_subject && Object.entries(summary.by_subject).map(([subj, mins]) => (
          <div key={subj} className="flex justify-between text-xs">
            <span className="text-gray-400">{subj}</span>
            <span className="mono text-neon">{Math.round((mins as number) / 60 * 10) / 10} saat</span>
          </div>
        ))}
      </div>
      {summary?.recent?.length > 0 && (
        <div className="mt-3 space-y-1">
          {summary.recent.slice(0, 5).map((s: any, i: number) => (
            <div key={i} className="flex justify-between text-xs py-1 border-b border-gray-800">
              <span className="text-gray-400">{s.subject} {s.topic ? `— ${s.topic}` : ""}</span>
              <span className="mono text-neon">{s.duration_minutes}dk {s.net_count ? `| ${s.net_count} net` : ""}</span>
            </div>
          ))}
        </div>
      )}
    </ModuleCard>
  );
}
