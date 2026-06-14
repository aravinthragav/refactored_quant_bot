"use client";

import React, { useEffect, useRef } from "react";
import { createChart, ColorType, CrosshairMode, CandlestickSeries, LineSeries, createTextWatermark, createSeriesMarkers } from "lightweight-charts";

interface ChartWidgetProps {
  data: any;
  currentInterval?: string;
  onIntervalChange?: (interval: string) => void;
}

export default function ChartWidget({ data, currentInterval = "5m", onIntervalChange }: ChartWidgetProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);

  useEffect(() => {
    if (!chartContainerRef.current || !data) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: "#0d0f16" },
        textColor: "#d1d4dc",
      },
      grid: {
        vertLines: { visible: false },
        horzLines: { visible: false },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
      },
      rightPriceScale: {
        borderColor: "#2B2B43",
      },
      timeScale: {
        borderColor: "#2B2B43",
        timeVisible: true,
        secondsVisible: false,
        rightOffset: typeof window !== "undefined" && window.innerWidth < 768 ? 12 : 35,
      },
      width: chartContainerRef.current.clientWidth,
      height: typeof window !== "undefined" && window.innerWidth < 768 ? 400 : 550,
    });

    chartRef.current = chart;

    // Apply watermark in lightweight-charts v5
    try {
      const firstPane = chart.panes()[0];
      if (firstPane) {
        createTextWatermark(firstPane, {
          horzAlign: "center",
          vertAlign: "center",
          lines: [
            {
              text: "www.aigoldforecast.com",
              color: "rgba(212, 175, 55, 0.18)",
              fontSize: 72,
            },
          ],
        });
      }
    } catch (err) {
      console.error("Watermark error:", err);
    }

    // Candlestick Series
    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#26a69a",
      downColor: "#ef5350",
      borderVisible: false,
      wickUpColor: "#26a69a",
      wickDownColor: "#ef5350",
    });

    if (data.hist_data) {
      candlestickSeries.setData(data.hist_data);
    }

    // EMA 20 Series
    if (data.ema20_data && data.ema20_data.length > 0) {
      const ema20Series = chart.addSeries(LineSeries, {
        color: "#29b6f6",
        lineWidth: 1,
        priceLineVisible: false,
        lastValueVisible: false,
      });
      ema20Series.setData(data.ema20_data);
    }

    // EMA 89 Series
    if (data.ema89_data && data.ema89_data.length > 0) {
      const ema89Series = chart.addSeries(LineSeries, {
        color: "#ec407a",
        lineWidth: 1,
        priceLineVisible: false,
        lastValueVisible: false,
      });
      ema89Series.setData(data.ema89_data);
    }

    // Forecast Line
    if (data.forecast_data) {
      const forecastColor = "#ff9800";
      const forecastSeries = chart.addSeries(LineSeries, {
        color: forecastColor,
        lineWidth: 3,
      });
      forecastSeries.setData(data.forecast_data);

      // Add markers along forecast line: small circles
      try {
        const markers = data.forecast_data.slice(1).map((item: any) => {
          return {
            time: item.time,
            position: "inBar",
            color: forecastColor,
            shape: "circle",
            size: 1,
          };
        });
        createSeriesMarkers(forecastSeries, markers);
      } catch (err) {
        console.error("Error setting forecast markers:", err);
      }
    }

    // SR Levels
    if (data.sr_levels && data.sr_levels.length > 0) {
      data.sr_levels.forEach((lvl: any) => {
        const color = lvl.type === "R" ? "rgba(255, 77, 77, 0.5)" : "rgba(0, 204, 150, 0.5)";
        candlestickSeries.createPriceLine({
          price: lvl.price,
          color: color,
          lineWidth: 1,
          lineStyle: 3, // Dashed
          axisLabelVisible: true,
          title: `${lvl.tf} ${lvl.type}`,
        });
      });
    }

    const handleResize = () => {
      if (chartContainerRef.current) {
        const mobile = window.innerWidth < 768;
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
          height: mobile ? 400 : 550
        });
        chart.timeScale().applyOptions({
          rightOffset: mobile ? 12 : 35
        });
      }
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
      chartRef.current = null;
    };
  }, [data]);

  const isLong = data?.direction?.includes("Bullish") || data?.direction === "LONG";

  return (
    <div className="glass-card rounded-xl overflow-hidden">
      {/* Chart Header */}
      <div className="flex justify-between items-center px-4 py-3 border-b border-outline-variant/30">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-playfair text-base md:text-lg font-bold gold-shimmer-text">GOLD / USD</span>
          <div className="flex items-center gap-1 bg-[#161820] p-0.5 rounded border border-outline-variant/30">
            {["5m", "15m", "30m", "1h"].map((intv) => (
              <button
                key={intv}
                onClick={() => onIntervalChange?.(intv)}
                type="button"
                className={`px-2 py-0.5 rounded text-[10px] font-extrabold uppercase transition-all duration-200 cursor-pointer ${
                  currentInterval === intv
                    ? "bg-primary text-on-primary shadow-[0_0_8px_rgba(212,175,55,0.4)]"
                    : "text-on-surface-variant/70 hover:text-on-surface hover:bg-surface-container-high"
                }`}
              >
                {intv}
              </button>
            ))}
          </div>
          {(data?.market_closed || (typeof window !== "undefined" && [0, 6].includes(new Date().getDay()))) ? (
            <span className="text-xs md:text-sm text-amber-500 font-extrabold border border-amber-500/30 bg-amber-500/10 px-3 py-1 rounded uppercase tracking-wider animate-pulse flex items-center gap-1.5 shadow-lg shadow-amber-950/20">
              <span className="w-2 h-2 rounded-full bg-amber-500 animate-ping" />
              Market is closed
            </span>
          ) : (
            <span className="text-[10px] text-secondary/70 font-semibold hidden lg:inline">
              • Auto refreshes every 5 minutes
            </span>
          )}
        </div>
        <div className="flex items-center gap-2 text-[10px] text-on-surface-variant font-semibold">
          <span className="flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: "#29b6f6" }} /> EMA(20)
          </span>
          <span className="flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: "#ec407a" }} /> EMA(89)
          </span>
          <span className="flex items-center gap-1 text-[#ff9800]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#ff9800]" /> Forecast
          </span>
        </div>
      </div>

      {/* Chart Container */}
      <div ref={chartContainerRef} className="w-full h-[400px] md:h-[550px]" />

      {/* Chart Footer */}
      <div className="flex items-center justify-between px-4 py-2 bg-surface-container-lowest/50 backdrop-blur-md border-t border-outline-variant/20 text-[10px] font-semibold text-on-surface-variant">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1">
            <span className="w-1.5 h-1.5 bg-[#26a69a] rounded-full" /> Up
          </span>
          <span className="flex items-center gap-1">
            <span className="w-1.5 h-1.5 bg-[#ef5350] rounded-full" /> Down
          </span>
        </div>
        <span className="text-primary font-bold animate-pulse tracking-wider">● LIVE</span>
      </div>
    </div>
  );
}
