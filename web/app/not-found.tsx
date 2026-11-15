import Link from "next/link";
import { ArrowLeft, Sprout } from "lucide-react";

export default function NotFound() {
  return (
    <div className="page-wrap" style={{ minHeight: "65vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", textAlign: "center", padding: "64px 20px" }}>
      <div className="brand-mark" style={{ width: 52, height: 52, borderRadius: 12, display: "inline-flex", alignItems: "center", justifyContent: "center", marginBottom: 24 }}>
        <Sprout size={26} />
      </div>
      <h1 style={{ fontFamily: "var(--font-serif)", fontSize: "clamp(2rem, 4vw, 3rem)", margin: "0 0 14px", color: "var(--ink)" }}>Field Not Found</h1>
      <p style={{ maxWidth: 460, color: "var(--muted)", margin: "0 0 32px", fontSize: 16 }}>
        The requested field workspace or page could not be located in this monitoring region.
      </p>
      <Link href="/" className="button-primary">
        <ArrowLeft size={16} /> Return to field explorer
      </Link>
    </div>
  );
}

