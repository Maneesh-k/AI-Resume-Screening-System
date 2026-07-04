import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getScoreColor(score: number): string {
  if (score >= 85) return "text-emerald-400";
  if (score >= 70) return "text-blue-400";
  if (score >= 55) return "text-yellow-400";
  return "text-red-400";
}

export function getScoreBadgeVariant(score: number): "excellent" | "good" | "average" | "poor" {
  if (score >= 85) return "excellent";
  if (score >= 70) return "good";
  if (score >= 55) return "average";
  return "poor";
}

export function getRecommendationColor(rec: string | null): string {
  if (!rec) return "text-muted-foreground";
  if (rec === "Highly Recommended") return "text-emerald-400";
  if (rec === "Recommended") return "text-blue-400";
  if (rec === "Maybe") return "text-yellow-400";
  return "text-red-400";
}

export function formatScore(score: number | null): string {
  if (score === null || score === undefined) return "—";
  return score.toFixed(1);
}

export function formatExperience(years: number | null): string {
  if (!years) return "N/A";
  if (years < 1) return "< 1 year";
  return `${years} yr${years !== 1 ? "s" : ""}`;
}

export function formatSalary(min: number | null, max: number | null, currency = "USD"): string {
  if (!min && !max) return "Not disclosed";
  const fmt = (n: number) =>
    new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 0 }).format(n);
  const symbol = currency === "USD" ? "$" : currency;
  if (min && max) return `${symbol}${fmt(min)} – ${symbol}${fmt(max)}`;
  if (min) return `${symbol}${fmt(min)}+`;
  return `Up to ${symbol}${fmt(max!)}`;
}

export function formatDate(dateStr: string): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(dateStr));
}

export function formatRelativeDate(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
  return `${Math.floor(diffDays / 365)} years ago`;
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    open: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20",
    closed: "text-red-400 bg-red-400/10 border-red-400/20",
    draft: "text-yellow-400 bg-yellow-400/10 border-yellow-400/20",
    pending: "text-yellow-400 bg-yellow-400/10 border-yellow-400/20",
    processing: "text-blue-400 bg-blue-400/10 border-blue-400/20",
    processed: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20",
    failed: "text-red-400 bg-red-400/10 border-red-400/20",
  };
  return colors[status] ?? "text-muted-foreground bg-muted border-border";
}

export function truncate(str: string, maxLen: number): string {
  if (str.length <= maxLen) return str;
  return str.slice(0, maxLen) + "...";
}
