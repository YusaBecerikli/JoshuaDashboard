import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0a0a0f",
        surface: "#12121a",
        "surface-light": "#1a1a2e",
        accent: "#6366f1",
        "accent-light": "#818cf8",
        neon: "#00f0ff",
        "neon-purple": "#b44aff",
        "neon-green": "#00ff88",
        "neon-pink": "#ff006e",
        "neon-orange": "#ff8c00",
        "neon-yellow": "#ffd600",
      },
      fontFamily: {
        mono: ["'JetBrains Mono'", "monospace"],
        sans: ["'Inter'", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
