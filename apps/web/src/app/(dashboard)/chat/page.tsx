"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Sparkles, User, Loader2, Bot } from "lucide-react";
import { streamChat } from "@/lib/api";
import type { ChatMessage } from "@/types";
import { cn } from "@/lib/utils";

let msgCounter = 0;
const nextId = () => `msg-${++msgCounter}`;

const SUGGESTED_QUERIES = [
  "Find backend engineers with 5+ years experience",
  "Show candidates with AWS and Kubernetes skills",
  "Who has payment processing domain experience?",
  "Find candidates with the highest match scores",
];

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn("flex gap-3 max-w-4xl", isUser && "ml-auto flex-row-reverse")}
    >
      <div className={cn(
        "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5",
        isUser
          ? "bg-primary/20 border border-primary/30"
          : "bg-violet-500/20 border border-violet-500/30",
      )}>
        {isUser ? <User className="w-4 h-4 text-primary" /> : <Bot className="w-4 h-4 text-violet-400" />}
      </div>
      <div className={cn(
        "flex-1 min-w-0 rounded-2xl px-4 py-3 text-sm leading-relaxed",
        isUser
          ? "bg-primary text-primary-foreground rounded-tr-sm"
          : "glass-card rounded-tl-sm",
      )}>
        <p className="whitespace-pre-wrap">{message.content}</p>
        <p className={cn(
          "text-[11px] mt-2",
          isUser ? "text-primary-foreground/60 text-right" : "text-muted-foreground",
        )}>
          {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </p>
      </div>
    </motion.div>
  );
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: nextId(),
      role: "assistant",
      content:
        "Hello! I'm your AI Hiring Copilot. I can help you find, evaluate, and compare candidates using natural language.\n\nTry asking me something like: \"Find me backend engineers with payment experience and AWS knowledge\"",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || isStreaming) return;

    const userMsgId = nextId();
    const asstMsgId = nextId();

    setMessages((prev) => [
      ...prev,
      { id: userMsgId, role: "user", content: text, timestamp: new Date() },
      { id: asstMsgId, role: "assistant", content: "", timestamp: new Date() },
    ]);
    setInput("");
    setIsStreaming(true);

    try {
      let fullContent = "";
      for await (const event of streamChat(text, sessionId)) {
        if (event.type === "token" && event.content) {
          fullContent += event.content;
          setMessages((prev) =>
            prev.map((m) => (m.id === asstMsgId ? { ...m, content: fullContent } : m))
          );
        } else if (event.type === "done" && event.session_id) {
          setSessionId(event.session_id);
        }
      }
    } catch {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === asstMsgId
            ? { ...m, content: "Sorry, I encountered an error. Please try again." }
            : m
        )
      );
    } finally {
      setIsStreaming(false);
    }
  }, [isStreaming, sessionId]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-64px-48px)] animate-fade-in">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500/20 to-blue-500/20 border border-violet-500/20 flex items-center justify-center">
          <Sparkles className="w-5 h-5 text-violet-400" />
        </div>
        <div>
          <h1 className="text-xl font-bold">AI Recruiter Copilot</h1>
          <p className="text-sm text-muted-foreground">Search and evaluate candidates using natural language</p>
        </div>
        <div className="ml-auto flex items-center gap-1.5 text-xs text-emerald-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          Online
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto custom-scrollbar space-y-4 pb-4">
        <AnimatePresence>
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
        </AnimatePresence>

        {isStreaming && messages[messages.length - 1]?.content === "" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-3 max-w-4xl">
            <div className="w-8 h-8 rounded-full bg-violet-500/20 border border-violet-500/30 flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 text-violet-400" />
            </div>
            <div className="glass-card rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-1">
              {Array.from({ length: 3 }).map((_, i) => (
                <motion.div
                  key={i}
                  className="w-1.5 h-1.5 rounded-full bg-muted-foreground"
                  animate={{ opacity: [0.3, 1, 0.3], y: [0, -3, 0] }}
                  transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                />
              ))}
            </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested queries */}
      {messages.length === 1 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {SUGGESTED_QUERIES.map((q) => (
            <button
              key={q}
              onClick={() => sendMessage(q)}
              className="text-sm px-3 py-1.5 rounded-full glass-card text-muted-foreground hover:text-foreground hover:border-primary/30 transition-all"
            >
              {q}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="glass-card p-3 flex items-end gap-3">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isStreaming}
          placeholder="Ask anything about candidates… (Enter to send, Shift+Enter for newline)"
          rows={1}
          className="flex-1 resize-none bg-transparent text-sm text-foreground placeholder:text-muted-foreground focus:outline-none min-h-[36px] max-h-32 py-1.5 custom-scrollbar"
          onInput={(e) => {
            const el = e.currentTarget;
            el.style.height = "auto";
            el.style.height = `${Math.min(el.scrollHeight, 128)}px`;
          }}
        />
        <button
          onClick={() => sendMessage(input)}
          disabled={!input.trim() || isStreaming}
          className="w-9 h-9 rounded-lg bg-primary text-primary-foreground flex items-center justify-center hover:bg-primary/90 disabled:opacity-40 disabled:cursor-not-allowed transition-all flex-shrink-0"
        >
          {isStreaming ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
        </button>
      </div>
    </div>
  );
}
