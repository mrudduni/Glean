import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function NotFound() {
  return (
    <div className="page-wrap state-page">
      <h1>Page not found</h1>
      <p>There is no page at this address.</p>
      <div className="state-actions">
        <Link href="/" className="button-primary"><ArrowLeft size={16} aria-hidden="true" />Back to the fields</Link>
      </div>
    </div>
  );
}
