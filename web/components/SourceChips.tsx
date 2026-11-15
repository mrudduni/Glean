"use client";

import type { SourceTag, SourcesFile } from "@/lib/types";

/** Source tag chips; hover shows the dataset name, click opens its URL. Unknown tags render as plain chips. */
export function SourceChips({ tags, sources }: { tags: SourceTag[]; sources: SourcesFile }) {
  if (!tags.length) return null;
  return (
    <span className="source-chips">
      {[...new Set(tags)].map((tag) => {
        const source = sources.sources.find((item) => item.tag === tag);
        return source ? (
          <a className="source-chip" href={source.url} key={tag} target="_blank" rel="noreferrer" title={`${source.name}. ${source.provider}`}>
            {tag}
          </a>
        ) : (
          <span className="source-chip" key={tag} title={tag === "MODEL" ? "Field Shift model estimate" : tag}>{tag}</span>
        );
      })}
    </span>
  );
}
