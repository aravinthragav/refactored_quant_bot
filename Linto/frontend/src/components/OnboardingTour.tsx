"use client";

import React, { useEffect, useState, useRef } from "react";

interface Step {
  target: string;
  title: string;
  content: string;
  position: "bottom" | "top" | "center";
}

const TOUR_STEPS: Step[] = [
  {
    target: "tour-header",
    title: "Welcome to AI Gold Forecast Terminal! 🟡",
    content: "This Executive Terminal provides real-time commodities intelligence. We track live metrics and maintain a 71.4% signal accuracy rate over our last 30 alerts.",
    position: "bottom",
  },
  {
    target: "tour-metrics",
    title: "Real-Time Forecasting Metrics 📊",
    content: "Monitor current spot gold prices, model-forecasted targets, expected movement percentages, buy/sell directional bias, and the Mean Absolute Error (MAE) instantly.",
    position: "bottom",
  },
  {
    target: "tour-chart",
    title: "Interactive Deep Learning Chart 📈",
    content: "Observe active 20 & 89 hourly Exponential Moving Averages alongside our model's unique forecast curve (the orange line) to time session breakouts and reversals.",
    position: "top",
  },
  {
    target: "tour-sidebars",
    title: "Market Intelligence & Strategies 📰",
    content: "Read daily AI-generated session reports in the Blog and review 10 quantitative trading rules (breakouts, crossovers, straddles) to confirm your execution entries.",
    position: "top",
  },
];

interface OnboardingTourProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function OnboardingTour({ isOpen, onClose }: OnboardingTourProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [coords, setCoords] = useState<{ top: number; left: number; position: string }>({
    top: 0,
    left: 0,
    position: "center",
  });
  const tooltipRef = useRef<HTMLDivElement>(null);

  // Position calculation
  useEffect(() => {
    if (!isOpen) return;

    const calculatePosition = () => {
      const step = TOUR_STEPS[currentStep];
      const element = document.getElementById(step.target);

      // Reset style modifications on previous targets
      TOUR_STEPS.forEach((s) => {
        const el = document.getElementById(s.target);
        if (el) {
          el.classList.remove("tour-highlight");
          el.style.zIndex = "";
          el.style.position = "";
        }
      });

      if (!element || element.offsetWidth === 0 || element.offsetHeight === 0) {
        // Fallback to center if element is hidden/missing on current screen size (e.g. sidebars on mobile)
        setCoords({
          top: window.innerHeight / 2,
          left: window.innerWidth / 2,
          position: "center",
        });
        return;
      }

      // Add high z-index highlight to target
      element.classList.add("tour-highlight");
      element.style.position = "relative";
      element.style.zIndex = "99999";

      // Scroll target smoothly into view
      element.scrollIntoView({ behavior: "smooth", block: "center" });

      // Calculate coordinates after a short delay to allow scrolling to finalize
      setTimeout(() => {
        const rect = element.getBoundingClientRect();
        const tooltipWidth = tooltipRef.current?.offsetWidth || 340;
        const tooltipHeight = tooltipRef.current?.offsetHeight || 160;

        let top = 0;
        let left = rect.left + window.scrollX + (rect.width - tooltipWidth) / 2;

        if (step.position === "bottom") {
          top = rect.bottom + window.scrollY + 16;
        } else {
          top = rect.top + window.scrollY - tooltipHeight - 16;
        }

        // Viewport clamping to keep tooltips on screen
        left = Math.max(16, Math.min(left, window.innerWidth - tooltipWidth - 16));
        top = Math.max(16, top);

        setCoords({ top, left, position: "absolute" });
      }, 300);
    };

    calculatePosition();
    window.addEventListener("resize", calculatePosition);

    return () => {
      window.removeEventListener("resize", calculatePosition);
      // Clean up highlights on unmount or step change
      TOUR_STEPS.forEach((s) => {
        const el = document.getElementById(s.target);
        if (el) {
          el.classList.remove("tour-highlight");
          el.style.zIndex = "";
          el.style.position = "";
        }
      });
    };
  }, [isOpen, currentStep]);

  // Ensure tooltip itself is scrolled into view if it goes off-screen
  useEffect(() => {
    if (isOpen && coords.position === "absolute") {
      // Small timeout to let coordinate rendering paint first
      const t = setTimeout(() => {
        tooltipRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }, 100);
      return () => clearTimeout(t);
    }
  }, [coords, isOpen]);

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
    <>
      {/* Dark Backdrop Overlay */}
      <div 
        onClick={onClose}
        className="fixed inset-0 bg-[#06070a]/82 backdrop-blur-[2px] z-[99990] transition-opacity duration-300" 
      />

      {/* Floating Tooltip Card */}
      <div
        ref={tooltipRef}
        style={
          coords.position === "center"
            ? {
                position: "fixed",
                top: "50%",
                left: "50%",
                transform: "translate(-50%, -50%)",
              }
            : {
                position: "absolute",
                top: `${coords.top}px`,
                left: `${coords.left}px`,
              }
        }
        className="z-[99999] w-[340px] glass-card gold-rim p-5 rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.8),0_0_30px_rgba(212,175,55,0.1)] transition-all duration-300"
      >
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
    </>
  );
}
