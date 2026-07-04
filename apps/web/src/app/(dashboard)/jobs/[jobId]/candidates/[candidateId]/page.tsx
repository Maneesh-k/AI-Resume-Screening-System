"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  ArrowLeft, User, Briefcase, GraduationCap, Wrench,
  MessageSquare, ChevronDown, ChevronUp, Award, Target,
  TrendingUp, AlertTriangle
} from "lucide-react";
import Link from "next/link";
import { candidatesApi, aiApi } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import { cn, formatScore, getScoreColor, getRecommendationColor, formatExperience } from "@/lib/utils";
import { useState } from "react";
import type { InterviewQuestion } from "@/types";

function ScoreBar({ label, value }: { label: string; value: number | null }) {
  if (value === null) return null;
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-sm">
        <span className="text-muted-foreground">{label}</span>
        <span className={cn("font-semibold", getScoreColor(value))}>{formatScore(value)}</span>
      </div>
      <div className="h-1.5 rounded-full bg-secondary overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className={cn(
            "h-full rounded-full",
            value >= 85 ? "bg-emerald-400" : value >= 70 ? "bg-blue-400" : value >= 55 ? "bg-yellow-400" : "bg-red-400",
          )}
        />
      </div>
    </div>
  );
}

function QuestionCard({ q, index }: { q: InterviewQuestion; index: number }) {
  const [open, setOpen] = useState(false);
  const typeColors: Record<string, string> = {
    technical: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    behavioral: "bg-violet-500/10 text-violet-400 border-violet-500/20",
    system_design: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  };
  const diffColors: Record<string, string> = {
    easy: "text-emerald-400",
    medium: "text-yellow-400",
    hard: "text-red-400",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="glass-card overflow-hidden"
    >
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-start gap-3 p-4 text-left hover:bg-secondary/30 transition-colors"
      >
        <span className="text-sm font-bold text-muted-foreground w-5 flex-shrink-0 mt-0.5">
          {index + 1}.
        </span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1.5">
            <span className={cn("text-[11px] font-medium px-2 py-0.5 rounded border capitalize", typeColors[q.type] ?? "")}>
              {q.type.replace("_", " ")}
            </span>
            {q.difficulty && (
              <span className={cn("text-[11px] font-medium capitalize", diffColors[q.difficulty] ?? "")}>
                {q.difficulty}
              </span>
            )}
          </div>
          <p className="text-sm text-foreground font-medium leading-relaxed">{q.question}</p>
        </div>
        {open ? (
          <ChevronUp className="w-4 h-4 text-muted-foreground flex-shrink-0 mt-0.5" />
        ) : (
          <ChevronDown className="w-4 h-4 text-muted-foreground flex-shrink-0 mt-0.5" />
        )}
      </button>
      {open && q.rationale && (
        <div className="px-4 pb-4 pt-0 ml-8">
          <p className="text-xs text-muted-foreground bg-secondary/50 rounded-lg p-3 border border-border/50">
            <strong className="text-foreground/70">Why ask this:</strong> {q.rationale}
          </p>
        </div>
      )}
    </motion.div>
  );
}

