"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import ModuleCard from "@/components/ModuleCard";

export default function SocialModule() {
  const [notes, setNotes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.social().then((n) => {
      setNotes(Array.isArray(n) ? n.slice(0, 5) : []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return <ModuleCard title="Sosyal" emoji="👥" value="..." />;

  return (
    <ModuleCard
      title="Sosyal"
      emoji="👥"
      value={`${notes.length} not`}
      size="sm"
      accentColor="neon-pink"
    >
      <div className="mt-3 space-y-2">
        {notes.map((note) => (
          <div key={note.id} className="text-xs py-1 border-b border-gray-800">
            <div className="flex justify-between">
              <span className="text-gray-300">{note.person_name}</span>
              <span className="text-gray-600">{note.date}</span>
            </div>
            <p className="text-gray-500 mt-0.5 line-clamp-2">{note.note}</p>
            {note.tags?.length > 0 && (
              <div className="flex gap-1 mt-1">
                {note.tags.map((tag: string, i: number) => (
                  <span key={i} className="text-[10px] bg-gray-800 text-gray-400 px-1.5 py-0.5 rounded">
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </ModuleCard>
  );
}
