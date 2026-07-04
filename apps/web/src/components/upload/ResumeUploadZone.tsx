"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, File, X, CheckCircle2, Loader2, AlertCircle } from "lucide-react";
import { toast } from "sonner";
import { resumesApi } from "@/lib/api";
import { cn } from "@/lib/utils";

interface Props {
  jobId: string;
  onUploadComplete?: (candidateId: string) => void;
}

interface UploadFile {
  file: File;
  status: "pending" | "uploading" | "success" | "error";
  error?: string;
  candidateId?: string;
}

export function ResumeUploadZone({ jobId, onUploadComplete }: Props) {
  const [files, setFiles] = useState<UploadFile[]>([]);

  const onDrop = useCallback((accepted: File[]) => {
    const newFiles: UploadFile[] = accepted.map((f) => ({ file: f, status: "pending" }));
    setFiles((prev) => [...prev, ...newFiles]);
    newFiles.forEach((uf) => uploadFile(uf.file));
  }, [jobId]); // eslint-disable-line react-hooks/exhaustive-deps

  const uploadFile = async (file: File) => {
    setFiles((prev) =>
      prev.map((f) => (f.file === file ? { ...f, status: "uploading" } : f))
    );

    try {
      const res = await resumesApi.upload(file, jobId);
      setFiles((prev) =>
        prev.map((f) =>
          f.file === file ? { ...f, status: "success", candidateId: res.candidate_id } : f
        )
      );
      toast.success(`${file.name} uploaded — AI processing started`);
      onUploadComplete?.(res.candidate_id);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Upload failed";
      setFiles((prev) =>
        prev.map((f) => (f.file === file ? { ...f, status: "error", error: message } : f))
      );
      toast.error(`Failed to upload ${file.name}`);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: true,
  });

  const removeFile = (file: File) => {
    setFiles((prev) => prev.filter((f) => f.file !== file));
  };

  return (
    <div className="glass-card p-5 space-y-4">
      <h3 className="font-semibold text-foreground text-sm">Upload Resumes</h3>

      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={cn(
          "border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all",
          isDragActive
            ? "border-primary bg-primary/5"
            : "border-border hover:border-primary/50 hover:bg-primary/5",
        )}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center gap-3">
          <div className={cn(
            "w-12 h-12 rounded-xl flex items-center justify-center transition-colors",
            isDragActive ? "bg-primary/20 text-primary" : "bg-secondary text-muted-foreground",
          )}>
            <Upload className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-foreground">
              {isDragActive ? "Drop resumes here" : "Drop resumes or click to browse"}
            </p>
            <p className="text-xs text-muted-foreground mt-1">PDF or DOCX, up to 10MB each</p>
          </div>
        </div>
      </div>

      {/* File list */}
      <AnimatePresence>
        {files.map(({ file, status, error }) => (
          <motion.div
            key={file.name}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, x: 8 }}
            className="flex items-center gap-3 px-4 py-3 rounded-lg bg-secondary/50 border border-border"
          >
            <File className="w-4 h-4 text-muted-foreground flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-sm text-foreground font-medium truncate">{file.name}</p>
              <p className="text-xs text-muted-foreground">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>

            {/* Status */}
            {status === "uploading" && <Loader2 className="w-4 h-4 text-primary animate-spin flex-shrink-0" />}
            {status === "success" && <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />}
            {status === "error" && (
              <div className="flex items-center gap-1 text-destructive">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span className="text-xs">{error}</span>
              </div>
            )}

            {status !== "uploading" && (
              <button
                onClick={() => removeFile(file)}
                className="text-muted-foreground hover:text-foreground transition-colors flex-shrink-0"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
