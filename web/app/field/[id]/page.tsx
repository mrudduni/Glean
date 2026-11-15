import { notFound } from "next/navigation";
import { FieldWorkspace } from "@/components/FieldWorkspace";
import type { FieldId } from "@/lib/types";

export default async function FieldPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!["f1", "f2", "f3"].includes(id)) notFound();
  return <FieldWorkspace fieldId={id as FieldId} />;
}
