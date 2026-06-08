"use client";

import React, { useEffect, useState } from "react";
import ChartWidget from "@/components/ChartWidget";
import NewsTicker from "@/components/NewsTicker";
import SignalBanner from "@/components/SignalBanner";

export default function Home() {
  const [data, setData] = useState<any>(null);
  const [activeSignal, setActiveSignal] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const API_BASE_URL = typeof window !== "undefined"
    ? (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000")
    : "http://localhost:8000";

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

  useEffect(() => {
    fetchForecast();
    fetchActiveSignal();
    const interval = setInterval(() => {
      fetchForecast();
      fetchActiveSignal();
    }, 5 * 60 * 1000); // 5 min
    return () => clearInterval(interval);
  }, []);

  return (
    <main className="min-h-screen bg-[#0e1117] text-white font-sans overflow-x-hidden pb-16">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row justify-between items-center gap-2 md:gap-4 bg-gradient-to-r from-[#06142c] to-[#0d1f44] p-3 md:p-6 mx-4 mt-3 rounded-xl border border-white/10 text-center sm:text-left">
        <div className="flex items-center justify-between w-full sm:w-auto">
          <div>
            <h1 className="text-base sm:text-lg md:text-[32px] font-extrabold leading-tight">
              🟡 AI Gold Forecast Terminal
            </h1>
            <div className="mt-1 hidden md:block text-xs md:text-sm text-gray-400">
              Smart Signals • Market Intelligence • Real-Time Forecasting
            </div>
          </div>
          {/* Mobile-only accuracy badge next to title */}
          <div className="sm:hidden flex flex-col items-end">
            <span className="text-[10px] text-gray-400">Accuracy</span>
            <span className="text-sm font-bold text-green-500">71.4%</span>
          </div>
        </div>
        <div className="flex flex-row items-center justify-between sm:justify-end gap-3 w-full sm:w-auto border-t border-white/5 pt-2 sm:pt-0 sm:border-t-0 mt-1 sm:mt-0">
          <div className="hidden sm:block text-right">
            <div className="text-xs text-gray-400">30-Signal Accuracy</div>
            <div className="text-lg md:text-[28px] font-extrabold text-green-500 leading-none mt-0.5">
              71.4%
            </div>
          </div>
          <a
            href="https://t.me/tradingalertsAR"
            target="_blank"
            rel="noopener noreferrer"
            className="w-full sm:w-auto text-center no-underline bg-[#229ED9] px-3 py-1.5 md:px-5 md:py-2.5 rounded-lg text-white font-bold text-xs md:text-[15px] inline-block hover:bg-[#1d8bcb] transition-colors"
          >
            📢 Telegram
          </a>
        </div>
      </div>

      {/* Horizontal ad banner - Top on Mobile only */}
      <div className="block md:hidden text-center mt-3 mx-4">
        <a href="https://one.exnessonelink.com/intl/en/a/thvdkhvd" target="_blank" rel="noopener noreferrer" className="inline-block w-full">
          <img src="https://d3dpet1g0ty5ed.cloudfront.net/EN_Trade_USOIL_with_Exness_720x90.png" className="max-w-full h-auto rounded-xl border border-white/5" alt="Exness Ad" />
        </a>
      </div>

      <SignalBanner signal={activeSignal} />
 
      {/* Main Content */}
      <div className="max-w-[1600px] mx-auto px-4 mt-4 md:mt-6">
        {loading ? (
          <div className="flex justify-center items-center h-[400px] md:h-[600px]">
            <div className="text-xl text-gray-400 animate-pulse">Running AI Forecast Models...</div>
          </div>
        ) : data ? (
          <>
            {/* Flex container only wrapping Chart and Metrics to handle responsive ordering */}
            <div className="flex flex-col">
              {/* Layout with Ads & Chart */}
              <div className="order-1 md:order-2 flex gap-4 mb-4">
                <div className="w-[15%] hidden lg:flex rounded-xl overflow-hidden border border-white/5 items-center justify-center min-h-[600px] bg-[#1a1c24]">
                  <a href="https://one.exnessonelink.com/intl/en/a/thvdkhvd" target="_blank" rel="noopener noreferrer" className="w-full">
                    <img src="https://d3dpet1g0ty5ed.cloudfront.net/EN_Take_control_300x600.png" className="w-full h-auto object-contain" alt="Exness Ad" />
                  </a>
                </div>
                
                <div className="w-full lg:w-[70%] relative">
                  <ChartWidget data={data} />
                </div>
                
                <div className="w-[15%] hidden lg:flex rounded-xl overflow-hidden border border-white/5 items-center justify-center min-h-[600px] bg-[#1a1c24]">
                  <a href="https://one.exnessonelink.com/intl/en/a/thvdkhvd" target="_blank" rel="noopener noreferrer" className="w-full">
                    <img src="https://d3dpet1g0ty5ed.cloudfront.net/EN_Trading_Conditions_300x600px.gif" className="w-full h-auto object-contain" alt="Exness Ad" />
                  </a>
                </div>
              </div>

              {/* Metrics simple view: Horizontally scrollable on mobile, grid on desktop */}
              <div className="order-2 md:order-1 flex overflow-x-auto md:grid md:grid-cols-5 gap-3 md:gap-4 mb-4 pb-2 md:pb-0 scrollbar-none">
                <div className="bg-[#1a1c24] p-3 md:p-4 rounded-xl border border-white/5 min-w-[125px] md:min-w-0 flex-1 flex flex-col justify-between">
                  <div className="text-[11px] md:text-sm text-gray-400 mb-0.5 md:mb-1">Current</div>
                  <div className="text-base md:text-2xl font-bold">{data.current_price?.toFixed(2)}</div>
                </div>
                <div className="bg-[#1a1c24] p-3 md:p-4 rounded-xl border border-white/5 min-w-[125px] md:min-w-0 flex-1 flex flex-col justify-between">
                  <div className="text-[11px] md:text-sm text-gray-400 mb-0.5 md:mb-1">Forecast</div>
                  <div className="text-base md:text-2xl font-bold">{data.forecast_price?.toFixed(2)}</div>
                </div>
                <div className="bg-[#1a1c24] p-3 md:p-4 rounded-xl border border-white/5 min-w-[125px] md:min-w-0 flex-1 flex flex-col justify-between">
                  <div className="text-[11px] md:text-sm text-gray-400 mb-0.5 md:mb-1">Move %</div>
                  <div className="text-base md:text-2xl font-bold">{data.move_pct?.toFixed(2)}%</div>
                </div>
                <div className="bg-[#1a1c24] p-3 md:p-4 rounded-xl border border-white/5 min-w-[125px] md:min-w-0 flex-1 flex flex-col justify-between">
                  <div className="text-[11px] md:text-sm text-gray-400 mb-0.5 md:mb-1">Direction</div>
                  <div className={`text-base md:text-2xl font-bold ${data.direction === "LONG" ? "text-orange-500" : "text-blue-500"}`}>
                    {data.direction === "LONG" ? "Bullish" : "Bearish"}
                  </div>
                </div>
                <div className="bg-[#1a1c24] p-3 md:p-4 rounded-xl border border-white/5 min-w-[125px] md:min-w-0 flex-1 flex flex-col justify-between">
                  <div className="text-[11px] md:text-sm text-gray-400 mb-0.5 md:mb-1">MAE</div>
                  <div className="text-base md:text-2xl font-bold">{data.mae ? `${data.mae.toFixed(4)}%` : "N/A"}</div>
                </div>
              </div>
            </div>

            {/* Bottom Ad - Desktop only */}
            <div className="hidden md:block text-center mt-6">
              <a href="https://one.exnessonelink.com/intl/en/a/thvdkhvd" target="_blank" rel="noopener noreferrer" className="inline-block">
                <img src="https://d3dpet1g0ty5ed.cloudfront.net/EN_Trade_USOIL_with_Exness_720x90.png" className="max-w-full h-auto rounded-xl border border-white/5" alt="Exness Ad" />
              </a>
            </div>

            {/* Footer */}
            <div className="border-t border-white/10 mt-8 pt-6 pb-12 text-center text-sm text-gray-500 max-w-[1200px] mx-auto">
              <div>Auto refreshes every 5 minutes</div>
              <div className="mt-2">
                To purchase this bot or finetune a custom asset:{" "}
                <a href="mailto:arnkl@gmail.com" className="text-[#229ED9] hover:underline font-semibold">
                  arkankl07@gmail.com
                </a>
              </div>
              <div className="mt-2 text-xs opacity-75">
                This is for educational purposes only and does not constitute financial advice.
              </div>
            </div>
          </>
        ) : (
          <div className="text-red-400">Failed to load forecast data. Is the backend running?</div>
        )}
      </div>

      <NewsTicker apiUrl={API_BASE_URL} />
    </main>
  );
}
