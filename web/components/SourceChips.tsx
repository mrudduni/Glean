"use client";

import type { SourcesFile, Lang } from "@/lib/types";

export function SourceChips({ ids, sources, lang }: { ids: string[]; sources: SourcesFile; lang: Lang }) {
  if (!ids.length) return null;
  return (
    <span className="source-chips">
      {ids.map((id) => {
        const source = sources.sources[id];
        if (!source) return null;
        return (
          <a className="source-chip" href={source.url} key={id} target="_blank" rel="noreferrer" title={source.role[lang] || source.role.en}>
            {source.name[lang] || source.name.en}
          </a>
        );
      })}
    </span>
  );
}
