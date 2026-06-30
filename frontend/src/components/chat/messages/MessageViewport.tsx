"use client";

import { AnimatePresence, motion } from "framer-motion";
import type { ChatMessage } from "../MainChatArea";
import { MessageBubble } from "./MessageBubble";

interface MessageViewportProps {
  messages: ChatMessage[];
}

export function MessageViewport({
  messages,
}: MessageViewportProps) {
  return (
    <div
      className="
        mx-auto
        flex
        w-full
        max-w-5xl
        flex-col
        gap-6
        pb-8
      "
    >
      <AnimatePresence initial={false}>
        {messages.map((message, index) => {
          const previous = messages[index - 1];

          const groupWithPrevious =
            previous &&
            previous.role === message.role;

          return (
            <motion.div
              key={`${message.role}-${index}`}
              initial={{
                opacity: 0,
                y: 18,
              }}
              animate={{
                opacity: 1,
                y: 0,
              }}
              exit={{
                opacity: 0,
                y: -10,
              }}
              transition={{
                duration: 0.18,
                ease: "easeOut",
              }}
              className={
                message.role === "user"
                  ? "flex justify-end"
                  : "flex justify-start"
              }
            >
              <div
                className={
                  groupWithPrevious
                    ? "mt-1 w-full"
                    : "mt-5 w-full"
                }
              >
                <MessageBubble
                  message={message}
                  grouped={groupWithPrevious}
                />
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>

      {/* Scroll anchor */}
      <div id="conversation-bottom" />
    </div>
  );
}