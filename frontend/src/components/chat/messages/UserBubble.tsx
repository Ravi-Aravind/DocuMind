"use client";

import { motion } from "framer-motion";
import type { ChatMessage } from "../MainChatArea";

interface Props {
  message: ChatMessage;
  grouped?: boolean;
}

export function UserBubble({
  message,
}: Props) {
  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 10,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      className="flex justify-end"
    >
      <div
        className="
          max-w-[75%]
          rounded-[24px]
          bg-[#303030]
          px-5
          py-3
          text-[15px]
          leading-7
          text-white
          shadow-sm
        "
      >
        {message.content}
      </div>
    </motion.div>
  );
}