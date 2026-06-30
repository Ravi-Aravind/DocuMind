"use client";

import {
  ChevronDown,
  FolderOpen,
  Sparkles,
  MoreHorizontal,
} from "lucide-react";

export function ConversationHeader() {
  return (
    <header
      className="
        sticky
        top-0
        z-20

        border-b
        border-[#2E2E2E]

        bg-[#212121]/90
        backdrop-blur-xl
      "
    >
      <div
        className="
          mx-auto
          flex
          h-16
          max-w-6xl
          items-center
          justify-between
          px-6
        "
      >
        {/* Left */}

        <div className="flex items-center gap-4">

          <div>

            <h2
              className="
                text-[15px]
                font-semibold
                text-white
              "
            >
              New Conversation
            </h2>

            <div
              className="
                mt-0.5
                flex
                items-center
                gap-2

                text-xs

                text-[#8A8A8A]
              "
            >
              <FolderOpen size={13} />

              Default Workspace

            </div>

          </div>

        </div>

        {/* Right */}

        <div className="flex items-center gap-2">

          <button
            className="
              flex
              items-center
              gap-2

              rounded-xl

              border

              border-[#3A3A3A]

              bg-[#2A2A2A]

              px-3

              py-2

              text-sm

              text-[#ECECEC]

              transition

              hover:bg-[#343434]
            "
          >
            <Sparkles size={16} />

            GPT-4.1

            <ChevronDown size={15} />

          </button>

          <button
            className="
              flex
              h-10
              w-10
              items-center
              justify-center

              rounded-xl

              text-[#8A8A8A]

              transition

              hover:bg-[#2D2D2D]

              hover:text-white
            "
          >
            <MoreHorizontal size={18} />
          </button>

        </div>
      </div>
    </header>
  );
}