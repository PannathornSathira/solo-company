import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";
import { StateProvider } from "../lib/StateContext";
import { Navigation } from "../components/Navigation";

export const metadata: Metadata = {
  title: "Solo Company Console",
  description: "Owner console for a single AI-assisted company.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <StateProvider>
          <Navigation>{children}</Navigation>
        </StateProvider>
      </body>
    </html>
  );
}
