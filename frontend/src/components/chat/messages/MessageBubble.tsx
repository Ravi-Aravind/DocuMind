"use client";

import type { ChatMessage } from "../MainChatArea";
import { AssistantBubble } from "./AssistantBubble";
import { UserBubble } from "./UserBubble";

interface MessageBubbleProps {
  message: ChatMessage;
  grouped?: boolean;
}

export function MessageBubble({
  message,
  grouped = false,
}: MessageBubbleProps) {
  switch (message.role) {
    case "assistant":
      return (
        <AssistantBubble
          message={message}
          grouped={grouped}
        />
      );

    case "user":
      return (
        <UserBubble
          message={message}
          grouped={grouped}
        />
      );

    default:
      return null;
  }
}