import "@ant-design/v5-patch-for-react-19";
import type { Metadata } from "next";
import { Inter, DM_Sans } from "next/font/google";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import { AntdRegistry } from "@ant-design/nextjs-registry";
import { QueryProvider } from "@/components/providers/query-provider";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

const dmSans = DM_Sans({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-dm-sans",
});

export const metadata: Metadata = {
  title: "Ideanance",
  description: "Governance-first design workspace for agentic applications",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${dmSans.variable} ${GeistSans.variable} ${GeistMono.variable}`}
    >
      <body className="font-sans antialiased">
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:p-2 focus:bg-[var(--color-primary)] focus:text-[var(--color-primary-foreground)]"
        >
          Skip to main content
        </a>
        <AntdRegistry>
          <QueryProvider>{children}</QueryProvider>
        </AntdRegistry>
      </body>
    </html>
  );
}
