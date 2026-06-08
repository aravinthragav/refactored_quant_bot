"use client";

import Link from "next/link";
import { Calendar, User, ArrowRight } from "lucide-react";

interface BlogPost {
  id: number;
  created_at: string;
  title: string;
  slug: string;
  summary: string;
  author: string;
}

export default function BlogCard({ post }: { post: BlogPost }) {
  const formattedDate = new Date(post.created_at).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <div className="group relative overflow-hidden rounded-2xl border border-white/10 bg-white/[0.03] p-6 backdrop-blur-md transition-all duration-350 hover:border-amber-500/35 hover:bg-white/[0.05] hover:shadow-[0_0_30px_-5px_rgba(245,158,11,0.15)] flex flex-col justify-between h-full">
      {/* Decorative gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-amber-500/0 via-amber-500/0 to-amber-500/[0.02] opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
      
      <div>
        {/* Meta Info */}
        <div className="flex items-center gap-4 text-xs text-slate-400 mb-4">
          <span className="flex items-center gap-1.5">
            <Calendar className="h-3.5 w-3.5 text-amber-500" />
            {formattedDate}
          </span>
          <span className="flex items-center gap-1.5">
            <User className="h-3.5 w-3.5 text-amber-500" />
            {post.author}
          </span>
        </div>

        {/* Title */}
        <h3 className="text-xl font-bold text-white group-hover:text-amber-400 transition-colors duration-300 mb-3 leading-snug line-clamp-2">
          {post.title}
        </h3>

        {/* Summary */}
        <p className="text-slate-300 text-sm leading-relaxed mb-6 line-clamp-3">
          {post.summary}
        </p>
      </div>

      {/* Action Link */}
      <Link
        href={`/blog/${post.slug}`}
        className="inline-flex items-center gap-2 text-sm font-semibold text-amber-400 hover:text-amber-300 transition-colors group/link self-start mt-auto"
      >
        Read Full Report
        <ArrowRight className="h-4 w-4 transition-transform duration-300 group-hover/link:translate-x-1" />
      </Link>
    </div>
  );
}
