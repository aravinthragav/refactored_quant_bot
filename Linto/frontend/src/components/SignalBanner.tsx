"use client";

import React, { useEffect, useState } from "react";

interface SignalBannerProps {
  signal: any;
}

export default function SignalBanner({ signal }: SignalBannerProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (signal) {
      setVisible(true);
      const timer = setTimeout(() => {
        setVisible(false);
      }, 8000); // Show for 8 seconds
      return () => clearTimeout(timer);
    } else {
      setVisible(false);
    }
  }, [signal]);

  if (!visible || !signal) return null;

  const isLong = signal.direction.includes("Bullish") || signal.direction.includes("LONG");
  const color = isLong ? "#ff8c00" : "#2962ff";
  const directionText = isLong ? "BULLISH LONG" : "BEARISH SHORT";

  // Use a key combining id and time to force re-render and re-run CSS fade-in animations on new signals
  const bannerKey = `${signal.id}_${signal.created_at}`;

  return (
    <div key={bannerKey} className="signal-banner">
      <div className="relative flex items-center justify-center w-3 h-3 flex-shrink-0">
        <span className="absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping" style={{ backgroundColor: color }}></span>
        <span className="relative inline-flex rounded-full h-3 w-3" style={{ backgroundColor: color }}></span>
      </div>
      <div className="flex flex-col leading-tight ml-1">
        <div className="text-[14px] font-extrabold flex items-center gap-1.5">
          <span>🚨 ACTIVE SIGNAL:</span>
          <span style={{ color }}>{directionText}</span>
        </div>
        <div className="text-[12px] opacity-90 mt-0.5 font-medium">
          Entry: <span className="font-bold text-white">{signal.entry_price?.toFixed(2)}</span> &nbsp;|&nbsp;
          TP: <span className="font-bold text-green-400">{signal.tp_price?.toFixed(2)}</span> &nbsp;|&nbsp;
          SL: <span className="font-bold text-red-400">{signal.sl_price?.toFixed(2)}</span> &nbsp;|&nbsp;
          Confidence: <span className="font-bold text-white">{signal.confidence?.toFixed(1)}%</span>
        </div>
      </div>
    </div>
  );
}
