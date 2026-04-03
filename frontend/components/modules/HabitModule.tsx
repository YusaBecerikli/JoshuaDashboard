"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import ModuleCard from "@/components/ModuleCard";

export default function HabitModule({ date }: { date?: string }) {
  const [habits, setHabits] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.habits(date).then((h) => {
      setHabits(Array.isArray(h) ? h : []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [date]);

  const toggleHabit = async (id: number, current: boolean) => {
    try {
      await api.logHabit(id, { completed: !current, date });
      setHabits((prev) =>
        prev.map((h) => (h.id === id ? { ...h, completed_today: !current } : h))
      );
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <ModuleCard title="Alışkanlıklar" emoji="✅" value="..." />;

  const completed = habits.filter((h) => h.completed_today).length;

  return (
    <ModuleCard
      title="Alışkanlıklar"
      emoji="✅"
      value={`${completed}/${habits.length}`}
      subtitle={date || "Bugün"}
      size="sm"
      accentColor="neon-green"
    >
      <div className="mt-3 space-y-2">
        {habits.map((habit) => (
          <button
            key={habit.id}
            onClick={() => toggleHabit(habit.id, habit.completed_today)}
            className={`w-full flex items-center gap-2 text-xs py-1.5 px-2 rounded-lg transition-all ${
              habit.completed_today
                ? "bg-neon-green/10 text-neon-green"
                : "bg-gray-800/50 text-gray-500 hover:bg-gray-800"
            }`}
          >
            <span>{habit.emoji || "○"}</span>
            <span className="flex-1 text-left">{habit.name}</span>
            <span className="mono">{habit.completed_today ? "✓" : "○"}</span>
          </button>
        ))}
      </div>
    </ModuleCard>
  );
}
