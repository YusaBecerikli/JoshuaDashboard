"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import ModuleCard from "@/components/ModuleCard";

const moodEmojis = ["", "😫", "😕", "😐", "🙂", "😊", "😄", "😁", "🤩", "🔥", "💯"];

export default function DailyPlanModule({ date }: { date?: string }) {
  const [plan, setPlan] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [tasks, setTasks] = useState<any[]>([]);

  useEffect(() => {
    api.daily(date).then((p) => {
      setPlan(p);
      setTasks(p.tasks || []);
      setLoading(false);
    });
  }, [date]);

  const toggleTask = async (index: number) => {
    const updated = tasks.map((t, i) => (i === index ? { ...t, done: !t.done } : t));
    setTasks(updated);
    await api.updateDaily({ ...plan, tasks: updated, date });
  };

  if (loading) return <ModuleCard title="Günlük Plan" emoji="📋" value="..." />;

  const done = tasks.filter((t) => t.done).length;

  return (
    <ModuleCard
      title="Günlük Plan"
      emoji="📋"
      value={`${done}/${tasks.length}`}
      subtitle={plan?.mood ? `${moodEmojis[plan.mood]} Ruh hali: ${plan.mood}/10` : ""}
      size="lg"
      accentColor="neon"
    >
      <div className="mt-3 space-y-2">
        {tasks.map((task, i) => (
          <button
            key={i}
            onClick={() => toggleTask(i)}
            className={`w-full flex items-center gap-3 text-sm py-2 px-3 rounded-lg transition-all ${
              task.done ? "bg-neon-green/10 text-gray-500 line-through" : "bg-gray-800/50 text-gray-300 hover:bg-gray-800"
            }`}
          >
            <span className={`text-xs mono ${task.priority === "high" ? "text-neon-pink" : task.priority === "medium" ? "text-neon-yellow" : "text-gray-500"}`}>
              {task.priority === "high" ? "!!" : task.priority === "medium" ? "!" : "-"}
            </span>
            <span className="flex-1 text-left">{task.title}</span>
            <span className="mono text-xs">{task.done ? "✓" : "○"}</span>
          </button>
        ))}
        {tasks.length === 0 && (
          <p className="text-xs text-gray-600 text-center py-4">Henüz görev yok. Telegram'dan ekle!</p>
        )}
      </div>
      {plan?.notes && (
        <p className="text-xs text-gray-500 mt-3 italic">{plan.notes}</p>
      )}
    </ModuleCard>
  );
}
