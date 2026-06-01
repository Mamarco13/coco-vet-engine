import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Cormorant_Garamond, Space_Grotesk } from "next/font/google";
import { SiteFooter } from "@/components/layout/SiteFooter";
import { SiteHeader } from "@/components/layout/SiteHeader";
import "./globals.css";

const spaceGrotesk = Space_Grotesk({
  variable: "--font-manrope",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
});

const cormorantGaramond = Cormorant_Garamond({
  variable: "--font-fraunces",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "COCO | Deteccion temprana canina",
  description:
    "Plataforma de analisis de enfermedades caninas con enfoque en soporte clinico.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html
      lang="es"
      className={`${spaceGrotesk.variable} ${cormorantGaramond.variable} h-full antialiased`}
    >
      <body className="min-h-full bg-[var(--background)] text-[var(--foreground)]">
        <div className="relative min-h-screen overflow-hidden">
          <div className="pointer-events-none absolute -top-24 right-0 h-[320px] w-[320px] rounded-full bg-[radial-gradient(circle,_rgba(13,139,141,0.35)_0%,_rgba(13,139,141,0)_70%)] blur-3xl" />
          <div className="pointer-events-none absolute -bottom-32 left-0 h-[360px] w-[360px] rounded-full bg-[radial-gradient(circle,_rgba(250,210,160,0.4)_0%,_rgba(250,210,160,0)_70%)] blur-3xl" />
          <div className="relative z-10 flex min-h-screen flex-col">
            <SiteHeader />
            <main className="flex-1">{children}</main>
            <SiteFooter />
          </div>
        </div>
      </body>
    </html>
  );
}
