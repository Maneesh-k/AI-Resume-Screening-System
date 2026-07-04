"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Briefcase,
  MapPin,
  Upload,
  Users,
  TrendingUp,
  ChevronRight,
} from "lucide-react";
import Link from "next/link";
import { jobsApi } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import { cn, formatScore, getScoreColor, getRecommendationColor, formatExperience, formatRelativeDate } from "@/lib/utils";
import { ResumeUploadZone } from "@/components/upload/ResumeUploadZone";
import type { RankedCandidate } from "@/types";

function ScoreRing({ score }: { score: number }) {
  const radius = 20;
  const circumference = 2 * Math.PI * radius;
  const filled = (score / 100) * circumference;

  return (
    <div className="relative w-14 h-14 flex-shrink-0">
      <svg className="w-full h-full -rotate-90" viewBox="0 0 48 48">
        <circle cx="24" cy="24" r={radius} fill="none" stroke="hsl(var(--border))" strokeWidth="4" />
        <circle
          cx="24" cy="24" r={radius} fill="none"
          stroke={score >= 85 ? "#34d399" : score >= 70 ? "#60a5fa" : score >= 55 ? "#fbbf24" : "#f87171"}
          strokeWidth="4"
          strokeDasharray={`${filled} ${circumference}`}
          strokeLinecap="round"
        />
      </svg>
      <span className={cn("absolute inset-0 flex items-center justify-center text-xs font-bold", getScoreColor(score))}>
        {Math.round(score)}
      </span>
    </div>
  );
}

function CandidateRow({ ranked, jobId }: { ranked: RankedCandidate; jobId: string }) {
  const { candidate, overall_score, recommendation, skill_gaps, ai_summary } = ranked;

  return (
    <Link href={`/jobs/${jobId}/candidates/${candidate.id}`}>
      <motion.div
        whileHover={{ backgroundColor: "hsl(var(--secondary) / 0.3)" }}
        className="flex items-center gap-4 px-5 py-4 border-b border-border/50 last:border-0 cursor-pointer transition-colors"
      >
        {/* Rank */}
        <span className="text-sm font-bold text-muted-foreground w-6 flex-shrink-0">
          #{ranked.rank}
        </span>

        {/* Score ring */}
        <ScoreRing score={overall_score} />

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <p className="font-medium text-foreground text-sm">{candidate.name ?? "Unknown"}</p>
            {recommendation && (
              <span className={cn("text-[11px] font-medium", getRecommendationColor(recommendation))}>
                {recommendation}
              </span>
            )}
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            {candidate.current_title ?? "N/A"} · {formatExperience(candidate.experience_years)}
          </p>
          {ai_summary && (
            <p className="text-xs text-muted-foreground/70 mt-1 line-clamp-1">{ai_summary}</p>
          )}
        </div>

        {/* Skills */}
        <div className="hidden lg:flex flex-wrap gap-1 max-w-[200px] flex-shrink-0">
          {candidate.skills.slice(0, 3).map((s) => (
            <span key={s.name} className="text-[11px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/15">
              {s.name}
            </span>
          ))}
        </div>

        {/* Skill gaps */}
        {skill_gaps.length > 0 && (
          <div className="hidden xl:flex flex-wrap gap-1 max-w-[150px] flex-shrink-0">
            {skill_gaps.slice(0, 2).map((g) => (
              <span key={g} className="text-[11px] px-1.5 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/15">
                Missing: {g}
              </span>
            ))}
          </div>
        )}

        <ChevronRight className="w-4 h-4 text-muted-foreground flex-shrink-0" />
      </motion.div>
    </Link>
  );
}

export default function JobDetailPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const [showUpload, setShowUpload] = useState(false);

  const { data: job, isLoading: jobLoading } = useQuery({
    queryKey: queryKeys.jobs.detail(jobId),
    queryFn: () => jobsApi.get(jobId),
  });

  const { data: ranked, isLoading: candidatesLoading, refetch } = useQuery({
    queryKey: queryKeys.jobs.candidates(jobId),
    queryFn: () => jobsApi.getRankedCandidates(jobId),
    enabled: !!jobId,
  });

  if (jobLoading) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="skeleton h-8 w-64 rounded" />
        <div className="glass-card p-6 space-y-4">
          <div className="skeleton h-6 w-48 rounded" />
          <div className="skeleton h-4 w-full rounded" />
          <div className="skeleton h-4 w-3/4 rounded" />
        </div>
      </div>
    );
  }

  if (!job) return <div className="text-muted-foreground">Job not found</div>;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link
          href="/jobs"
          className="w-9 h-9 rounded-lg flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-secondary/50 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <div className="flex-1 min-w-0">
          <h1 className="text-2xl font-bold truncate">{job.title}</h1>
          <div className="flex items-center gap-3 mt-1 text-sm text-muted-foreground">
            {job.department && (
              <span className="flex items-center gap-1">
                <Briefcase className="w-3.5 h-3.5" /> {job.department}
              </span>
            )}
            {job.location && (
              <span className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5" /> {job.location}
              </span>
            )}
            <span className="flex items-center gap-1">
              <Users className="w-3.5 h-3.5" /> {job.candidate_count} candidates
            </span>
          </div>
        </div>
        <button
          onClick={() => setShowUpload((v) => !v)}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors"
        >
          <Upload className="w-4 h-4" />
          Upload Resume
        </button>
      </div>

      {/* Upload zone */}
      {showUpload && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
        >
          <ResumeUploadZone
            jobId={jobId}
            onUploadComplete={() => {
              setShowUpload(false);
              setTimeout(() => refetch(), 3000);
            }}
          />
        </motion.div>
      )}

      {/* Skills */}
      <div className="glass-card p-5">
        <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3">
          Required Skills
        </h2>
        <div className="flex flex-wrap gap-2">
          {job.required_skills.map((skill) => (
            <span
              key={skill}
              className="text-sm px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 font-medium"
            >
              {skill}
            </span>
          ))}
          {job.preferred_skills.map((skill) => (
            <span
              key={skill}
              className="text-sm px-3 py-1 rounded-full bg-violet-500/10 text-violet-400 border border-violet-500/20 font-medium"
            >
              {skill}
            </span>
          ))}
        </div>
      </div>

      {/* Candidate ranking */}
      <div className="glass-card overflow-hidden">
        <div className="flex items-center justify-between p-5 border-b border-border">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-primary" />
            <h2 className="font-semibold">Ranked Candidates</h2>
            <span className="text-sm text-muted-foreground">({ranked?.length ?? 0})</span>
          </div>
          <p className="text-xs text-muted-foreground">Sorted by AI match score</p>
        </div>

        {candidatesLoading ? (
          <div className="divide-y divide-border/50">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex items-center gap-4 px-5 py-4">
                <div className="skeleton w-6 h-4 rounded" />
                <div className="skeleton w-14 h-14 rounded-full" />
                <div className="flex-1 space-y-1.5">
                  <div className="skeleton h-4 w-36 rounded" />
                  <div className="skeleton h-3 w-48 rounded" />
                </div>
              </div>
            ))}
          </div>
        ) : ranked?.length === 0 ? (
          <div className="py-16 text-center">
            <Users className="w-8 h-8 text-muted-foreground mx-auto mb-3" />
            <p className="text-foreground font-medium">No candidates yet</p>
            <p className="text-muted-foreground text-sm mt-1">
              Upload resumes to start AI screening
            </p>
          </div>
        ) : (
          <div>
            {ranked?.map((r) => (
              <CandidateRow key={r.candidate.id} ranked={r} jobId={jobId} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
