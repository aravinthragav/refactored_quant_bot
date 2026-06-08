"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Calendar, User, BookOpen, Clock, Sparkles } from "lucide-react";
import Footer from "@/components/Footer";

interface BlogPost {
  id: number;
  created_at: string;
  title: string;
  slug: string;
  summary: string;
  content: string;
  author: string;
}

export default function BlogDetailPage() {
  const params = useParams();
  const slug = params?.slug as string;
  const [post, setPost] = useState<BlogPost | null>(null);
  const [loading, setLoading] = useState(true);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://api.aigoldforecast.com";

  useEffect(() => {
    if (!slug) return;
    async function fetchPost() {
      try {
        const res = await fetch(`${apiUrl}/api/blog/${slug}`);
        const data = await res.json();
        if (data.success) {
          setPost(data.post);
        }
      } catch (err) {
        console.error("Failed to load blog post:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchPost();
  }, [slug, apiUrl]);

  // Premium inline formatting parser
  function parseInlineFormatting(text: string) {
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return (
          <strong key={i} className="font-bold text-primary">
            {part.slice(2, -2)}
          </strong>
        );
      }
      return part;
    });
  }

  // Pure React Custom Markdown Renderer
  function renderMarkdown(md: string) {
    if (!md) return null;
    const lines = md.split("\n");
    let inList = false;
    const elements: React.ReactNode[] = [];

    lines.forEach((line, index) => {
      const trimmed = line.trim();
      
      // Header 1
      if (trimmed.startsWith("# ")) {
        inList = false;
        elements.push(
          <h1 key={index} className="text-3xl sm:text-4xl font-extrabold text-white mt-8 mb-4 border-b border-outline-variant/30 pb-3 tracking-tight font-playfair">
            {trimmed.slice(2)}
          </h1>
        );
        return;
      }

      // Header 2
      if (trimmed.startsWith("## ")) {
        inList = false;
        elements.push(
          <h2 key={index} className="text-2xl font-bold text-white mt-8 mb-4 flex items-center gap-2 border-l-4 border-primary pl-3 font-playfair">
            {trimmed.slice(3)}
          </h2>
        );
        return;
      }

      // Header 3
      if (trimmed.startsWith("### ")) {
        inList = false;
        elements.push(
          <h3 key={index} className="text-xl font-bold text-on-surface mt-6 mb-3 font-playfair">
            {trimmed.slice(4)}
          </h3>
        );
        return;
      }

      // Bullet List Items
      if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
        if (!inList) {
          inList = true;
        }
        elements.push(
          <ul key={index} className="list-disc list-inside text-on-surface-variant ml-4 mb-2 space-y-1">
            <li className="leading-relaxed">{parseInlineFormatting(trimmed.slice(2))}</li>
          </ul>
        );
        return;
      }

      // Empty Lines
      if (!trimmed) {
        inList = false;
        elements.push(<div key={index} className="h-4" />);
        return;
      }

      // Regular paragraphs
      inList = false;
      elements.push(
        <p key={index} className="text-on-surface-variant text-base leading-relaxed mb-4">
          {parseInlineFormatting(trimmed)}
        </p>
      );
    });

    return elements;
  }

  const formattedDate = post
    ? new Date(post.created_at).toLocaleDateString("en-US", {
        month: "long",
        day: "numeric",
        year: "numeric",
      })
    : "";

  return (
    <div className="min-h-screen text-white selection:bg-primary/30 selection:text-gold-light pb-20" style={{ backgroundColor: "#06070a" }}>
      {/* Ambient glows */}
      <div className="absolute top-0 left-10 w-[500px] h-[500px] bg-[rgba(212,175,55,0.05)] rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-1/4 right-10 w-[600px] h-[600px] bg-[rgba(33,150,243,0.04)] rounded-full blur-[150px] pointer-events-none" />

      <div className="w-full px-4 md:px-12 py-8 relative z-10">
        {/* Navigation */}
        <header className="flex items-center justify-between mb-12 border-b border-outline-variant/30 pb-6">
          <Link
            href="/blog"
            className="flex items-center gap-2 text-sm text-on-surface-variant hover:text-white transition-colors duration-200 group"
          >
            <ArrowLeft className="h-4 w-4 transition-transform duration-200 group-hover:-translate-x-1" />
            Back to Journal
          </Link>
          <div className="flex items-center gap-2 text-xs text-on-surface-variant bg-primary/5 px-3 py-1 rounded-full border border-primary/20">
            <BookOpen className="h-3.5 w-3.5 text-primary" />
            AI Intelligence Report
          </div>
        </header>

        {loading ? (
          <div className="animate-pulse space-y-6">
            <div className="h-4 w-1/4 bg-white/10 rounded" />
            <div className="h-10 w-3/4 bg-white/10 rounded" />
            <div className="h-4 w-1/2 bg-white/10 rounded" />
            <div className="h-48 w-full bg-white/10 rounded mt-10" />
          </div>
        ) : post ? (
          <article className="rounded-xl glass-card p-6 sm:p-10">
            {/* Tag/Category */}
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-primary/20 bg-primary/5 text-primary text-xs font-semibold uppercase tracking-wider mb-6">
              <Sparkles className="h-3 w-3" />
              Daily Spot Gold Analysis
            </div>

            {/* Title */}
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight text-white mb-6 leading-tight font-playfair">
              {post.title}
            </h1>

            {/* Meta data row */}
            <div className="flex flex-wrap items-center gap-6 text-sm text-on-surface-variant mb-8 pb-8 border-b border-outline-variant/30">
              <span className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-primary" />
                {formattedDate}
              </span>
              <span className="flex items-center gap-2">
                <User className="h-4 w-4 text-primary" />
                {post.author}
              </span>
              <span className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-primary" />
                3 min read
              </span>
            </div>

            {/* Executive Summary Callout */}
            <div className="border border-primary/20 bg-primary/5 rounded-xl p-5 mb-8 text-on-surface-variant text-base leading-relaxed italic">
              <strong>Report Summary:</strong> {post.summary}
            </div>

            {/* Markdown rendered body */}
            <div className="prose prose-invert max-w-none mb-10">
              {renderMarkdown(post.content)}
            </div>

            {/* Premium Broker CTA Banner */}
            <div className="border border-primary/30 bg-primary/10 rounded-xl p-6 backdrop-blur-md relative overflow-hidden flex flex-col sm:flex-row items-center justify-between gap-6 mt-10">
              <div className="absolute top-0 right-0 w-[150px] h-[150px] bg-primary/10 rounded-full blur-[40px] pointer-events-none" />
              <div>
                <h3 className="text-lg font-bold text-white mb-1.5 flex items-center gap-2 font-playfair">
                  <Sparkles className="h-5 w-5 text-primary" />
                  Ready to execute these signals?
                </h3>
                <p className="text-on-surface-variant text-xs sm:text-sm leading-relaxed max-w-xl">
                  Trade Spot Gold (XAU/USD) with our recommended broker **Exness**. Experience raw spreads, 0% commissions, dynamic leverage, and instant deposit/withdrawal processing.
                </p>
              </div>
              <a
                href="https://one.exnessonelink.com/intl/en/a/thvdkhvd"
                target="_blank"
                rel="noopener noreferrer"
                className="w-full sm:w-auto text-center shrink-0 px-6 py-3 bg-primary hover:bg-gold-light text-on-primary text-sm font-bold rounded-xl shadow-[0_0_20px_rgba(212,175,55,0.25)] hover:shadow-[0_0_25px_rgba(212,175,55,0.35)] transition-all duration-300 premium-hover-btn no-underline"
              >
                Trade on Exness
              </a>
            </div>
          </article>
        ) : (
          <div className="text-center py-20 border border-outline-variant/30 glass-card rounded-xl">
            <h3 className="text-lg font-bold font-playfair">Post not found</h3>
            <p className="text-on-surface-variant text-sm mt-1">
              The article slug you requested could not be located in our archives.
            </p>
            <Link
              href="/blog"
              className="mt-6 inline-flex items-center justify-center px-4 py-2 bg-primary text-on-primary text-sm font-bold rounded-xl hover:bg-gold-light transition-colors no-underline"
            >
              Return to Blog
            </Link>
          </div>
        )}
      </div>
      <Footer />
    </div>
  );
}
