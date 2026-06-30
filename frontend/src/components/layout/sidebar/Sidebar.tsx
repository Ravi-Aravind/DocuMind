"use client";

import React from "react";
import { useAuth } from "@/context/auth-context";
import { useCollections, useQASessions } from "@/lib/hooks";
import {
  MessageSquare,
  Search,
  NotebookPen,
  FolderKanban,
  Hash,
  Clock,
} from "lucide-react";

interface SidebarProps {
  activeSessionId: string | null;
  onSelectSession: (sessionId: string | null) => void;
  onNewChat?: () => void;
  collapsed?: boolean;
}

export default function Sidebar({
  activeSessionId,
  onSelectSession,
  onNewChat,
  collapsed = false,
}: SidebarProps) {
  const { user } = useAuth();
  const { data: collections = [] } = useCollections();
  const { data: sessions = [] } = useQASessions();

  const userInitial =
    user?.email?.[0]?.toUpperCase() ??
    user?.full_name?.[0]?.toUpperCase() ??
    "U";

  const sidebarWidthClass = collapsed ? "w-[60px]" : "w-[260px]";

  return (
    <aside
      className={`
        ${sidebarWidthClass}
        h-full
        bg-[#0D0D0D]
        text-white
        flex
        flex-col
        overflow-hidden
      `}
      suppressHydrationWarning
    >
      {/* Logo */}

      <div className="shrink-0 border-b border-[#1E1E1E] px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white text-black font-semibold">
            D
          </div>

          {!collapsed && (
            <span className="text-lg font-semibold">
              DocuMind
            </span>
          )}
        </div>
      </div>

      {/* Scroll Area */}

      <div
        className="
          flex-1
          overflow-y-auto
          overflow-x-hidden
        "
      >
        {/* Primary */}

        <div className="py-3">
          <SidebarActionItem
            icon={MessageSquare}
            label="New Chat"
            collapsed={collapsed}
            onClick={() => {
              onNewChat?.();
              onSelectSession(null);
            }}
          />

          <SidebarActionItem
            icon={Search}
            label="Search"
            collapsed={collapsed}
          />

          <SidebarActionItem
            icon={NotebookPen}
            label="Notes"
            collapsed={collapsed}
          />

          <SidebarActionItem
            icon={FolderKanban}
            label="Workspace"
            collapsed={collapsed}
          />
        </div>

        {/* Collections */}

        {!collapsed && (
          <div className="px-4 pt-6">
            <p className="mb-2 text-xs uppercase tracking-wider text-[#6B7280]">
              Collections
            </p>

            <button
              className="
                mb-3
                w-full
                rounded-xl
                border
                border-[#343434]
                py-2
                text-sm
                hover:bg-[#202020]
              "
            >
              + New Collection
            </button>

            {collections.length === 0 && (
              <p className="text-sm text-[#777]">
                No collections yet
              </p>
            )}
          </div>
        )}

        {collections.map((collection) => (
          <SidebarNavItem
            key={collection.id}
            icon={Hash}
            label={collection.name}
            collapsed={collapsed}
          />
        ))}

        {/* Chats */}

        {!collapsed && (
          <div className="px-4 pt-8">
            <p className="mb-2 text-xs uppercase tracking-wider text-[#6B7280]">
              Recent Chats
            </p>
          </div>
        )}

        {sessions.length === 0 && !collapsed && (
          <p className="px-4 text-sm text-[#777]">
            No conversations yet
          </p>
        )}

        {sessions.map((session) => (
          <SidebarNavItem
            key={session.id}
            icon={Clock}
            label={session.title || "Untitled"}
            collapsed={collapsed}
            active={activeSessionId === session.id}
            onClick={() => onSelectSession(session.id)}
          />
        ))}

        <div className="h-6" />
      </div>

      {/* User */}

      <div className="shrink-0 border-t border-[#222] p-4">
        <div
          className="
            flex
            items-center
            gap-3
            rounded-xl
            bg-[#171717]
            p-3
            transition
            hover:bg-[#222]
          "
        >
          <div
            className="
              flex
              h-10
              w-10
              items-center
              justify-center
              rounded-full
              bg-[#2B2B2B]
              font-semibold
            "
          >
            {userInitial}
          </div>

          {!collapsed && (
            <div>
              <p className="text-sm font-medium">
                {user?.email ?? "Guest"}
              </p>

              <p className="text-xs text-[#777]">
                Account
              </p>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}

interface SidebarActionItemProps {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  collapsed: boolean;
  onClick?: () => void;
}

function SidebarActionItem({
  icon: Icon,
  label,
  collapsed,
  onClick,
}: SidebarActionItemProps) {
  return (
    <button
      type="button"
      className="w-full px-2"
      onClick={onClick}
    >
      <div className="flex items-center gap-2.5 rounded-xl px-2 py-1.5 text-[13px] text-[#E5E7EB] hover:bg-[#2d2d2d] transition-colors duration-150">
        <Icon className="h-4 w-4" />
        {!collapsed && <span>{label}</span>}
      </div>
    </button>
  );
}

interface SidebarNavItemProps {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  collapsed: boolean;
  active?: boolean;
  onClick?: () => void;
}

function SidebarNavItem({
  icon: Icon,
  label,
  collapsed,
  active = false,
  onClick,
}: SidebarNavItemProps) {
  return (
    <button
      type="button"
      className="w-full px-2"
      onClick={onClick}
    >
      <div
        className={[
          "flex items-center gap-2.5 rounded-xl px-2 py-1.5 text-[13px]",
          "transition-all duration-150",
          active
            ? "bg-[#1f1f1f] text-[#ECECEC] border-l-2 border-l-[#FFFFFF]"
            : "text-[#A1A1AA] hover:bg-[#2d2d2d]",
        ].join(" ")}
      >
        <Icon className="h-4 w-4" />
        {!collapsed && <span>{label}</span>}
      </div>
    </button>
  );
}