"use client";

import { motion } from "framer-motion";

interface ModuleCardProps {
  title: string;
  emoji: string;
  value?: string | number;
  subtitle?: string;
  children?: React.ReactNode;
  size?: "sm" | "md" | "lg";
  accentColor?: string;
}

const colorMap: Record<string, string> = {
  accent: "from-indigo-500",
  "neon-green": "from-green-400",
  "neon-pink": "from-pink-500",
  "neon-purple": "from-purple-500",
  "neon-orange": "from-orange-500",
  "neon-yellow": "from-yellow-400",
  neon: "from-cyan-400",
};

export default function ModuleCard({
  title,
  emoji,
  value,
  subtitle,
  children,
  size = "md",
  accentColor = "accent",
}: ModuleCardProps) {
  const sizeClasses = {
    sm: "col-span-1",
    md: "col-span-1 md:col-span-2",
    lg: "col-span-1 md:col-span-2 lg:col-span-3",
  };

  const gradientFrom = colorMap[accentColor] || "from-indigo-500";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className={`glass p-5 ${sizeClasses[size]} relative overflow-hidden group`}
    >
      <div className={`absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r ${gradientFrom} to-transparent opacity-0 group-hover:opacity-100 transition-opacity`} />
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-xl">{emoji}</span>
          <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider">{title}</h3>
        </div>
      </div>
      {value !== undefined && (
        <div className="mono text-3xl font-semibold mb-1 text-white">{value}</div>
      )}
      {subtitle && (
        <div className="text-xs text-gray-500 mb-3">{subtitle}</div>
      )}
      {children}
    </motion.div>
  );
}
