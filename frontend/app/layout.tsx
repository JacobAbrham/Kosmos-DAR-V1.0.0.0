import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "KOSMOS Agent Swarm",
  description: "Interface for the KOSMOS Digital Agentic System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen flex flex-col">
        <header className="bg-slate-900 border-b border-slate-800 p-4">
            <h1 className="text-xl font-bold text-blue-400">KOSMOS <span className="text-slate-400 text-sm font-normal">Digital Agentic System</span></h1>
        </header>
        <main className="flex-1 flex flex-col">
            {children}
        </main>
      </body>
    </html>
  );
}
