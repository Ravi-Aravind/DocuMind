"use client";

import type { SourceCitation } from "../MainChatArea";

interface CitationCardProps {
  citation: SourceCitation;
}

export function CitationCard({ citation }: CitationCardProps) {
  const { title, page, section, chunk_text } = citation;

  return (
    <div className="rounded-md bg-[#FAFAFA] px-3 py-2 text-xs">
      {title && (
        <p className="mb-0.5 font-medium text-[#111827]">
          {title}
          {page != null && ` p. ${page}`}
          {section && ` – ${section}`}
        </p>
      )}
      <p className="line-clamp-2 text-[#6B7280]">
        {chunk_text}
      </p>
    </div>
  );
}