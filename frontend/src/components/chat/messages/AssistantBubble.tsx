"use client";

import { motion } from "framer-motion";

import type { ChatMessage } from "../MainChatArea";
import { MarkdownRenderer } from "./MarkdownRenderer";
import { MessageActions } from "./MessageActions";
import { BrandAvatar } from "@/constants/BrandAvatar";

interface Props {
  message: ChatMessage;
  grouped?: boolean;
}

export function AssistantBubble({
  message,
  grouped = false,
}: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={grouped ? "ml-12" : ""}
    >
      <div className="flex items-start gap-4">
        {/* Avatar */}
        {!grouped ? (
          <div
            className="
              flex
              h-9
              w-9
              shrink-0
              items-center
              justify-center
              rounded-full
              border
              border-[#3A3A3A]
              bg-[#2A2A2A]
              text-sm
              font-semibold
              text-white
            "
          >
            <BrandAvatar />
          </div>
        ) : (
          <div className="w-9 shrink-0" />
        )}

        {/* Message */}
        <div className="group min-w-0 flex-1">
          <div
            className="
              rounded-2xl
              px-1
              py-1
            "
          >
            <MarkdownRenderer
              content={message.content}
            />
          </div>

          {/* Actions */}
          <div
            className="
              mt-2
              opacity-0
              transition-opacity
              duration-200
              group-hover:opacity-100
            "
          >
            <MessageActions
              text={message.content}
              hasSources={Boolean(message.citations?.length)}
            />
          </div>
        </div>
      </div>
    </motion.div>
  );
}