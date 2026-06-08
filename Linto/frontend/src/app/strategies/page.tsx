"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, BookOpen, Compass, ShieldAlert, Award, ArrowUpRight, ArrowDownRight } from "lucide-react";

interface Strategy {
  id: number;
  name: string;
  tagline: string;
  timeframe: string;
  indicators: string[];
  description: string;
  buyRules: string[];
  sellRules: string[];
  riskManagement: string;
}

const strategies: Strategy[] = [
  {
    id: 1,
    name: "EMA 20 & 89 Trend Crossover",
    tagline: "Follow major momentum swings by tracking the intersection of fast and median trend averages.",
    timeframe: "30m / 1H",
    indicators: ["Exponential Moving Average (EMA 20)", "Exponential Moving Average (EMA 89)"],
    description: "This strategy seeks to catch the beginning of sustained directional trends. Gold tends to respect moving averages, using the EMA 89 as a median support/resistance line and the EMA 20 as an active momentum filter.",
    buyRules: [
      "The fast EMA 20 crosses above the median EMA 89 from below.",
      "Price holds and closes above the crossover point on the confirmation candle.",
      "Enter a long position on the open of the next candle."
    ],
    sellRules: [
      "The fast EMA 20 crosses below the median EMA 89 from above.",
      "Price holds and closes below the crossover point on the confirmation candle.",
      "Enter a short position on the open of the next candle."
    ],
    riskManagement: "Place the Stop Loss 15-20 pips ($1.50 - $2.00 in Gold) below the cross point for longs, or above it for shorts. Target a 1:1.5 or 1:2 Risk-to-Reward ratio."
  },
  {
    id: 2,
    name: "ATR Volatility Breakout",
    tagline: "Enter high-velocity trades when price breaks out of consolidation with volume expansion.",
    timeframe: "15m / 30m",
    indicators: ["Average True Range (ATR 14)", "Donchian Channels (20)"],
    description: "Gold spends a significant portion of the day consolidating. When it breaks out of a narrow range with high ATR expansion, it signals institutional participation. This strategy captures that explosive breakout momentum.",
    buyRules: [
      "Spot Gold has been trading in a tight consolidation range for at least 3 hours.",
      "The current candle breaks out above the upper Donchian Channel boundary.",
      "The ATR value spikes above its 20-period average, validating the breakout volume."
    ],
    sellRules: [
      "Spot Gold has been trading in a tight consolidation range for at least 3 hours.",
      "The current candle breaks out below the lower Donchian Channel boundary.",
      "The ATR value spikes above its 20-period average, validating the breakdown volume."
    ],
    riskManagement: "Place the Stop Loss at the median line of the consolidation channel (usually 1.5x ATR). Trail the Stop Loss at the lower channel boundary as the trade moves in profit."
  },
  {
    id: 3,
    name: "S/R Range Bounce",
    tagline: "Buy near historical support and sell near historical resistance in a consolidated market.",
    timeframe: "15m / 1H",
    indicators: ["Historical Support & Resistance Levels", "Stochastic Oscillator (14, 3, 3)"],
    description: "During quiet market conditions (e.g. Asian session), Gold oscillates reliably between horizontal key zones. Buying at support and selling at resistance with oscillators confirming exhaustion is a highly profitable strategy.",
    buyRules: [
      "Gold price approaches a verified horizontal support level.",
      "The Stochastic Oscillator falls below 20 (oversold) and prints a bullish %K/%D crossover.",
      "A bullish rejection candlestick (e.g. Pin Bar or Engulfing) forms at the support level."
    ],
    sellRules: [
      "Gold price approaches a verified horizontal resistance level.",
      "The Stochastic Oscillator rises above 80 (overbought) and prints a bearish %K/%D crossover.",
      "A bearish rejection candlestick (e.g. Shooting Star or Engulfing) forms at the resistance level."
    ],
    riskManagement: "Place the Stop Loss 10 pips ($1.00) below the support zone for longs, or above the resistance zone for shorts. Target the opposite end of the range."
  },
  {
    id: 4,
    name: "RSI Momentum Divergence",
    tagline: "Identify trend exhaustion and catch early reversals before they become obvious.",
    timeframe: "15m / 1H",
    indicators: ["Relative Strength Index (RSI 14)", "Price Action Highs/Lows"],
    description: "Divergence occurs when price action and momentum indicator trends disagree. If Gold makes a new high but momentum fails to print a new high, it indicates smart money is exiting, setting up a sharp reversal.",
    buyRules: [
      "Price action makes a lower low (LL).",
      "RSI prints a higher low (HL) in the oversold region (under 30).",
      "Enter long when the price breaks above the high of the first bullish rejection candle."
    ],
    sellRules: [
      "Price action makes a higher high (HH).",
      "RSI prints a lower high (LH) in the overbought region (over 70).",
      "Enter short when the price breaks below the low of the first bearish rejection candle."
    ],
    riskManagement: "Place the Stop Loss just below the swing low for longs, or above the swing high for shorts. Target the nearest EMA 89 line or key pivot zone."
  },
  {
    id: 5,
    name: "MACD Histogram Reversals",
    tagline: "Capture micro-reversals in trend momentum during active session overlaps.",
    timeframe: "15m",
    indicators: ["MACD (12, 26, 9)", "RSI (14)"],
    description: "The MACD histogram represents the distance between the MACD line and the signal line. When the histogram bars start shrinking in size, it signals that the current micro-trend is losing momentum, offering high Risk-to-Reward reversals.",
    buyRules: [
      "RSI is oversold (under 30) or approaching it.",
      "MACD histogram is below the zero line and prints at least three consecutive shrinking red bars.",
      "Enter long when the histogram color shifts or crosses back towards the zero line."
    ],
    sellRules: [
      "RSI is overbought (over 70) or approaching it.",
      "MACD histogram is above the zero line and prints at least three consecutive shrinking green bars.",
      "Enter short when the histogram color shifts or crosses back towards the zero line."
    ],
    riskManagement: "Place the Stop Loss 12 pips below the recent swing low. Take partial profits at a 1:1 Risk-to-Reward ratio, and let the remaining run with a break-even stop."
  },
  {
    id: 6,
    name: "Fibonacci Golden Ratio Entry",
    tagline: "Enter pullback trades at high-confluence zones in the direction of the dominant trend.",
    timeframe: "30m / 4H / D",
    indicators: ["Fibonacci Retracement tool", "EMA 20"],
    description: "When Gold begins a strong trend, it rarely moves in a straight line. Pullbacks to the 50.0% and 61.8% (Golden Ratio) Fibonacci levels attract massive buyer/seller liquidity. Entering at these pullbacks offers optimal entry prices.",
    buyRules: [
      "Identify a clear, strong uptrend on the daily/4H chart.",
      "Draw the Fibonacci retracement from the recent swing low to the swing high.",
      "Wait for the price to pull back to the 50% or 61.8% retracement level.",
      "Enter long when a bullish confirmation candle appears at the Fibonacci zone."
    ],
    sellRules: [
      "Identify a clear, strong downtrend on the daily/4H chart.",
      "Draw the Fibonacci retracement from the recent swing high to the swing low.",
      "Wait for the price to pull back to the 50% or 61.8% retracement level.",
      "Enter short when a bearish confirmation candle appears at the Fibonacci zone."
    ],
    riskManagement: "Stop Loss is placed below the 78.6% retracement level. Take Profit targets are the 0% level (recent high/low) and the -27% Fibonacci extension."
  },
  {
    id: 7,
    name: "Bollinger Bands Volatility Squeeze",
    tagline: "Position yourself for explosive breakouts when market volatility contracts.",
    timeframe: "30m / 1H",
    indicators: ["Bollinger Bands (20, 2)", "Average True Range (ATR)"],
    description: "Upticks in volatility always follow periods of low volatility. When Bollinger Bands contract (squeeze) to a historical minimum, it indicates an explosive breakout is imminent. We enter in the direction of the breakout candle.",
    buyRules: [
      "The upper and lower Bollinger Bands contract tightly, with width at its lowest in 24 hours.",
      "A strong bullish candle breaks out and closes completely above the upper Bollinger Band.",
      "Enter long immediately on the close of the breakout candle."
    ],
    sellRules: [
      "The upper and lower Bollinger Bands contract tightly, with width at its lowest in 24 hours.",
      "A strong bearish candle breaks out and closes completely below the lower Bollinger Band.",
      "Enter short immediately on the close of the breakout candle."
    ],
    riskManagement: "Place the Stop Loss on the opposite side of the median Bollinger Band (20 SMA). Trail the Stop Loss at the median band as the trend develops."
  },
  {
    id: 8,
    name: "Multi-Timeframe Trend Alignment",
    tagline: "Only trade in alignment with institutional direction by checking the H4 and Daily trend.",
    timeframe: "5m (Entry) / 4H & Daily (Trend)",
    indicators: ["EMA 89 (on H4)", "EMA 20 (on 5m)"],
    description: "Trading against the higher timeframe trend is a primary reason retail traders fail. This strategy filters out 5-minute noise, ensuring you only take buy signals if the 4-hour trend is bullish, and sell signals if the 4-hour trend is bearish.",
    buyRules: [
      "Higher Timeframe check: H4 Gold price must be trading above the H4 EMA 89.",
      "On the 5-minute chart, wait for the price to dip below the 5m EMA 20.",
      "Enter long when the price crosses back above the 5m EMA 20 with a strong bullish candle."
    ],
    sellRules: [
      "Higher Timeframe check: H4 Gold price must be trading below the H4 EMA 89.",
      "On the 5-minute chart, wait for the price to rally above the 5m EMA 20.",
      "Enter short when the price crosses back below the 5m EMA 20 with a strong bearish candle."
    ],
    riskManagement: "Place Stop Loss at the recent swing low on the 5m chart. Target 2 to 3 times the risk amount by trailing profit via the 5m EMA 20 line."
  },
  {
    id: 9,
    name: "Macro News Straddle Strategy",
    tagline: "Capture rapid momentum surges on major economic releases like CPI, NFP, and FOMC.",
    timeframe: "5m / Pre-release",
    indicators: ["Macro Risk Index", "Horizontal range levels"],
    description: "Major news events create instant 100-200 pip swings in Gold. Since predicting the direction of the news is highly risky, this strategy places pending orders on both sides of a tight pre-news range to capture whichever direction breaks out.",
    buyRules: [
      "Verify a high-impact USD economic event (CPI, NFP, rate decision) is scheduled in 10 minutes.",
      "Identify the high and low of the range established over the last 30 minutes.",
      "Place a Buy Stop order 5 pips ($0.50) above the range high, 2 minutes before the release."
    ],
    sellRules: [
      "Verify a high-impact USD economic event (CPI, NFP, rate decision) is scheduled in 10 minutes.",
      "Identify the high and low of the range established over the last 30 minutes.",
      "Place a Sell Stop order 5 pips ($0.50) below the range low, 2 minutes before the release."
    ],
    riskManagement: "Place the Stop Loss for each order at the opposite side of the pre-news range. Once one order triggers, immediately cancel the other order. Set a take profit target of 1:2 Risk-to-Reward."
  },
  {
    id: 10,
    name: "London/NY Session Open Breakout",
    tagline: "Trade the high-liquidity volume surges during the major forex market overlaps.",
    timeframe: "5m / 15m",
    indicators: ["Session High/Low range indicator"],
    description: "Gold volume spikes dramatically at the London open (07:00 UTC) and New York open (12:30 UTC). This strategy tracks the high and low of the range established in the 30 minutes prior to the open, and trades the breakout.",
    buyRules: [
      "Identify the highest and lowest price points during the 30 minutes prior to the session open.",
      "At the session open, wait for a 5-minute candle to break and close above the range high.",
      "Enter long on the close of the breakout candle."
    ],
    sellRules: [
      "Identify the highest and lowest price points during the 30 minutes prior to the session open.",
      "At the session open, wait for a 5-minute candle to break and close below the range low.",
      "Enter short on the close of the breakout candle."
    ],
    riskManagement: "Stop Loss is placed at the midpoint of the pre-session range. Take Profit should be set to 1.5 times the range height."
  }
];

