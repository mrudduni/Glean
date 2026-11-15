import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "var(--ink)",
        muted: "var(--muted)",
        surface: "var(--surface)",
        canvas: "var(--canvas)",
        line: "var(--line)",
        crop: Object.fromEntries(["corn", "sorghum", "wheat", "soybean", "alfalfa", "triticale", "rye_cover", "cotton", "fallow", "bare"].map((id) => [id, `var(--crop-${id})`])),
      },
    },
  },
  plugins: [],
};

export default config;
