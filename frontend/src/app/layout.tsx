import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MTC Verification System | AI-Powered Material Certificate Analysis",
  description: "Automated Material Test Certificate verification using AI-powered OCR and structured validation against international standards (ASTM, ASME, MIL).",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="gradient-mesh">{children}</body>
    </html>
  );
}