export default function StrategiesPage() {
  const [selectedId, setSelectedId] = useState(1);
  const activeStrategy = strategies.find((s) => s.id === selectedId) || strategies[0];

  return (
    <div className="min-h-screen bg-[#070b13] text-white selection:bg-amber-500/30 selection:text-amber-200">
      {/* Ambient glows */}
      <div className="absolute top-0 right-10 w-[500px] h-[500px] bg-amber-500/5 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-10 left-10 w-[600px] h-[600px] bg-blue-500/5 rounded-full blur-[150px] pointer-events-none" />

      <div className="max-w-6xl mx-auto px-4 py-8 relative z-10">
        {/* Navigation */}
        <header className="flex items-center justify-between mb-12 border-b border-white/10 pb-6">
          <Link
            href="/"
            className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors duration-200 group"
          >
            <ArrowLeft className="h-4 w-4 transition-transform duration-200 group-hover:-translate-x-1" />
            Back to Terminal
          </Link>
          <div className="flex items-center gap-3">
            <Compass className="h-5 w-5 text-amber-500" />
            <span className="text-sm font-semibold tracking-wider text-slate-300 uppercase">
              Trading Playbook
            </span>
          </div>
        </header>

        {/* Hero */}
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h1 className="text-4xl sm:text-5xl font-black tracking-tight text-white mb-6 leading-tight">
            Gold Trading <span className="bg-gradient-to-r from-amber-400 via-amber-200 to-yellow-500 bg-clip-text text-transparent">Strategies</span>
          </h1>
          <p className="text-slate-300 text-lg leading-relaxed">
            Explore 10 proven, institutional-grade quantitative strategies specifically customized for trading Gold (XAU/USD).
          </p>
        </div>

        {/* Dynamic Interactive Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left Navigation Panel */}
          <div className="lg:col-span-4 space-y-3 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
            {strategies.map((strategy) => (
              <button
                key={strategy.id}
                onClick={() => setSelectedId(strategy.id)}
                className={`w-full text-left p-4 rounded-xl border transition-all duration-300 flex items-start gap-3 ${
                  selectedId === strategy.id
                    ? "border-amber-500/50 bg-amber-500/10 text-white shadow-[0_0_15px_-3px_rgba(245,158,11,0.2)]"
                    : "border-white/5 bg-white/[0.01] hover:border-white/15 hover:bg-white/[0.03] text-slate-400 hover:text-slate-200"
                }`}
              >
                <span className={`h-6 w-6 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 mt-0.5 ${
                  selectedId === strategy.id ? "bg-amber-500 text-black" : "bg-white/10 text-white"
                }`}>
                  {strategy.id}
                </span>
                <div>
                  <h3 className="font-bold text-sm leading-snug">{strategy.name}</h3>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-1">{strategy.tagline}</p>
                </div>
              </button>
            ))}
          </div>

          {/* Right Content Details Panel */}
          <div className="lg:col-span-8">
            <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6 sm:p-8 backdrop-blur-md relative overflow-hidden min-h-[500px]">
              {/* Decorative top border glow */}
              <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-amber-500/50 to-transparent" />
              
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-6 mb-6">
                <div>
                  <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-amber-500/20 bg-amber-500/5 text-amber-400 text-xs font-semibold uppercase tracking-wider mb-3">
                    Strategy #{activeStrategy.id}
                  </div>
                  <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-white">
                    {activeStrategy.name}
                  </h2>
                </div>
                
                {/* Timeframe Pill */}
                <div className="shrink-0 flex flex-col items-start sm:items-end gap-1">
                  <span className="text-xs text-slate-400">RECOMMENDED TIMEFRAME</span>
                  <span className="bg-white/5 border border-white/10 px-3 py-1 rounded-lg text-sm font-bold text-slate-200">
                    {activeStrategy.timeframe}
                  </span>
                </div>
              </div>

              {/* Description */}
              <p className="text-slate-300 text-base leading-relaxed mb-6">
                {activeStrategy.description}
              </p>

              {/* Indicators Used */}
              <div className="mb-6 bg-white/[0.01] border border-white/5 rounded-xl p-4">
                <h4 className="text-xs font-bold tracking-wider text-slate-400 uppercase mb-2 flex items-center gap-1.5">
                  <Award className="h-4 w-4 text-amber-500" />
                  Key Indicators Used
                </h4>
                <div className="flex flex-wrap gap-2">
                  {activeStrategy.indicators.map((ind, i) => (
                    <span key={i} className="text-xs bg-white/5 border border-white/10 rounded-full px-3 py-1 text-slate-200">
                      {ind}
                    </span>
                  ))}
                </div>
              </div>

              {/* Rules Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                {/* Buy Rules */}
                <div className="border border-green-500/10 bg-green-500/[0.01] rounded-xl p-5">
                  <h4 className="font-bold text-green-400 text-sm flex items-center gap-1.5 mb-3 border-b border-green-500/10 pb-2">
                    <ArrowUpRight className="h-5 w-5" />
                    Buy Trigger Conditions
                  </h4>
                  <ol className="list-decimal list-inside text-xs text-slate-300 space-y-2">
                    {activeStrategy.buyRules.map((rule, idx) => (
                      <li key={idx} className="leading-relaxed pl-1">{rule}</li>
                    ))}
                  </ol>
                </div>

                {/* Sell Rules */}
                <div className="border border-red-500/10 bg-red-500/[0.01] rounded-xl p-5">
                  <h4 className="font-bold text-red-400 text-sm flex items-center gap-1.5 mb-3 border-b border-red-500/10 pb-2">
                    <ArrowDownRight className="h-5 w-5" />
                    Sell Trigger Conditions
                  </h4>
                  <ol className="list-decimal list-inside text-xs text-slate-300 space-y-2">
                    {activeStrategy.sellRules.map((rule, idx) => (
                      <li key={idx} className="leading-relaxed pl-1">{rule}</li>
                    ))}
                  </ol>
                </div>
              </div>

              {/* Risk Management */}
              <div className="border border-amber-500/20 bg-amber-500/5 rounded-xl p-5 flex items-start gap-4">
                <ShieldAlert className="h-6 w-6 text-amber-500 shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-bold text-amber-400 text-sm mb-1.5">Risk Management & Stop Placement</h4>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {activeStrategy.riskManagement}
                  </p>
                </div>
              </div>

            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
