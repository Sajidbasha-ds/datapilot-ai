import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "DataPilot AI — Autonomous AI Data Scientist",
  description: "Enterprise-grade autonomous data science platform. Upload raw datasets to automatically profile, audit quality, explore, model, evaluate, and generate production insights.",
  keywords: ["Data Science", "AutoML", "Machine Learning", "Data Profiling", "FastAPI", "Next.js"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-background text-foreground antialiased min-h-screen flex flex-col selection:bg-brand-cyan/20 selection:text-brand-sky">
        {children}
      </body>
    </html>
  );
}
