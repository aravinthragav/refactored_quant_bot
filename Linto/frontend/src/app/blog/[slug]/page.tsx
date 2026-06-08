"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Calendar, User, BookOpen, Clock, Sparkles } from "lucide-react";

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
          <strong key={i} className="font-bold text-amber-300">
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
          <h1 key={index} className="text-3xl sm:text-4xl font-extrabold text-white mt-8 mb-4 border-b border-white/10 pb-3 tracking-tight">
            {trimmed.slice(2)}
          </h1>
        );
        return;
      }

      // Header 2
      if (trimmed.startsWith("## ")) {
        inList = false;
        elements.push(
          <h2 key={index} className="text-2xl font-bold text-white mt-8 mb-4 flex items-center gap-2 border-l-4 border-amber-500 pl-3">
            {trimmed.slice(3)}
          </h2>
        );
        return;
      }

      // Header 3
      if (trimmed.startsWith("### ")) {
        inList = false;
        elements.push(
          <h3 key={index} className="text-xl font-bold text-slate-100 mt-6 mb-3">
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
          <ul key={index} className="list-disc list-inside text-slate-300 ml-4 mb-2 space-y-1">
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
        <p key={index} className="text-slate-300 text-base leading-relaxed mb-4">
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
    <div className="min-h-screen bg-[#070b13] text-white selection:bg-amber-500/30 selection:text-amber-200 pb-20">
      {/* Ambient glows */}
      <div className="absolute top-0 left-10 w-[500px] h-[500px] bg-amber-500/5 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-1/4 right-10 w-[600px] h-[600px] bg-blue-500/5 rounded-full blur-[150px] pointer-events-none" />

      <div className="max-w-4xl mx-auto px-4 py-8 relative z-10">
        {/* Navigation */}
        <header className="flex items-center justify-between mb-12 border-b border-white/10 pb-6">
          <Link
            href="/blog"
            className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors duration-200 group"
          >
            <ArrowLeft className="h-4 w-4 transition-transform duration-200 group-hover:-translate-x-1" />
            Back to Journal
          </Link>
          <div className="flex items-center gap-2 text-xs text-slate-400 bg-white/5 px-3 py-1 rounded-full border border-white/10">
            <BookOpen className="h-3.5 w-3.5 text-amber-500" />
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
          <article className="rounded-2xl border border-white/10 bg-white/[0.02] p-6 sm:p-10 backdrop-blur-md">
            {/* Tag/Category */}
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-amber-500/20 bg-amber-500/5 text-amber-400 text-xs font-semibold uppercase tracking-wider mb-6">
              <Sparkles className="h-3 w-3" />
              Daily Spot Gold Analysis
            </div>

            {/* Title */}
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight text-white mb-6 leading-tight">
              {post.title}
            </h1>

            {/* Meta data row */}
            <div className="flex flex-wrap items-center gap-6 text-sm text-slate-400 mb-8 pb-8 border-b border-white/10">
              <span className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-amber-500" />
                {formattedDate}
              </span>
              <span className="flex items-center gap-2">
                <User className="h-4 w-4 text-amber-500" />
                {post.author}
              </span>
              <span className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-amber-500" />
                3 min read
              </span>
            </div>

            {/* Executive Summary Callout */}
            <div className="border border-amber-500/20 bg-amber-500/5 rounded-xl p-5 mb-8 text-slate-200 text-base leading-relaxed italic">
              <strong>Report Summary:</strong> {post.summary}
            </div>

            {/* Markdown rendered body */}
            <div className="prose prose-invert max-w-none">
              {renderMarkdown(post.content)}
            </div>
          </article>
        ) : (
          <div className="text-center py-20 border border-white/10 bg-white/[0.01] rounded-2xl">
            <h3 className="text-lg font-bold">Post not found</h3>
            <p className="text-slate-400 text-sm mt-1">
              The article slug you requested could not be located in our archives.
            </p>
            <Link
              href="/blog"
              className="mt-6 inline-flex items-center justify-center px-4 py-2 bg-amber-500 text-black text-sm font-bold rounded-xl hover:bg-amber-400 transition-colors"
            >
              Return to Blog
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
