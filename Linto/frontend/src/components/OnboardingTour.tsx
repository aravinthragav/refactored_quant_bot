"use client";

import React, { useEffect, useState } from "react";

interface Step {
  target: string;
  title: string;
  content: string;
}

const TOUR_STEPS: Step[] = [
  {
    target: "tour-header",
    title: "Welcome to AI Gold Forecast Terminal! 🟡",
    content: "This Executive Terminal provides real-time commodities intelligence. We track live metrics and maintain a 71.4% signal accuracy rate over our last 30 alerts.",
  },
  {
    target: "tour-metrics",
    title: "Real-Time Forecasting Metrics 📊",
    content: "Monitor current spot gold prices, model-forecasted targets, expected movement percentages, buy/sell directional bias, and the Mean Absolute Error (MAE) instantly.",
  },
  {
    target: "tour-chart",
    title: "Interactive Deep Learning Chart 📈",
    content: "Observe active 20 & 89 hourly Exponential Moving Averages alongside our model's unique forecast curve (the orange line) to time session breakouts and reversals.",
  },
  {
    target: "tour-sidebars",
    title: "Market Intelligence & Strategies 📰",
    content: "Read daily AI-generated session reports in the Blog and review 10 quantitative trading rules (breakouts, crossovers, straddles) to confirm your execution entries.",
  },
];

interface OnboardingTourProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function OnboardingTour({ isOpen, onClose }: OnboardingTourProps) {
  const [currentStep, setCurrentStep] = useState(0);

  // Target highlighting and scrolling
  useEffect(() => {
    if (!isOpen) return;

    const step = TOUR_STEPS[currentStep];
    const element = document.getElementById(step.target);

    // Reset style modifications on previous targets
    TOUR_STEPS.forEach((s) => {
      const el = document.getElementById(s.target);
      if (el) {
        el.classList.remove("tour-highlight");
      }
    });

    if (element && element.offsetWidth > 0 && element.offsetHeight > 0) {
      // Add visual glow to current target without changing relative position / z-index to stay non-blocking
      element.classList.add("tour-highlight");
      // Scroll target smoothly into view
      element.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    return () => {
      // Clean up highlights on step change or close
      TOUR_STEPS.forEach((s) => {
        const el = document.getElementById(s.target);
        if (el) {
          el.classList.remove("tour-highlight");
        }
      });
    };
  }, [isOpen, currentStep]);

  if (!isOpen) return null;

  const step = TOUR_STEPS[currentStep];
  const isLastStep = currentStep === TOUR_STEPS.length - 1;

  const handleNext = () => {
    if (isLastStep) {
      onClose();
    } else {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <div className="fixed bottom-24 right-4 md:right-8 z-[9999] w-[340px] glass-card gold-rim p-5 rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.85),0_0_30px_rgba(212,175,55,0.15)] animate-fade-up border border-primary/20">
      {/* Progress Tracker */}
      <div className="flex justify-between items-center mb-3">
        <span className="text-[10px] font-bold tracking-widest uppercase text-primary">
          Step {currentStep + 1} of {TOUR_STEPS.length}
        </span>
        <button
          onClick={onClose}
          className="text-on-surface-variant hover:text-primary transition-colors text-xs font-semibold uppercase tracking-wider bg-transparent border-none cursor-pointer"
        >
          Skip
        </button>
      </div>

      {/* Header & Description */}
      <h4 className="text-sm font-bold text-white mb-2 font-playfair leading-tight">
        {step.title}
      </h4>
      <p className="text-[11px] text-on-surface-variant/90 leading-relaxed font-sans font-medium mb-5">
        {step.content}
      </p>

      {/* Footer Actions */}
      <div className="flex justify-between items-center border-t border-outline-variant/20 pt-4 mt-2">
        <button
          onClick={handleBack}
          disabled={currentStep === 0}
          className="text-[10px] font-bold uppercase tracking-wider border border-primary/20 bg-primary/5 hover:bg-primary/10 disabled:opacity-40 disabled:hover:bg-primary/5 text-primary px-3.5 py-1.5 rounded-lg transition-all"
        >
          ← Back
        </button>
        
        <button
          onClick={handleNext}
          className="text-[10px] font-bold uppercase tracking-wider bg-primary hover:bg-gold-light text-on-primary px-5 py-2 rounded-lg shadow-[0_0_10px_rgba(212,175,55,0.3)] transition-all active:scale-95"
        >
          {isLastStep ? "Finish ✓" : "Next →"}
        </button>
      </div>
    </div>
  );
}
