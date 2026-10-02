import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ASTRA VIDEO AI — Create anything. Direct everything.",
  description: "Professional AI creative studio for video, image, audio, characters and storyboards.",
  applicationName: "ASTRA VIDEO AI",
};

export const viewport: Viewport = {
  themeColor: "#080a0f",
  colorScheme: "dark",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