export default function CandidateDetailPage() {
  const { jobId, candidateId } = useParams<{ jobId: string; candidateId: string }>();

  const { data: candidate, isLoading } = useQuery({
    queryKey: queryKeys.candidates.detail(candidateId),
    queryFn: () => candidatesApi.get(candidateId),
  });

  const { data: questions, isLoading: questionsLoading } = useQuery({
    queryKey: queryKeys.candidates.questions(candidateId, jobId),
    queryFn: () => aiApi.getQuestions(candidateId, jobId),
    enabled: !!candidate && candidate.processing_status === "processed",
  });

  const { data: skillGap } = useQuery({
    queryKey: queryKeys.candidates.skillGap(candidateId, jobId),
    queryFn: () => aiApi.getSkillGap(candidateId, jobId),
    enabled: !!candidate && candidate.processing_status === "processed",
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="skeleton h-8 w-64 rounded" />
        <div className="grid grid-cols-3 gap-6">
          <div className="col-span-2 space-y-4">
            <div className="glass-card p-6 space-y-3">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="skeleton h-4 rounded" />
              ))}
            </div>
          </div>
          <div className="glass-card p-6 space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="space-y-1">
                <div className="skeleton h-3 w-24 rounded" />
                <div className="skeleton h-2 rounded" />
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!candidate) return <div className="text-muted-foreground">Candidate not found</div>;

  const score = candidate.score;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link
          href={`/jobs/${jobId}`}
          className="w-9 h-9 rounded-lg flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-secondary/50 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500/20 to-violet-500/20 border border-border flex items-center justify-center">
              <User className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-bold">{candidate.name ?? "Unknown Candidate"}</h1>
              <p className="text-sm text-muted-foreground">
                {candidate.current_title ?? "N/A"} ·{" "}
                {candidate.current_company ?? "N/A"} ·{" "}
                {formatExperience(candidate.experience_years)}
              </p>
            </div>
          </div>
        </div>
        {score?.recommendation && (
          <div className={cn("px-4 py-1.5 rounded-full border text-sm font-semibold", getRecommendationColor(score.recommendation))}>
            {score.recommendation}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-6">
          {/* AI Summary */}
          {score?.ai_summary && (
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-5 h-5 rounded bg-violet-500/20 flex items-center justify-center">
                  <span className="text-[10px] font-bold text-violet-400">AI</span>
                </div>
                <h3 className="font-semibold text-sm">AI Summary</h3>
              </div>
              <p className="text-sm text-foreground/80 leading-relaxed">{score.ai_summary}</p>
            </motion.div>
          )}

          {/* Strengths & Concerns */}
          {score && (score.strengths?.length > 0 || score.concerns?.length > 0) && (
            <div className="grid grid-cols-2 gap-4">
              {score.strengths?.length > 0 && (
                <div className="glass-card p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Award className="w-4 h-4 text-emerald-400" />
                    <h3 className="text-sm font-semibold text-emerald-400">Strengths</h3>
                  </div>
                  <ul className="space-y-1.5">
                    {score.strengths.map((s, i) => (
                      <li key={i} className="text-xs text-foreground/80 flex items-start gap-2">
                        <span className="w-1 h-1 rounded-full bg-emerald-400 mt-1.5 flex-shrink-0" />
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {score.concerns?.length > 0 && (
                <div className="glass-card p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <AlertTriangle className="w-4 h-4 text-yellow-400" />
                    <h3 className="text-sm font-semibold text-yellow-400">Concerns</h3>
                  </div>
                  <ul className="space-y-1.5">
                    {score.concerns.map((c, i) => (
                      <li key={i} className="text-xs text-foreground/80 flex items-start gap-2">
                        <span className="w-1 h-1 rounded-full bg-yellow-400 mt-1.5 flex-shrink-0" />
                        {c}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Skills */}
          {candidate.skills.length > 0 && (
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card p-5">
              <div className="flex items-center gap-2 mb-4">
                <Wrench className="w-4 h-4 text-primary" />
                <h3 className="font-semibold">Skills</h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {candidate.skills.map((skill) => {
                  const isGap = skillGap?.missing_skills.includes(skill.name);
                  const isMatch = skillGap?.matching_skills.includes(skill.name);
                  return (
                    <span
                      key={skill.name}
                      className={cn(
                        "text-sm px-3 py-1 rounded-full border font-medium",
                        isMatch
                          ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                          : isGap
                          ? "bg-red-500/10 text-red-400 border-red-500/20"
                          : "bg-blue-500/10 text-blue-400 border-blue-500/20",
                      )}
                    >
                      {skill.name}
                    </span>
                  );
                })}
              </div>
            </motion.div>
          )}

          {/* Experience */}
          {candidate.experience.length > 0 && (
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="glass-card p-5">
              <div className="flex items-center gap-2 mb-4">
                <Briefcase className="w-4 h-4 text-primary" />
                <h3 className="font-semibold">Experience</h3>
              </div>
              <div className="space-y-4">
                {candidate.experience.map((exp, i) => (
                  <div key={i} className="flex gap-4">
                    <div className="flex flex-col items-center">
                      <div className="w-2 h-2 rounded-full bg-primary mt-1.5" />
                      {i < candidate.experience.length - 1 && (
                        <div className="w-0.5 flex-1 bg-border mt-1" />
                      )}
                    </div>
                    <div className="pb-4">
                      <p className="text-sm font-semibold text-foreground">{exp.title}</p>
                      <p className="text-sm text-muted-foreground">{exp.company}</p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {exp.start_date} — {exp.is_current ? "Present" : (exp.end_date ?? "N/A")}
                      </p>
                      {exp.description && (
                        <p className="text-xs text-foreground/60 mt-1 line-clamp-2">{exp.description}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Education */}
          {candidate.education.length > 0 && (
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card p-5">
              <div className="flex items-center gap-2 mb-4">
                <GraduationCap className="w-4 h-4 text-primary" />
                <h3 className="font-semibold">Education</h3>
              </div>
              <div className="space-y-3">
                {candidate.education.map((edu, i) => (
                  <div key={i}>
                    <p className="text-sm font-semibold text-foreground">{edu.degree} {edu.field ? `in ${edu.field}` : ""}</p>
                    <p className="text-sm text-muted-foreground">{edu.institution}</p>
                    {edu.graduation_year && (
                      <p className="text-xs text-muted-foreground">{edu.graduation_year}</p>
                    )}
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Interview Questions */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-primary" />
              <h3 className="font-semibold">Interview Questions</h3>
            </div>
            {questionsLoading ? (
              <div className="space-y-2">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="skeleton h-16 rounded-xl" />
                ))}
              </div>
            ) : questions && questions.length > 0 ? (
              <div className="space-y-2">
                {questions.map((q, i) => (
                  <QuestionCard key={i} q={q} index={i} />
                ))}
              </div>
            ) : (
              <div className="glass-card py-8 text-center text-sm text-muted-foreground">
                Questions will be generated once the resume is processed
              </div>
            )}
          </div>
        </div>

        {/* Score sidebar */}
        <div className="space-y-5">
          {/* Overall score */}
          {score && (
            <motion.div initial={{ opacity: 0, x: 8 }} animate={{ opacity: 1, x: 0 }} className="glass-card p-5">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="w-4 h-4 text-primary" />
                <h3 className="font-semibold text-sm">AI Score</h3>
              </div>

              {/* Big score */}
              <div className="text-center py-4">
                <div className={cn("text-5xl font-bold tabular-nums", getScoreColor(score.overall_score))}>
                  {Math.round(score.overall_score)}
                </div>
                <div className="text-xs text-muted-foreground mt-1">out of 100</div>
                {score.ai_confidence !== null && (
                  <div className="text-xs text-muted-foreground mt-0.5">
                    {Math.round((score.ai_confidence ?? 0) * 100)}% confidence
                  </div>
                )}
              </div>

              {/* Score breakdown */}
              <div className="space-y-3 border-t border-border pt-4">
                <ScoreBar label="Skills" value={score.skill_score} />
                <ScoreBar label="Experience" value={score.experience_score} />
                <ScoreBar label="Domain" value={score.domain_score} />
                <ScoreBar label="Education" value={score.education_score} />
                <ScoreBar label="Certifications" value={score.certification_score} />
              </div>

              {score.score_justification && (
                <p className="text-xs text-muted-foreground mt-4 pt-4 border-t border-border leading-relaxed">
                  {score.score_justification}
                </p>
              )}
            </motion.div>
          )}

          {/* Skill gap */}
          {skillGap && (
            <motion.div initial={{ opacity: 0, x: 8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }} className="glass-card p-5">
              <div className="flex items-center gap-2 mb-4">
                <Target className="w-4 h-4 text-primary" />
                <h3 className="font-semibold text-sm">Skill Gap</h3>
              </div>

              <div className="flex items-center gap-2 mb-3">
                <div className="flex-1 h-2 bg-secondary rounded-full overflow-hidden">
                  <div
                    className="h-full bg-emerald-400 rounded-full transition-all"
                    style={{ width: `${skillGap.match_percentage}%` }}
                  />
                </div>
                <span className="text-sm font-semibold text-emerald-400">
                  {skillGap.match_percentage.toFixed(0)}%
                </span>
              </div>

              {skillGap.missing_skills.length > 0 && (
                <div>
                  <p className="text-xs text-muted-foreground mb-2">Missing skills:</p>
                  <div className="flex flex-wrap gap-1.5">
                    {skillGap.missing_skills.map((s) => (
                      <span key={s} className="text-[11px] px-2 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/20">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}

          {/* Contact */}
          {(candidate.email || candidate.phone) && (
            <motion.div initial={{ opacity: 0, x: 8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }} className="glass-card p-5">
              <h3 className="font-semibold text-sm mb-3">Contact</h3>
              {candidate.email && (
                <a
                  href={`mailto:${candidate.email}`}
                  className="block text-sm text-primary hover:underline truncate"
                >
                  {candidate.email}
                </a>
              )}
              {candidate.phone && (
                <p className="text-sm text-muted-foreground mt-1">{candidate.phone}</p>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
