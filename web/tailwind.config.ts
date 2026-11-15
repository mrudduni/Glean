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
        crop: {
          corn: "var(--crop-corn)",
          soy: "var(--crop-soy)",
          wheat: "var(--crop-wheat)",
          sorghum: "var(--crop-sorghum)",
          cover: "var(--crop-cover)",
          bare: "var(--crop-bare)",
        },
      },
    },
  },
  plugins: [],
};

export default config;
