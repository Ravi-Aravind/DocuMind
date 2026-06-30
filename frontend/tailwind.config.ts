import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
    "./src/app/**/*.{js,ts,jsx,tsx}",
    "./src/components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        background: "#FFFFFF",
        surface: "#FAFAFA",
        card: "#FFFFFF",
        border: "#E5E5E5",
        text: "#111111",
        textMuted: "#6B7280",
        accent: "#000000",
        danger: "#DC2626",
        success: "#16A34A",
      },
      borderRadius: {
        lg: "12px",
        xl: "16px",
      },
      boxShadow: {
        subtle: "0 10px 30px rgba(0,0,0,0.06)",
      },
      spacing: {
        1: "4px",
        2: "8px",
        3: "12px",
        4: "16px",
        5: "20px",
        6: "24px",
      },
    },
  },
  plugins: [],
};

export default config;