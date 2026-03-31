"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import ModuleCard from "@/components/ModuleCard";

interface BudgetEntry {
  id: number;
  type: string;
  category: string;
  amount: number;
  description: string;
  date: string;
}

export default function BudgetModule() {
  const [summary, setSummary] = useState<any>(null);
  const [recent, setRecent] = useState<BudgetEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.budgetSummary(), api.budget()]).then(([s, r]) => {
      setSummary(s);
      setRecent(r.slice(0, 5));
      setLoading(false);
    });
  }, []);

  if (loading) return <ModuleCard title="Bütçe" emoji="💰" value="..." />;

  return (
    <ModuleCard
      title="Bütçe"
      emoji="💰"
      value={`${summary?.balance.toLocaleString("tr-TR")} TL`}
      subtitle={`Gelir: ${summary?.total_income.toLocaleString("tr-TR")} | Gider: ${summary?.total_expense.toLocaleString("tr-TR")} TL`}
      size="md"
      accentColor="neon-green"
    >
      <div className="space-y-2 mt-3">
        {summary?.by_category && Object.entries(summary.by_category).map(([cat, amount]) => (
          <div key={cat} className="flex justify-between text-xs">
            <span className="text-gray-400">{cat}</span>
            <span className="mono text-neon-pink">{(amount as number).toLocaleString("tr-TR")} TL</span>
          </div>
        ))}
      </div>
      {recent.length > 0 && (
        <div className="mt-3 space-y-1">
          {recent.map((entry) => (
            <motion.div
              key={entry.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex justify-between text-xs py-1 border-b border-gray-800"
            >
              <span className="text-gray-400">{entry.category || entry.description}</span>
              <span className={`mono ${entry.type === "income" ? "text-neon-green" : "text-neon-pink"}`}>
                {entry.type === "income" ? "+" : "-"}{(entry.amount || 0).toLocaleString("tr-TR")} TL
              </span>
            </motion.div>
          ))}
        </div>
      )}
    </ModuleCard>
  );
}
