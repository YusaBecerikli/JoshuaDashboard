"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import ModuleCard from "@/components/ModuleCard";

export default function IncomeModule() {
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.incomeSummary().then((s) => {
      setSummary(s);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return <ModuleCard title="Online Gelir" emoji="💻" value="..." />;

  return (
    <ModuleCard
      title="Online Gelir"
      emoji="💻"
      value={`${summary?.total?.toLocaleString("tr-TR") || 0} TL`}
      size="sm"
      accentColor="neon-yellow"
    >
      <div className="mt-3 space-y-2">
        {summary?.by_platform && Object.entries(summary.by_platform).map(([plat, amount]) => (
          <div key={plat} className="flex justify-between text-xs">
            <span className="text-gray-400">{plat}</span>
            <span className="mono text-neon-yellow">{(amount as number).toLocaleString("tr-TR")} TL</span>
          </div>
        ))}
      </div>
    </ModuleCard>
  );
}
