"use client";

import { useAuthStore } from "@/stores/auth.store";
import { motion } from "framer-motion";
import { User, Shield, Bell } from "lucide-react";

export default function SettingsPage() {
  const { user } = useAuthStore();

  return (
    <div className="max-w-2xl space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-muted-foreground text-sm mt-0.5">Manage your account preferences</p>
      </div>

      {/* Profile */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-6"
      >
        <div className="flex items-center gap-3 mb-5">
          <User className="w-4 h-4 text-primary" />
          <h2 className="font-semibold">Profile</h2>
        </div>
        <div className="flex items-center gap-4 mb-5">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500/20 to-violet-500/20 border-2 border-border flex items-center justify-center text-2xl font-bold text-primary">
            {user?.name?.charAt(0).toUpperCase()}
          </div>
          <div>
            <p className="font-semibold text-foreground">{user?.name}</p>
            <p className="text-sm text-muted-foreground">{user?.email}</p>
            <span className="inline-block mt-1 text-[11px] font-medium px-2 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20 capitalize">
              {user?.role?.replace("_", " ")}
            </span>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-foreground/80">Full Name</label>
            <input
              defaultValue={user?.name ?? ""}
              className="w-full h-10 px-3 rounded-lg bg-secondary/50 border border-border text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-foreground/80">Email</label>
            <input
              defaultValue={user?.email ?? ""}
              disabled
              className="w-full h-10 px-3 rounded-lg bg-secondary/30 border border-border text-sm text-muted-foreground cursor-not-allowed"
            />
          </div>
        </div>
        <div className="mt-4 flex justify-end">
          <button className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors">
            Save Changes
          </button>
        </div>
      </motion.div>

      {/* Security */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
        className="glass-card p-6"
      >
        <div className="flex items-center gap-3 mb-5">
          <Shield className="w-4 h-4 text-primary" />
          <h2 className="font-semibold">Security</h2>
        </div>
        <div className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-foreground/80">Current Password</label>
            <input
              type="password"
              placeholder="••••••••"
              className="w-full h-10 px-3 rounded-lg bg-secondary/50 border border-border text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-foreground/80">New Password</label>
            <input
              type="password"
              placeholder="••••••••"
              className="w-full h-10 px-3 rounded-lg bg-secondary/50 border border-border text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
            />
          </div>
        </div>
        <div className="mt-4 flex justify-end">
          <button className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors">
            Update Password
          </button>
        </div>
      </motion.div>

      {/* Notifications */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass-card p-6"
      >
        <div className="flex items-center gap-3 mb-5">
          <Bell className="w-4 h-4 text-primary" />
          <h2 className="font-semibold">Notifications</h2>
        </div>
        {[
          { label: "Resume processed", desc: "When AI finishes analyzing a resume" },
          { label: "High match candidate", desc: "When a candidate scores above 85" },
          { label: "Job status updates", desc: "When a job is opened or closed" },
        ].map((item) => (
          <div key={item.label} className="flex items-center justify-between py-3 border-b border-border/50 last:border-0">
            <div>
              <p className="text-sm font-medium text-foreground">{item.label}</p>
              <p className="text-xs text-muted-foreground mt-0.5">{item.desc}</p>
            </div>
            <button
              role="switch"
              className="w-10 h-5 rounded-full bg-primary relative transition-colors"
            >
              <span className="absolute top-0.5 right-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform" />
            </button>
          </div>
        ))}
      </motion.div>
    </div>
  );
}
