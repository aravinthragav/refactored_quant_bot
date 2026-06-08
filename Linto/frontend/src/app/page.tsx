"use client";

import React, { useEffect, useState, useRef, useCallback } from "react";
import Link from "next/link";
import ChartWidget from "@/components/ChartWidget";
import NewsTicker from "@/components/NewsTicker";
import SignalBanner from "@/components/SignalBanner";
import Footer from "@/components/Footer";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [data, setData] = useState<any>(null);
  const [activeSignal, setActiveSignal] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [scrolled, setScrolled] = useState(false);
  const [blogs, setBlogs] = useState<any[]>([]);
  const [randomStrategy, setRandomStrategy] = useState<any>(null);

  const strategiesList = [
    { name: "EMA 20 & 89 Crossover", tagline: "Follow major momentum swings by tracking moving averages." },
    { name: "ATR Volatility Breakout", tagline: "Capture explosive breakout momentum in consolidation." },
    { name: "S/R Range Bounce", tagline: "Buy near support and sell near resistance in sideways markets." },
    { name: "RSI Momentum Divergence", tagline: "Identify trend exhaustion and catch early reversals." },
    { name: "MACD Histogram Reversals", tagline: "Capture micro-reversals in trend momentum." },
    { name: "Fibonacci Golden Ratio Entry", tagline: "Enter pullback trades at high-confluence zones." },
    { name: "Bollinger Bands Squeeze", tagline: "Position yourself for explosive volatility expansion." },
    { name: "Multi-Timeframe Trend Alignment", tagline: "Only trade in alignment with institutional direction." },
    { name: "Macro News Straddle", tagline: "Capture rapid momentum surges on major economic releases." },
    { name: "London/NY Open Breakout", tagline: "Trade high-liquidity volume surges during session overlaps." }
  ];

  const fetchForecast = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/forecast?ticker=GC=F&asset_name=GOLD`);
      const json = await res.json();
      if (json.success) {
        setData(json);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchActiveSignal = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/active-signal?symbol=GC=F`);
      const json = await res.json();
      if (json.success && json.has_signal) {
        setActiveSignal(json.signal);
      } else {
        setActiveSignal(null);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchBlogs = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/blog`);
      const json = await res.json();
      if (json.success) {
        setBlogs(json.posts ? json.posts.slice(0, 2) : []);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const pickRandomStrategy = () => {
    const idx = Math.floor(Math.random() * strategiesList.length);
    setRandomStrategy(strategiesList[idx]);
  };

  useEffect(() => {
    fetchForecast();
    fetchActiveSignal();
    fetchBlogs();
    pickRandomStrategy();
    const interval = setInterval(() => {
      fetchForecast();
      fetchActiveSignal();
    }, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  // Scroll listener for navbar
  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Glass card 3D hover effect
  useEffect(() => {
    if (loading || !data) return;
    const cards = document.querySelectorAll(".glass-card-hover");
    const cleanups: (() => void)[] = [];

    cards.forEach((card) => {
      const el = card as HTMLElement;
      const handleMove = (e: MouseEvent) => {
        const rect = el.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        requestAnimationFrame(() => {
          if (el.classList.contains("direction-card")) {
            const glowColor = isLong ? "38, 166, 154" : "239, 83, 80";
            el.style.background = `radial-gradient(600px circle at ${x}px ${y}px, rgba(${glowColor}, 0.15), transparent 40%), rgba(22, 24, 32, 0.75)`;
            el.style.transform = `perspective(1000px) rotateX(${(y - rect.height / 2) / -50}deg) rotateY(${(x - rect.width / 2) / 50}deg) translateY(-2px)`;
            el.style.borderColor = `rgba(${glowColor}, 0.6)`;
            el.style.boxShadow = `0 8px 32px rgba(${glowColor}, 0.15)`;
          } else {
            el.style.background = `radial-gradient(600px circle at ${x}px ${y}px, rgba(212, 175, 55, 0.1), transparent 40%), rgba(22, 24, 32, 0.75)`;
            el.style.transform = `perspective(1000px) rotateX(${(y - rect.height / 2) / -50}deg) rotateY(${(x - rect.width / 2) / 50}deg) translateY(-2px)`;
            el.style.borderColor = "rgba(212, 175, 55, 0.3)";
            el.style.boxShadow = "0 8px 32px rgba(212, 175, 55, 0.08)";
          }
        });
      };
      const handleLeave = () => {
        requestAnimationFrame(() => {
          el.style.background = "";
          el.style.borderColor = "";
          el.style.boxShadow = "";
          el.style.transform = "";
        });
      };
      el.addEventListener("mousemove", handleMove as any);
      el.addEventListener("mouseleave", handleLeave);
      cleanups.push(() => {
        el.removeEventListener("mousemove", handleMove as any);
        el.removeEventListener("mouseleave", handleLeave);
      });
    });

    return () => {
      cleanups.forEach((cleanup) => cleanup());
      // Reset all cards inline styles on cleanup to prevent stuck glows on refresh
      cards.forEach((card) => {
        const el = card as HTMLElement;
        el.style.background = "";
        el.style.borderColor = "";
        el.style.boxShadow = "";
        el.style.transform = "";
      });
    };
  }, [loading, data]);

  // Intersection Observer for scroll reveal
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.remove("reveal");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1 }
    );
    document.querySelectorAll(".animate-fade-up").forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, [loading]);

  const isLong = data?.direction?.includes("Bullish") || data?.direction === "LONG";

  return (
    <main className="min-h-screen text-foreground font-sans overflow-x-hidden pb-16">
      {/* ─── Fixed Glassmorphic Navbar ─── */}
      <header
        className={`fixed top-0 w-full z-50 transition-all duration-500 ease-in-out border-b backdrop-blur-[24px] ${
          scrolled
            ? "border-primary/15 bg-[#0a0c12]/88 shadow-[0_4px_30px_rgba(0,0,0,0.4),0_1px_0_rgba(212,175,55,0.05)]"
            : "border-transparent bg-[#06070a]/60"
        }`}
      >
        <div className="flex justify-between items-center px-4 md:px-12 py-3 md:py-4 w-full">
          {/* Logo + Title */}
          <div className="flex items-center gap-3 group cursor-pointer">
            <svg width="32" height="32" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-7 h-7 md:w-8 md:h-8 filter drop-shadow-[0_0_10px_rgba(212,175,55,0.5)]">
              <rect x="4" y="22" width="18" height="12" rx="2" fill="#d4af37" stroke="#f2ca50" strokeWidth="1.5"/>
              <rect x="8" y="24" width="10" height="2" rx="1" fill="#f2ca50" opacity="0.6"/>
              <rect x="14" y="16" width="18" height="12" rx="2" fill="#e9c349" stroke="#f2ca50" strokeWidth="1.5"/>
              <rect x="18" y="18" width="10" height="2" rx="1" fill="#ffe088" opacity="0.6"/>
              <rect x="24" y="10" width="18" height="12" rx="2" fill="#f2ca50" stroke="#ffe088" strokeWidth="1.5"/>
              <rect x="28" y="12" width="10" height="2" rx="1" fill="#ffe088" opacity="0.7"/>
            </svg>
            <div className="flex flex-col">
              <span className="font-playfair text-sm md:text-xl font-bold tracking-tight gold-shimmer-text">
                AI GOLD FORECAST
              </span>
              <span className="text-[9px] md:text-[10px] text-on-surface-variant tracking-[0.15em] uppercase hidden sm:block">
                Executive Intelligence Terminal
              </span>
            </div>
          </div>

          {/* Nav Links (Desktop) */}
          <nav className="hidden md:flex items-center gap-8 text-sm font-semibold">
            <Link href="/" className="text-primary border-b-2 border-primary pb-1 no-underline">
              Home
            </Link>
            <Link href="/blog" className="text-on-surface-variant hover:text-primary transition-colors nav-link no-underline">
              Blog
            </Link>
            <Link href="/strategies" className="text-on-surface-variant hover:text-primary transition-colors nav-link no-underline">
              Strategies
            </Link>
          </nav>

          {/* Right: Accuracy + CTAs */}
          <div className="flex items-center gap-4 md:gap-6">
            <div className="hidden lg:flex flex-col items-end">
              <span className="text-[10px] text-on-surface-variant font-semibold tracking-wider uppercase">
                30-Signal Accuracy
              </span>
              <span className="text-primary font-bold text-lg animate-pulse-glow">71.4%</span>
            </div>
            <a
              href="https://t.me/tradingalertsAR"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-primary hover:bg-gold-light text-on-primary font-bold px-6 py-2.5 rounded-lg transition-all duration-300 transform active:scale-95 shadow-[0_0_15px_rgba(212,175,55,0.3)] hover:shadow-[0_0_25px_rgba(212,175,55,0.5)] premium-hover-btn text-xs md:text-sm no-underline"
            >
              Subscribe
            </a>
          </div>
        </div>
      </header>

      <SignalBanner signal={activeSignal} />

      {/* Mobile Ad Banner */}
      <div className="block md:hidden text-center mt-[72px] mx-4">
        <a href="https://one.exnessonelink.com/intl/en/a/thvdkhvd" target="_blank" rel="noopener noreferrer" className="inline-block w-full">
          <img src="https://d3dpet1g0ty5ed.cloudfront.net/EN_Trade_USOIL_with_Exness_720x90.png" className="max-w-full h-auto rounded-xl border border-primary/10" alt="Trade with Exness" />
        </a>
      </div>

      {/* ─── Main Content ─── */}
      <div className="w-full px-4 md:px-12 pt-3 md:pt-[100px] ambient-glow">
        {loading ? (
          <div className="flex flex-col justify-center items-center h-[400px] md:h-[600px] gap-4">
            <div className="w-14 h-14 rounded-full border-2 border-primary/20 border-t-primary animate-spin" />
            <div className="text-xl text-on-surface-variant animate-pulse font-playfair gold-shimmer-text">
              Running AI Forecast Models...
            </div>
          </div>
        ) : data ? (
          <>
            {/* ─── Metrics Row ─── */}
            <section className="grid grid-cols-2 lg:grid-cols-5 gap-3 md:gap-5 mb-3">
              {/* Current — gold-rim hero card */}
              <div className="reveal animate-fade-up glass-card glass-card-hover gold-rim p-4 md:p-5 rounded-xl" style={{ animationDelay: "0.1s" }}>
                <p className="text-[10px] md:text-xs text-on-surface-variant uppercase mb-1.5 font-semibold tracking-wider">Current</p>
                <h3 className="text-xl md:text-2xl font-bold text-on-surface font-mono">{data.current_price?.toFixed(2)}</h3>
                <div className="w-full h-1 bg-surface-variant/40 mt-3 overflow-hidden rounded-full">
                  <div className="h-full w-2/3 rounded-full" style={{ background: "linear-gradient(90deg, #f2ca50 0%, #ffe088 50%, #f2ca50 100%)", backgroundSize: "200% 100%", animation: "shimmer 2.5s infinite linear" }} />
                </div>
              </div>

              {/* Forecast */}
              <div className="reveal animate-fade-up glass-card glass-card-hover p-4 md:p-5 rounded-xl" style={{ animationDelay: "0.2s" }}>
                <p className="text-[10px] md:text-xs text-on-surface-variant uppercase mb-1.5 font-semibold tracking-wider">Forecast</p>
                <h3 className="text-xl md:text-2xl font-bold text-on-surface font-mono">{data.forecast_price?.toFixed(2)}</h3>
                <p className={`text-[10px] md:text-xs font-semibold mt-1.5 ${(data.move_pct ?? 0) >= 0 ? "text-primary" : "text-error"}`}>
                  {(data.move_pct ?? 0) >= 0 ? "+" : ""}{data.move_pct?.toFixed(2)}% Target Diff
                </p>
              </div>

              {/* Move % */}
              <div className="reveal animate-fade-up glass-card glass-card-hover p-4 md:p-5 rounded-xl" style={{ animationDelay: "0.3s" }}>
                <p className="text-[10px] md:text-xs text-on-surface-variant uppercase mb-1.5 font-semibold tracking-wider">Move %</p>
                <h3 className={`text-xl md:text-2xl font-bold font-mono ${(data.move_pct ?? 0) >= 0 ? "text-primary" : "text-error"}`}>
                  {data.move_pct?.toFixed(2)}%
                </h3>
                <p className="text-[10px] md:text-xs text-on-surface-variant mt-1.5">24h Volatility</p>
              </div>

              {/* Direction — colored border and shadow glow */}
              <div className={`reveal animate-fade-up glass-card glass-card-hover direction-card p-4 md:p-5 rounded-xl border transition-all duration-300 ${
                isLong 
                  ? "border-[#26a69a]/40 shadow-[0_0_15px_rgba(38,166,154,0.1)] hover:border-[#26a69a]" 
                  : "border-[#ef5350]/40 shadow-[0_0_15px_rgba(239,83,80,0.1)] hover:border-[#ef5350]"
              }`} style={{ animationDelay: "0.4s" }}>
                <p className="text-[10px] md:text-xs text-on-surface-variant uppercase mb-1.5 font-semibold tracking-wider">Direction</p>
                <h3 className={`text-xl md:text-2xl font-extrabold font-mono ${
                  isLong ? "text-[#26a69a]" : "text-[#ef5350]"
                }`}>
                  {isLong ? "Bullish" : "Bearish"}
                </h3>
              </div>

              {/* MAE (Desktop Mode Only card in grid) */}
              <div className="reveal animate-fade-up glass-card glass-card-hover p-4 md:p-5 rounded-xl hidden lg:block" style={{ animationDelay: "0.5s" }}>
                <p className="text-[10px] md:text-xs text-on-surface-variant uppercase mb-1.5 font-semibold tracking-wider">MAE</p>
                <h3 className="text-xl md:text-2xl font-bold text-on-surface font-mono">{data.mae ? `${data.mae.toFixed(4)}%` : "N/A"}</h3>
                <p className="text-[10px] md:text-xs text-on-surface-variant mt-1.5">Mean Absolute Error</p>
              </div>
            </section>

            {/* MAE Row — Mobile/Tablet only full width compact bar */}
            <div className="reveal animate-fade-up glass-card glass-card-hover px-5 py-4 rounded-xl flex justify-between items-center mb-5 md:mb-6 lg:hidden" style={{ animationDelay: "0.5s" }}>
              <span className="text-[10px] md:text-xs text-on-surface-variant font-bold tracking-wider uppercase font-sans">
                MAE (Mean Absolute Error)
              </span>
              <span className="text-base md:text-lg font-bold text-on-surface font-mono">
                {data.mae ? `${data.mae.toFixed(4)}%` : "N/A"}
              </span>
            </div>

            {/* ─── 3-Column Layout ─── */}
            <div className="grid grid-cols-12 gap-4 md:gap-5">
              {/* Left Sidebar */}
              <aside className="col-span-12 lg:col-span-2 space-y-4 hidden lg:block">
                {/* Exness Promo Card */}
                <div className="reveal animate-fade-up glass-card rounded-xl overflow-hidden group" style={{ animationDelay: "0.6s" }}>
                  <a href="https://one.exnessonelink.com/intl/en/a/thvdkhvd" target="_blank" rel="noopener noreferrer" className="block relative w-full h-auto">
                    <img alt="Trade with Exness" className="w-full h-auto object-contain transition-transform duration-1000 ease-out group-hover:scale-105" src="https://d3dpet1g0ty5ed.cloudfront.net/EN_Take_control_300x600.png" />
                  </a>
                </div>

                {/* Quick Links */}
                <div className="reveal animate-fade-up glass-card p-3 rounded-xl flex flex-col gap-1" style={{ animationDelay: "0.7s" }}>
                  <Link href="/strategies" className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-surface-variant/50 transition-all group no-underline text-on-surface">
                    <span className="text-primary group-hover:scale-110 group-hover:drop-shadow-[0_0_8px_rgba(242,202,80,0.4)] transition-all">📖</span>
                    <span className="text-sm font-semibold">Strategies</span>
                  </Link>
                  <Link href="/blog" className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-surface-variant/50 transition-all group no-underline text-on-surface">
                    <span className="text-primary group-hover:scale-110 group-hover:drop-shadow-[0_0_8px_rgba(242,202,80,0.4)] transition-all">📰</span>
                    <span className="text-sm font-semibold">Daily Blog</span>
                  </Link>
                  <a href="https://t.me/tradingalertsAR" target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 p-2.5 rounded-lg bg-[#0088cc]/10 hover:bg-[#0088cc]/20 transition-all group no-underline">
                    <span className="group-hover:scale-110 transition-all">📢</span>
                    <span className="text-sm font-semibold text-[#229ED9]">Join Telegram</span>
                  </a>
                </div>
              </aside>

              {/* Center: Chart */}
              <section className="col-span-12 lg:col-span-8">
                <div className="reveal animate-fade-up" style={{ animationDelay: "0.4s" }}>
                  <ChartWidget data={data} />
                </div>
                {/* Mobile/Tablet Refresh Indicator - Centered between chart and footer */}
                <div className="reveal animate-fade-up text-center mt-6 lg:hidden text-[10px] text-secondary/50 font-bold uppercase tracking-[0.2em] font-sans" style={{ animationDelay: "0.5s" }}>
                  Auto refreshes every 5 minutes
                </div>
              </section>

              {/* Right Sidebar */}
              <aside className="col-span-12 lg:col-span-2 space-y-4 hidden lg:block">
                {/* Exness Ad */}
                <div className="reveal animate-fade-up glass-card rounded-xl overflow-hidden group" style={{ animationDelay: "1.0s" }}>
                  <a href="https://one.exnessonelink.com/intl/en/a/thvdkhvd" target="_blank" rel="noopener noreferrer" className="block relative w-full h-auto">
                    <img alt="Exness Trading" className="w-full h-auto object-contain transition-transform duration-1000 ease-out group-hover:scale-105" src="https://d3dpet1g0ty5ed.cloudfront.net/EN_Trading_Conditions_300x600px.gif" />
                  </a>
                </div>

                {/* Dynamic blogs and strategy card */}
                <div className="reveal animate-fade-up glass-card p-4 rounded-xl space-y-4" style={{ animationDelay: "1.1s" }}>
                  <div>
                    <h5 className="text-[10px] font-bold border-b border-primary/20 pb-1.5 mb-3 tracking-wider uppercase text-on-surface-variant font-sans">
                      <span className="gold-shimmer-text">Latest Intelligence</span>
                    </h5>
                    {blogs.length > 0 ? (
                      <div className="space-y-3">
                        {blogs.map((b: any) => (
                          <Link key={b.id} href={`/blog/${b.slug}`} className="block group no-underline">
                            <h6 className="text-[11px] font-bold text-white group-hover:text-primary transition-colors line-clamp-2 leading-tight font-sans">
                              {b.title}
                            </h6>
                            <p className="text-[9px] text-on-surface-variant/70 mt-0.5 font-sans">
                              {new Date(b.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                            </p>
                          </Link>
                        ))}
                      </div>
                    ) : (
                      <p className="text-[10px] text-on-surface-variant/50 font-sans">No reports found.</p>
                    )}
                  </div>

                  {randomStrategy && (
                    <div className="border-t border-outline-variant/15 pt-3">
                      <h5 className="text-[10px] font-bold pb-1 mb-2 tracking-wider uppercase text-primary font-sans">
                        Featured Strategy
                      </h5>
                      <Link href="/strategies" className="block group no-underline">
                        <h6 className="text-[11px] font-bold text-white group-hover:text-primary transition-colors leading-tight font-sans">
                          {randomStrategy.name}
                        </h6>
                        <p className="text-[9px] text-on-surface-variant/70 mt-1 line-clamp-2 leading-relaxed font-sans">
                          {randomStrategy.tagline}
                        </p>
                      </Link>
                    </div>
                  )}
                </div>
              </aside>
            </div>

            {/* Bottom Ad - Desktop */}
            <div className="hidden md:block text-center mt-8">
              <a href="https://one.exnessonelink.com/intl/en/a/thvdkhvd" target="_blank" rel="noopener noreferrer" className="inline-block">
                <img src="https://d3dpet1g0ty5ed.cloudfront.net/EN_Trade_USOIL_with_Exness_720x90.png" className="max-w-full h-auto rounded-xl border border-primary/10 hover:border-primary/25 transition-colors" alt="Trade with Exness" />
              </a>
            </div>

            {/* ─── Premium Footer (Full Width) ─── */}
          </>
        ) : (
          <div className="text-error text-center mt-20 text-lg">Failed to load forecast data. Is the backend running?</div>
        )}
      </div>

      <Footer />

      <NewsTicker apiUrl={API_BASE_URL} />
    </main>
  );
}
