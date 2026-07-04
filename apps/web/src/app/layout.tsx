import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "@/styles/globals.css";
import { Providers } from "./providers";
import { Toaster } from "sonner";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: {
    default: "AI Hiring Copilot",
    template: "%s | AI Hiring Copilot",
  },
  description: "AI-powered recruitment and resume screening platform",
  icons: { icon: "/favicon.ico" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans`}>
        <Providers>
          {children}
          <Toaster
            theme="dark"
            position="top-right"
            toastOptions={{
              style: {
                background: "hsl(222 47% 9%)",
                border: "1px solid hsl(217 33% 17%)",
                color: "hsl(210 40% 96%)",
              },
            }}
          />
        </Providers>
      </body>
    </html>
  );
}
