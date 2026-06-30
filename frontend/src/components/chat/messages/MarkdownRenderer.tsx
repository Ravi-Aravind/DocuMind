"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";

import { CodeBlock } from "./CodeBlock";

interface MarkdownRendererProps {
  content: string;
}

export function MarkdownRenderer({
  content,
}: MarkdownRendererProps) {
  return (
    <div
      className="
        prose
        prose-invert
        max-w-none

        prose-p:leading-8
        prose-p:text-[#ECECEC]

        prose-headings:text-white

        prose-strong:text-white

        prose-code:text-white

        prose-pre:bg-transparent

        prose-li:text-[#ECECEC]

        prose-a:text-blue-400

        prose-blockquote:border-l-[#444]
      "
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={{
          code(props) {
            const { className, children } = props;

            const match = /language-(\w+)/.exec(
              className || ""
            );

            if (!match) {
              return (
                <code className="rounded bg-[#2E2E2E] px-1 py-0.5">
                  {children}
                </code>
              );
            }

            return (
              <CodeBlock
                language={match[1]}
                code={String(children).replace(/\n$/, "")}
              />
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}