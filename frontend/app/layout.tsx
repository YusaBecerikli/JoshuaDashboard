import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Joshua Dashboard",
  description: "Personal life tracking dashboard",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="tr">
      <body>{children}</body>
    </html>
  );
}
