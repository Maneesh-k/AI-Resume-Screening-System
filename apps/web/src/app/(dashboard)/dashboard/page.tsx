"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Briefcase, Users, TrendingUp, Zap, Plus, ArrowRight } from "lucide-react";
import Link from "next/link";
import { jobsApi } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import { formatRelativeDate, getStatusColor } from "@/lib/utils";
import { cn } from "@/lib/utils";

function StatCard({
  label,
  value,
  icon: Icon,
  trend,
  color,
}: {
  label: string;
  value: string | number;
  icon: React.ElementType;
  trend?: string;
  color: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-5 hover:border-border/80 transition-colors"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-muted-foreground font-medium">{label}</p>
          <p className="text-3xl font-bold text-foreground mt-1">{value}</p>
          {trend && <p className="text-xs text-emerald-400 mt-1">{trend}</p>}
        </div>
        <div className={cn("w-10 h-10 rounded-xl flex items-center justify-center", color)}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </motion.div>
  );
}

export default function DashboardPage() {
  const { data: jobsData, isLoading } = useQuery({
    queryKey: queryKeys.jobs.list(),
    queryFn: () => jobsApi.list({ limit: 5 }),
  });

  const openJobs = jobsData?.items.filter((j) => j.status === "open").length ?? 0;
  const totalCandidates = jobsData?.items.reduce((sum, j) => sum + j.candidate_count, 0) ?? 0;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground text-sm mt-0.5">
            Overview of your recruitment pipeline
          </p>
        </div>
        <Link
          href="/jobs/create"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Post a Job
        </Link>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Jobs"
          value={jobsData?.total ?? "—"}
          icon={Briefcase}
          trend="+3 this week"
          color="bg-blue-500/10 text-blue-400"
        />
        <StatCard
          label="Active Openings"
          value={openJobs}
          icon={Zap}
          color="bg-violet-500/10 text-violet-400"
        />
        <StatCard
          label="Candidates"
          value={totalCandidates}
          icon={Users}
          trend="Processing now"
          color="bg-emerald-500/10 text-emerald-400"
        />
        <StatCard
          label="Avg Match Score"
          value="84.2"
          icon={TrendingUp}
          trend="↑ 2.1 vs last week"
          color="bg-yellow-500/10 text-yellow-400"
        />
      </div>

      {/* Recent Jobs */}
      <div className="glass-card overflow-hidden">
        <div className="flex items-center justify-between p-5 border-b border-border">
          <h2 className="font-semibold text-foreground">Recent Jobs</h2>
          <Link
            href="/jobs"
            className="text-sm text-primary hover:underline flex items-center gap-1"
          >
            View all <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {isLoading ? (
          <div className="p-5 space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="flex items-center gap-4">
                <div className="skeleton h-9 w-9 rounded-lg" />
                <div className="flex-1 space-y-1.5">
                  <div className="skeleton h-4 w-48 rounded" />
                  <div className="skeleton h-3 w-32 rounded" />
                </div>
                <div className="skeleton h-5 w-16 rounded-full" />
              </div>
            ))}
          </div>
        ) : jobsData?.items.length === 0 ? (
          <div className="p-12 text-center">
            <Briefcase className="w-8 h-8 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground text-sm">No jobs yet</p>
            <Link
              href="/jobs/create"
              className="text-primary text-sm hover:underline mt-1 inline-block"
            >
              Create your first job posting
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-border">
            {jobsData?.items.map((job, i) => (
              <motion.div
                key={job.id}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className="flex items-center gap-4 p-4 hover:bg-secondary/30 transition-colors"
              >
                <div className="w-9 h-9 rounded-lg bg-blue-500/10 flex items-center justify-center flex-shrink-0">
                  <Briefcase className="w-4 h-4 text-blue-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <Link href={`/jobs/${job.id}`}>
                    <p className="text-sm font-medium text-foreground hover:text-primary transition-colors truncate">
                      {job.title}
                    </p>
                  </Link>
                  <p className="text-xs text-muted-foreground">
                    {job.department ?? "General"} · {formatRelativeDate(job.created_at)}
                  </p>
                </div>
                <div className="flex items-center gap-3 flex-shrink-0">
                  <span className="text-sm text-muted-foreground">
                    {job.candidate_count} candidates
                  </span>
                  <span
                    className={cn(
                      "text-[11px] font-medium px-2 py-0.5 rounded-full border capitalize",
                      getStatusColor(job.status),
                    )}
                  >
                    {job.status}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
