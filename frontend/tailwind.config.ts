import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#101820",
        paper: "#F4F6F5",
        blueprint: "#0F2438",
        "blueprint-deep": "#0A1826",
        line: "#3E6E8E",
        amber: "#E3A857",
        green: "#4FA080",
        red: "#C1443C",
        "text-lo": "#9FB4C4",
      },
      fontFamily: {
        grotesk: ["Space Grotesk", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"],
        sans: ["IBM Plex Sans", "sans-serif"],
      },
      backgroundImage: {
        blueprint:
          "linear-gradient(rgba(62,110,142,0.35) 1px, transparent 1px), linear-gradient(90deg, rgba(62,110,142,0.35) 1px, transparent 1px)",
      },
      backgroundSize: {
        grid: "28px 28px",
      },
    },
  },
  plugins: [],
};
export default config;
