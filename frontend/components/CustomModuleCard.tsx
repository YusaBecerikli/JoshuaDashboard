"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import ModuleCard from "@/components/ModuleCard";

export default function CustomModuleCard({ module }: { module: any }) {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [inputValue, setInputValue] = useState("");

  useEffect(() => {
    api.getModuleData(module.module_key).then((d) => {
      setData(Array.isArray(d) ? d : []);
      setLoading(false);
    }).catch(() => {
      setData([]);
      setLoading(false);
    });
  }, [module.module_key]);

  const handleAdd = async () => {
    if (!inputValue.trim()) return;
    try {
      const schema = module.schema || {};
      let payload: any = {};
      if (schema.type === "counter") {
        payload = { value: parseInt(inputValue) || 1 };
      } else if (schema.type === "text") {
        payload = { text: inputValue };
      } else {
        payload = { value: inputValue };
      }
      await api.addModuleData(module.module_key, payload);
      const updated = await api.getModuleData(module.module_key);
      setData(Array.isArray(updated) ? updated : []);
      setInputValue("");
    } catch (e) {
      console.error("Custom module add error:", e);
    }
  };

  const schema = module.schema || {};
  const todayData = data.filter((d: any) => d.date === new Date().toISOString().split("T")[0]);

  if (loading) return <ModuleCard title={module.title} emoji="📦" value="..." />;

  return (
    <ModuleCard
      title={module.title}
      emoji="📦"
      subtitle={module.description}
      size="sm"
      accentColor="neon-purple"
    >
      {schema.type === "counter" && todayData.length > 0 && (
        <div className="mono text-2xl text-neon-purple mt-2">
          {todayData.reduce((sum: number, d: any) => sum + (d.data?.value || 0), 0)} {schema.unit || ""}
        </div>
      )}
      {schema.type === "checkbox" && todayData.length > 0 && (
        <div className="mt-2 space-y-1">
          {todayData.map((d: any, i: number) => (
            <div key={i} className="text-xs text-neon-green">✓ {d.data?.text}</div>
          ))}
        </div>
      )}
      <div className="mt-3 flex gap-2">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAdd()}
          placeholder={schema.unit ? `${schema.unit}...` : "Ekle..."}
          className="flex-1 bg-gray-900 border border-gray-700 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-accent"
        />
        <button
          onClick={handleAdd}
          className="bg-accent/20 text-accent px-3 py-1 rounded text-xs hover:bg-accent/30 transition-colors"
        >
          +
        </button>
      </div>
    </ModuleCard>
  );
}
