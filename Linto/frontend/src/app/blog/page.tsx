"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { ArrowLeft, Search, TrendingUp, Sparkles, BookOpen } from "lucide-react";
import BlogCard from "@/components/BlogCard";

interface BlogPost {
  id: number;
  created_at: string;
  title: string;
  slug: string;
  summary: string;
  author: string;
}

export default function BlogLandingPage() {
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://api.aigoldforecast.com";

  useEffect(() => {
    async function fetchPosts() {
      try {
        const res = await fetch(`${apiUrl}/api/blog`);
        const data = await res.json();
        if (data.success) {
          setPosts(data.posts || []);
        }
      } catch (err) {
        console.error("Failed to load blog posts:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchPosts();
  }, [apiUrl]);

  const filteredPosts = posts.filter(
    (post) =>
      post.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      post.summary.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-[#070b13] text-white selection:bg-amber-500/30 selection:text-amber-200">
      {/* Ambient background glow */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-amber-500/5 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-1/3 right-1/4 w-[600px] h-[600px] bg-blue-500/5 rounded-full blur-[150px] pointer-events-none" />

      <div className="max-w-6xl mx-auto px-4 py-8 relative z-10">
        {/* Navigation / Header */}
        <header className="flex items-center justify-between mb-12 border-b border-white/10 pb-6">
          <Link
            href="/"
            className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors duration-200 group"
          >
            <ArrowLeft className="h-4 w-4 transition-transform duration-200 group-hover:-translate-x-1" />
            Back to Terminal
          </Link>
          <div className="flex items-center gap-3">
            <BookOpen className="h-5 w-5 text-amber-500" />
            <span className="text-sm font-semibold tracking-wider text-slate-300 uppercase">
              AI Market Journal
            </span>
          </div>
        </header>

        {/* Hero Section */}
        <div className="text-center max-w-2xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-amber-500/20 bg-amber-500/5 text-amber-400 text-xs font-semibold uppercase tracking-wider mb-6">
            <Sparkles className="h-3 w-3" />
            Daily Market Intelligence
          </div>
          <h1 className="text-4xl sm:text-5xl font-black tracking-tight text-white mb-6 leading-tight">
            Precious Metals <span className="bg-gradient-to-r from-amber-400 via-amber-200 to-yellow-500 bg-clip-text text-transparent">Forecasting & Insights</span>
          </h1>
          <p className="text-slate-300 text-lg leading-relaxed">
            Read daily technical reports, deep-learning forecast reviews, and session recommendation guidelines compiled automatically by our gold-finetuned AI model.
          </p>
        </div>

        {/* Filters and Search */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mb-10">
          <div className="relative w-full sm:w-80">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4.5 w-4.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search reports..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-white/10 bg-white/[0.02] text-sm text-white placeholder-slate-400 focus:outline-none focus:border-amber-500/50 focus:bg-white/[0.05] transition-all duration-300"
            />
          </div>
          <div className="text-sm text-slate-400">
            Showing {filteredPosts.length} report{filteredPosts.length !== 1 ? "s" : ""}
          </div>
        </div>

        {/* Content Section */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((n) => (
              <div
                key={n}
                className="h-72 rounded-2xl border border-white/5 bg-white/[0.01] animate-pulse p-6"
              >
                <div className="h-4 w-1/3 bg-white/10 rounded mb-4" />
                <div className="h-6 w-3/4 bg-white/10 rounded mb-3" />
                <div className="h-4 w-full bg-white/10 rounded mb-2" />
                <div className="h-4 w-full bg-white/10 rounded mb-6" />
                <div className="h-4 w-1/4 bg-white/10 rounded mt-auto" />
              </div>
            ))}
          </div>
        ) : filteredPosts.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredPosts.map((post) => (
              <div key={post.id}>
                <BlogCard post={post} />
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-20 border border-dashed border-white/10 rounded-2xl bg-white/[0.01]">
            <TrendingUp className="h-10 w-10 text-slate-400 mx-auto mb-4" />
            <h3 className="text-lg font-bold mb-1">No market reports found</h3>
            <p className="text-slate-400 text-sm">
              Check back later or try adjusting your search terms.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
