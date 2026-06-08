"use client";

import Link from "next/link";
import React from "react";

export default function Footer() {
  return (
    <footer className="w-full border-t border-outline-variant/10 mt-12 bg-[#0a0c14] text-xs select-none">
      <div className="w-full px-4 md:px-12 py-5">
        <div className="grid grid-cols-1 md:grid-cols-3 items-center gap-6 w-full">
          {/* Left: Brand and Copyright */}
          <div className="flex items-center gap-3 justify-center md:justify-start md:translate-y-[8px]">
            <span className="font-playfair text-[15px] font-bold gold-shimmer-text tracking-wide leading-none">AI GOLD FORECAST</span>
            <span className="text-on-surface-variant/20 text-[11px] hidden md:inline translate-y-[0.5px]">|</span>
            <span className="text-on-surface-variant/60 text-[10px] tracking-wider font-mono uppercase translate-y-[0.5px]">
              © {new Date().getFullYear()} Precision Market Intelligence
            </span>
          </div>

          {/* Center: Social Links & Contact */}
          <div className="flex items-center gap-5 justify-center">
            <div className="flex items-center gap-2">
              <a 
                href="https://t.me/tradingalertsAR" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="w-6.5 h-6.5 rounded-full bg-white/[0.03] hover:bg-primary/10 border border-outline-variant/25 hover:border-primary/40 flex items-center justify-center text-on-surface-variant hover:text-primary transition-all duration-200" 
                aria-label="Telegram"
              >
                <svg className="w-3 h-3 fill-current" viewBox="0 0 24 24">
                  <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
                </svg>
              </a>
              <a 
                href="https://x.com" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="w-6.5 h-6.5 rounded-full bg-white/[0.03] hover:bg-primary/10 border border-outline-variant/25 hover:border-primary/40 flex items-center justify-center text-on-surface-variant hover:text-primary transition-all duration-200" 
                aria-label="X (Twitter)"
              >
                <svg className="w-3 h-3 fill-current" viewBox="0 0 24 24">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                </svg>
              </a>
              <a 
                href="https://instagram.com" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="w-6.5 h-6.5 rounded-full bg-white/[0.03] hover:bg-primary/10 border border-outline-variant/25 hover:border-primary/40 flex items-center justify-center text-on-surface-variant hover:text-primary transition-all duration-200" 
                aria-label="Instagram"
              >
                <svg className="w-3 h-3 fill-current" viewBox="0 0 24 24">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/>
                </svg>
              </a>
            </div>
            
            <span className="text-on-surface-variant/20 text-[11px] hidden md:inline translate-y-[0.5px]">|</span>

            <div className="flex items-center gap-2 text-on-surface-variant">
              <svg className="w-3.5 h-3.5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
              </svg>
              <a href="mailto:arkankl07@gmail.com" className="hover:text-primary transition-colors text-[11px] font-sans font-semibold no-underline translate-y-[0.5px]">
                arkankl07@gmail.com
              </a>
            </div>
          </div>

          {/* Right: Quick Links */}
          <div className="flex items-center gap-5 text-on-surface-variant/80 text-[11px] font-sans font-semibold justify-center md:justify-end">
            <Link href="/blog" className="hover:text-primary transition-colors no-underline">Blog</Link>
            <Link href="/strategies" className="hover:text-primary transition-colors no-underline">Strategies</Link>
            <Link href="/risk-disclosure" className="hover:text-primary transition-colors no-underline">Risk Disclosure</Link>
          </div>
        </div>

        {/* Minimal Risk line */}
        <div className="mt-3 pt-3 border-t border-outline-variant/10 text-center text-[9px] text-on-surface-variant/40 leading-relaxed font-sans">
          Precious metals trading involves high risk. Analyses are for educational purposes. <Link href="/risk-disclosure" className="text-primary hover:underline font-semibold no-underline">Full Disclosure</Link>
        </div>
      </div>
    </footer>
  );
}
