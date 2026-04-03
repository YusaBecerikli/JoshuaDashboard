/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        accent: "#6366f1",
        "accent-light": "#818cf8",
        neon: "#00f0ff",
        "neon-pink": "#ff006e",
        "neon-green": "#00ff88",
        "neon-purple": "#b44aff",
        "neon-orange": "#ff8c00",
        "neon-yellow": "#ffd600",
        surface: {
          DEFAULT: "#12121a",
          light: "#1a1a2e",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};
