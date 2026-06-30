"use client";

import { BRAND } from "@/constants/branding";

interface Props {
  size?: number;
}

export function BrandAvatar({
  size = 36,
}: Props) {
  return (
    <div
      style={{
        width: size,
        height: size,
      }}
      className="
        flex
        items-center
        justify-center

        rounded-full

        border

        border-[#3A3A3A]

        bg-[#2A2A2A]

        font-semibold

        text-white
      "
    >
      {BRAND.shortName}
    </div>
  );
}