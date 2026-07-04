"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { ArrowLeft, Plus, X, Loader2 } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";
import { jobsApi } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";

const schema = z.object({
  title: z.string().min(3, "Title must be at least 3 characters"),
  description: z.string().min(50, "Description must be at least 50 characters"),
  department: z.string().optional(),
  experience_min: z.coerce.number().min(0).optional(),
  experience_max: z.coerce.number().min(0).optional(),
  location: z.string().optional(),
  salary_min: z.coerce.number().min(0).optional(),
  salary_max: z.coerce.number().min(0).optional(),
  currency: z.string().default("USD"),
});

type FormData = z.infer<typeof schema>;

function SkillInput({
  label,
  skills,
  onAdd,
  onRemove,
  placeholder,
}: {
  label: string;
  skills: string[];
  onAdd: (s: string) => void;
  onRemove: (s: string) => void;
  placeholder?: string;
}) {
  const [input, setInput] = useState("");

  const handleAdd = () => {
    const val = input.trim();
    if (val && !skills.includes(val)) {
      onAdd(val);
      setInput("");
    }
  };

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-foreground/80">{label}</label>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAdd())}
          placeholder={placeholder ?? "Type and press Enter"}
          className="flex-1 h-10 px-3 rounded-lg bg-secondary/50 border border-border text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all"
        />
        <button
          type="button"
          onClick={handleAdd}
          className="h-10 px-3 rounded-lg bg-primary/10 text-primary border border-primary/20 hover:bg-primary/20 transition-colors"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>
      {skills.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {skills.map((skill) => (
            <span
              key={skill}
              className="inline-flex items-center gap-1 text-[12px] px-2.5 py-1 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20"
            >
              {skill}
              <button onClick={() => onRemove(skill)} className="hover:text-destructive transition-colors">
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

export default function CreateJobPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [requiredSkills, setRequiredSkills] = useState<string[]>([]);
  const [preferredSkills, setPreferredSkills] = useState<string[]>([]);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const { mutate, isPending } = useMutation({
    mutationFn: (data: FormData) =>
      jobsApi.create({
        ...data,
        required_skills: requiredSkills,
        preferred_skills: preferredSkills,
      }),
    onSuccess: (job) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.jobs.all });
      toast.success("Job posted successfully!");
      router.push(`/jobs/${job.id}`);
    },
    onError: (err: Error) => toast.error(err.message),
  });

  return (
    <div className="max-w-3xl animate-fade-in">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Link
          href="/jobs"
          className="w-9 h-9 rounded-lg flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-secondary/50 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold">Post a New Job</h1>
          <p className="text-muted-foreground text-sm mt-0.5">
            Fill in the details to start receiving AI-screened candidates
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit((data) => mutate(data))} className="space-y-6">
        {/* Basic info */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6 space-y-5"
        >
          <h2 className="font-semibold text-foreground">Basic Information</h2>

          <div className="space-y-1.5">
            <label className="text-sm font-medium text-foreground/80">Job Title *</label>
            <input
              {...register("title")}
              placeholder="e.g. Senior Backend Engineer"
              className="w-full h-10 px-3 rounded-lg bg-secondary/50 border border-border text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all"
            />
            {errors.title && <p className="text-xs text-destructive">{errors.title.message}</p>}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-foreground/80">Department</label>
              <input
                {...register("department")}
                placeholder="e.g. Engineering"
                className="w-full h-10 px-3 rounded-lg bg-secondary/50 border border-border text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-foreground/80">Location</label>
              <input
                {...register("location")}
                placeholder="e.g. Remote, New York"
                className="w-full h-10 px-3 rounded-lg bg-secondary/50 border border-border text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium text-foreground/80">
              Job Description *{" "}
              <span className="text-muted-foreground font-normal">(min. 50 characters)</span>
            </label>
            <textarea
              {...register("description")}
              rows={8}
              placeholder="Describe the role, responsibilities, team, and what success looks like..."
              className="w-full px-3 py-2.5 rounded-lg bg-secondary/50 border border-border text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 resize-none transition-all"
            />
            {errors.description && (
              <p className="text-xs text-destructive">{errors.description.message}</p>
            )}
          </div>
        </motion.div>

        {/* Skills */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="glass-card p-6 space-y-5"
        >
          <h2 className="font-semibold text-foreground">Skills</h2>
          <SkillInput
            label="Required Skills *"
            skills={requiredSkills}
            onAdd={(s) => setRequiredSkills((p) => [...p, s])}
            onRemove={(s) => setRequiredSkills((p) => p.filter((x) => x !== s))}
            placeholder="e.g. Python, AWS, PostgreSQL"
          />
          <SkillInput
            label="Preferred Skills"
            skills={preferredSkills}
            onAdd={(s) => setPreferredSkills((p) => [...p, s])}
            onRemove={(s) => setPreferredSkills((p) => p.filter((x) => x !== s))}
            placeholder="e.g. Kubernetes, Terraform"
          />
        </motion.div>

        {/* Compensation & Experience */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-card p-6 space-y-5"
        >
          <h2 className="font-semibold text-foreground">Compensation & Experience</h2>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-foreground/80">Min Experience (years)</label>
              <input
                {...register("experience_min")}
                type="number"
                min={0}
                placeholder="0"
                className="w-full h-10 px-3 rounded-lg bg-secondary/50 border border-border text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-foreground/80">Max Experience (years)</label>
              <input
                {...register("experience_max")}
                type="number"
                min={0}
                placeholder="10"
                className="w-full h-10 px-3 rounded-lg bg-secondary/50 border border-border text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-foreground/80">Min Salary</label>
              <input
                {...register("salary_min")}
                type="number"
                placeholder="80000"
                className="w-full h-10 px-3 rounded-lg bg-secondary/50 border border-border text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-foreground/80">Max Salary</label>
              <input
                {...register("salary_max")}
                type="number"
                placeholder="150000"
                className="w-full h-10 px-3 rounded-lg bg-secondary/50 border border-border text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-foreground/80">Currency</label>
              <select
                {...register("currency")}
                className="w-full h-10 px-3 rounded-lg bg-secondary/50 border border-border text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
              >
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
                <option value="INR">INR</option>
              </select>
            </div>
          </div>
        </motion.div>

        {/* Submit */}
        <div className="flex items-center justify-end gap-3">
          <Link
            href="/jobs"
            className="px-4 py-2 rounded-lg text-sm text-muted-foreground hover:text-foreground hover:bg-secondary/50 transition-colors"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={isPending}
            className="px-5 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
          >
            {isPending ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" /> Posting...
              </>
            ) : (
              "Post Job"
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
