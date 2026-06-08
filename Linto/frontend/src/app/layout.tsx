import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Script from "next/script";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Gold Forecast Terminal | Real-Time Precious Metals Intelligence",
  description: "Advanced AI-driven gold price forecasting, real-time market signals, technical EMAs, support/resistance levels, and breaking commodities news.",
  keywords: ["Gold Forecast", "AI Trading Signals", "Gold Price Prediction", "Commodities Trading", "Technical Analysis", "XAUUSD", "Precious Metals"],
  authors: [{ name: "AI Gold Forecast Team" }],
  openGraph: {
    title: "AI Gold Forecast Terminal | Real-Time Market Intelligence",
    description: "Get smart trading signals and real-time gold price forecasts powered by machine learning.",
    url: "http://localhost:3000",
    siteName: "AI Gold Forecast Terminal",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "AI Gold Forecast Terminal | Real-Time Market Signals",
    description: "Real-time AI gold price forecasting and commodities news.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <head>
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=G-8C0VKHXDF6"
          strategy="afterInteractive"
        />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-8C0VKHXDF6');
          `}
        </Script>
      </head>
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
