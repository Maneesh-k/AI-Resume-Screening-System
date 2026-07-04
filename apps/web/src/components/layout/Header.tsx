"use client";

import { useRouter } from "next/navigation";
import { LogOut, Bell } from "lucide-react";
import { useAuthStore } from "@/stores/auth.store";
import { toast } from "sonner";

export function Header() {
  const { user, logout } = useAuthStore();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    toast.success("Signed out successfully");
    router.push("/login");
  };

  return (
    <header className="h-16 border-b border-border bg-card/30 backdrop-blur-sm flex items-center px-6 gap-4 flex-shrink-0">
      <div className="flex-1" />

      <div className="flex items-center gap-3">
        {/* Notifications (placeholder) */}
        <button className="relative w-9 h-9 rounded-lg flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-secondary/50 transition-colors">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-primary rounded-full" />
        </button>

        {/* User avatar */}
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500/20 to-violet-500/20 border border-border flex items-center justify-center">
          <span className="text-xs font-semibold text-primary">
            {user?.name?.charAt(0).toUpperCase() ?? "U"}
          </span>
        </div>

        {/* Logout */}
        <button
          onClick={handleLogout}
          className="w-9 h-9 rounded-lg flex items-center justify-center text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
          title="Sign out"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
}
