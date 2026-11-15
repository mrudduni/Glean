"use client";

import type { CropId } from "@/lib/types";
import { cropColor } from "@/lib/theme";
import { cropLabel, type UI } from "@/lib/ui";

type Step = { crop: CropId; cover_after: CropId | null };

/** One chip per rotation step, coloured by crop; a cover crop after a step shows as a small "+ cover" chip. */
export function CropChips({ steps, ui }: { steps: Step[] | CropId[]; ui: Pick<UI, "crops" | "lang" | "t"> }) {
  const list: Step[] = steps.map((step) => (typeof step === "string" ? { crop: step, cover_after: null } : step));
  return (
    <div className="crop-chip-group">
      {list.map((step, index) => (
        <span key={`${step.crop}-${index}`} className="crop-chip-step">
          <span className="crop-chip" style={{ "--chip-color": cropColor(step.crop) } as React.CSSProperties}>{cropLabel(ui, step.crop)}</span>
          {step.cover_after && (
            <span className="crop-chip cover" style={{ "--chip-color": cropColor(step.cover_after) } as React.CSSProperties}>+ {cropLabel(ui, step.cover_after)}</span>
          )}
        </span>
      ))}
    </div>
  );
}
