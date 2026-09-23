import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#070B14",
        foreground: "#F8FAFC",
        surface: {
          DEFAULT: "#0B1220",
          card: "#0F172A",
          hover: "#1E293B",
          border: "rgba(148, 163, 184, 0.12)",
        },
        brand: {
          blue: "#3B82F6",
          cyan: "#06B6D4",
          sky: "#38BDF8",
          indigo: "#6366F1",
          violet: "#8B5CF6",
        },
        status: {
          success: "#10B981",
          warning: "#F59E0B",
          error: "#EF4444",
          info: "#38BDF8",
        },
      },
      boxShadow: {
        glow: "0 0 25px -5px rgba(6, 182, 212, 0.25)",
        card: "0 10px 30px -10px rgba(0, 0, 0, 0.5)",
      },
      backgroundImage: {
        "radial-gradient": "radial-gradient(circle at 50% 0%, rgba(14, 165, 233, 0.15) 0%, rgba(7, 11, 20, 0) 70%)",
        "glass-gradient": "linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%)",
      },
    },
  },
  plugins: [],
};

export default config;
