"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import ModuleCard from "@/components/ModuleCard";

export default function GoalsModule() {
  const [goals, setGoals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.goals().then((g) => {
      setGoals(g);
      setLoading(false);
    });
  }, []);

  if (loading) return <ModuleCard title="Hedefler" emoji="🎯" value="..." />;

  return (
    <ModuleCard
      title="Hedefler"
      emoji="🎯"
      value={`${goals.length} aktif`}
      size="md"
      accentColor="neon-orange"
    >
      <div className="mt-3 space-y-3">
        {goals.map((goal) => (
          <div key={goal.id} className="space-y-1">
            <div className="flex justify-between text-xs">
              <span className="text-gray-300">{goal.title}</span>
              <span className="mono text-neon-orange">{goal.progress}%</span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-1.5">
              <div
                className="bg-gradient-to-r from-neon-orange to-neon-pink h-1.5 rounded-full transition-all duration-500"
                style={{ width: `${goal.progress}%` }}
              />
            </div>
            {goal.deadline && (
              <span className="text-xs text-gray-600">Son: {goal.deadline}</span>
            )}
          </div>
        ))}
      </div>
    </ModuleCard>
  );
}
