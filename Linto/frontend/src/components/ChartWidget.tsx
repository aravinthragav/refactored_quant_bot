"use client";

import React, { useEffect, useRef } from "react";
import { createChart, ColorType, CrosshairMode, CandlestickSeries, LineSeries, createTextWatermark, createSeriesMarkers } from "lightweight-charts";

interface ChartWidgetProps {
  data: any;
}

export default function ChartWidget({ data }: ChartWidgetProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);

  useEffect(() => {
    if (!chartContainerRef.current || !data) return;



    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: "#0e1117" },
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
      height: typeof window !== "undefined" && window.innerWidth < 768 ? 400 : 600,
    });

    chartRef.current = chart;

    // Apply watermark in lightweight-charts v5
    try {
      const firstPane = chart.panes()[0];
      if (firstPane) {
        const isMarketClosed = !!data.market_closed || (data.asset_name === "GOLD" && (new Date().getDay() === 0 || new Date().getDay() === 6));
        createTextWatermark(firstPane, {
          horzAlign: "center",
          vertAlign: "center",
          lines: [
            {
              text: isMarketClosed ? "Market Closed" : "GOLD 5min",
              color: isMarketClosed ? "rgba(239, 83, 80, 0.15)" : "rgba(255, 255, 255, 0.08)",
              fontSize: isMarketClosed ? 64 : 72,
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
      const forecastColor = data.direction === "LONG" ? "#ff8c00" : "#2962ff";
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
          height: mobile ? 400 : 600
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

  return <div ref={chartContainerRef} className="w-full h-[400px] md:h-[600px] rounded-lg overflow-hidden border border-white/10" />;
}
