"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, Search, Briefcase, MapPin, Clock, Users } from "lucide-react";
import Link from "next/link";
import { jobsApi } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import { cn, formatSalary, formatRelativeDate, getStatusColor } from "@/lib/utils";

export default function JobsPage() {
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.jobs.list({ status: statusFilter !== "all" ? statusFilter : undefined, page }),
    queryFn: () =>
      jobsApi.list({ status: statusFilter !== "all" ? statusFilter : undefined, page, limit: 12 }),
  });

  const filtered = data?.items.filter(
    (j) => !searchQuery || j.title.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Jobs</h1>
          <p className="text-muted-foreground text-sm mt-0.5">
            {data?.total ?? 0} total job postings
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

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search jobs..."
            className="w-full h-10 pl-9 pr-4 rounded-lg bg-secondary/50 border border-border text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all"
          />
        </div>
        <div className="flex gap-2">
          {["all", "open", "draft", "closed"].map((s) => (
            <button
              key={s}
              onClick={() => { setStatusFilter(s); setPage(1); }}
              className={cn(
                "px-3 py-2 rounded-lg text-sm font-medium capitalize transition-all",
                statusFilter === s
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary/50 text-muted-foreground hover:text-foreground hover:bg-secondary",
              )}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Job cards grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="glass-card p-5 space-y-3">
              <div className="skeleton h-5 w-48 rounded" />
              <div className="skeleton h-4 w-32 rounded" />
              <div className="flex gap-2">
                <div className="skeleton h-6 w-16 rounded-full" />
                <div className="skeleton h-6 w-20 rounded-full" />
              </div>
              <div className="skeleton h-4 w-full rounded" />
            </div>
          ))}
        </div>
      ) : filtered?.length === 0 ? (
        <div className="glass-card py-16 text-center">
          <Briefcase className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
          <p className="text-foreground font-medium">No jobs found</p>
          <p className="text-muted-foreground text-sm mt-1">
            {searchQuery ? "Try a different search term" : "Create your first job posting"}
          </p>
          {!searchQuery && (
            <Link
              href="/jobs/create"
              className="inline-flex items-center gap-2 mt-4 px-4 py-2 rounded-lg bg-primary/10 text-primary text-sm hover:bg-primary/20 transition-colors"
            >
              <Plus className="w-4 h-4" /> Post a Job
            </Link>
          )}
        </div>
      ) : (
        <AnimatePresence mode="popLayout">
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {filtered?.map((job, i) => (
              <motion.div
                key={job.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ delay: i * 0.04 }}
              >
                <Link href={`/jobs/${job.id}`}>
                  <div className="glass-card p-5 hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5 transition-all group h-full">
                    {/* Header */}
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors line-clamp-1">
                          {job.title}
                        </h3>
                        <p className="text-sm text-muted-foreground mt-0.5">
                          {job.department ?? "General"}
                        </p>
                      </div>
                      <span
                        className={cn(
                          "text-[11px] font-medium px-2 py-0.5 rounded-full border capitalize ml-2 flex-shrink-0",
                          getStatusColor(job.status),
                        )}
                      >
                        {job.status}
                      </span>
                    </div>

                    {/* Skills */}
                    {job.required_skills.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mb-3">
                        {job.required_skills.slice(0, 4).map((skill) => (
                          <span
                            key={skill}
                            className="text-[11px] px-2 py-0.5 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20 font-medium"
                          >
                            {skill}
                          </span>
                        ))}
                        {job.required_skills.length > 4 && (
                          <span className="text-[11px] px-2 py-0.5 rounded-md bg-secondary text-muted-foreground border border-border">
                            +{job.required_skills.length - 4}
                          </span>
                        )}
                      </div>
                    )}

                    {/* Meta */}
                    <div className="space-y-1.5 text-xs text-muted-foreground">
                      {job.location && (
                        <div className="flex items-center gap-1.5">
                          <MapPin className="w-3.5 h-3.5" />
                          {job.location}
                        </div>
                      )}
                      {(job.salary_min || job.salary_max) && (
                        <div className="flex items-center gap-1.5 text-foreground/60">
                          {formatSalary(job.salary_min, job.salary_max, job.currency)}
                        </div>
                      )}
                    </div>

                    {/* Footer */}
                    <div className="flex items-center justify-between mt-4 pt-4 border-t border-border/50">
                      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                        <Users className="w-3.5 h-3.5" />
                        {job.candidate_count} candidates
                      </div>
                      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                        <Clock className="w-3.5 h-3.5" />
                        {formatRelativeDate(job.created_at)}
                      </div>
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </AnimatePresence>
      )}

      {/* Pagination */}
      {data && data.pages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1.5 rounded-lg text-sm bg-secondary/50 text-muted-foreground hover:text-foreground disabled:opacity-40 transition-colors"
          >
            Previous
          </button>
          <span className="text-sm text-muted-foreground">
            Page {page} of {data.pages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(data.pages, p + 1))}
            disabled={page === data.pages}
            className="px-3 py-1.5 rounded-lg text-sm bg-secondary/50 text-muted-foreground hover:text-foreground disabled:opacity-40 transition-colors"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
