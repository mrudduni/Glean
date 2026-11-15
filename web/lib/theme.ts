import tokens from "@/styles/tokens.json";
import { tokensSchema } from "@/lib/schemas";

const parsed = tokensSchema.safeParse(tokens);
if (!parsed.success) {
  if (process.env.NODE_ENV === "development") console.error("Invalid data at /styles/tokens.json", parsed.error.issues);
  throw new Error("Data validation failed for /styles/tokens.json");
}

export const theme = parsed.data;
