"use client";

import React, { useEffect, useState } from "react";

export default function NewsTicker({ apiUrl }: { apiUrl?: string }) {
  const [news, setNews] = useState<string[]>([]);

  useEffect(() => {
    const apiBase = apiUrl || (typeof window !== "undefined" ? (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000") : "http://localhost:8000");
    fetch(`${apiBase}/api/news?asset_name=GOLD`)
      .then((res) => res.json())
      .then((data) => {
        if (data.success && data.headlines) {
          // duplicate to make scrolling seamless
          setNews([...data.headlines, ...data.headlines, ...data.headlines]);
        }
      })
      .catch((err) => console.error("Failed to fetch news:", err));
  }, [apiUrl]);

  if (news.length === 0) return null;

  return (
    <div className="fixed bottom-0 left-0 w-full h-[42px] bg-[#080a12f5] border-t border-white/10 overflow-hidden z-[99999] flex items-center">
      <div className="news-ticker-track">
        {news.map((item, idx) => (
          <div key={idx} className="flex items-center gap-3 pr-12 text-white/90 text-sm font-semibold">
            <span className="text-[#ff8c00] text-[11px]">✦</span>
            <span>{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
