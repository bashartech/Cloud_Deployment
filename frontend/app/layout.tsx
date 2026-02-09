import type { Metadata } from "next";
import "./globals.css";

import "@chatscope/chat-ui-kit-styles/dist/default/styles.min.css"; // Import ChatKit styles
import { Toaster } from "sonner";


export const metadata: Metadata = {
  title: "Todo App",
  description: "A full-stack todo application with authentication",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`antialiased bg-background text-foreground`}
      >
        {/* <AuthProvider>
        </AuthProvider> */}
          {children}
          <Toaster />
      </body>
    </html>
  );
}
