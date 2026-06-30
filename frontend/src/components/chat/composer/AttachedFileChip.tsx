"use client";

import { FileText, X, CheckCircle2, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

interface AttachedFileChipProps {
  file: File;

  onRemove: () => void;

  uploading?: boolean;

  uploaded?: boolean;
}

export function AttachedFileChip({
  file,
  onRemove,
  uploading = false,
  uploaded = false,
}: AttachedFileChipProps) {
  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;

    if (bytes < 1024 * 1024)
      return `${(bytes / 1024).toFixed(1)} KB`;

    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

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
      exit={{
        opacity: 0,
        y: 10,
      }}
      transition={{
        duration: 0.18,
      }}
      className="
        flex
        items-center
        justify-between
        rounded-2xl
        border
        border-[#3A3A3A]
        bg-[#252525]
        px-4
        py-3
      "
    >
      <div className="flex items-center gap-3 min-w-0">

        <div
          className="
            flex
            h-10
            w-10
            items-center
            justify-center
            rounded-xl
            bg-[#333]
          "
        >
          <FileText
            size={18}
            className="text-[#ECECEC]"
          />
        </div>

        <div className="min-w-0">

          <div
            className="
              truncate
              text-sm
              font-medium
              text-white
            "
          >
            {file.name}
          </div>

          <div
            className="
              mt-0.5
              text-xs
              text-[#8B8B8B]
            "
          >
            {formatSize(file.size)}
          </div>

        </div>

      </div>

      <div className="flex items-center gap-2">

        {uploading && (
          <Loader2
            className="animate-spin text-[#A1A1AA]"
            size={16}
          />
        )}

        {uploaded && (
          <CheckCircle2
            size={16}
            className="text-green-500"
          />
        )}

        <button
          type="button"
          onClick={onRemove}
          aria-label="Remove file"
          className="
            rounded-lg
            p-1.5
            text-[#8B8B8B]
            transition-colors
            hover:bg-[#3A3A3A]
            hover:text-white
          "
        >
          <X size={16} />
        </button>

      </div>
    </motion.div>
  );
}