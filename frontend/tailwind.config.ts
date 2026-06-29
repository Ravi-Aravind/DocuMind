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
        surface: "#F8F8F8",
        card: "#FFFFFF",
        border: "#E5E5E5",
        text: "#111111",
        textMuted: "#666666",
        accent: "#000000",
        hover: "#F2F2F2",
      },
      borderRadius: {
        lg: "12px",
        xl: "16px",
      },
      boxShadow: {
        subtle: "0 10px 30px rgba(0,0,0,0.06)",
      },
    },
  },
  plugins: [],
};

export default config;