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
    <div className="group relative overflow-hidden rounded-xl glass-card p-6 transition-all duration-400 hover:border-primary/40 hover:shadow-[0_0_30px_-5px_rgba(212,175,55,0.15)] flex flex-col justify-between h-full">
      {/* Decorative gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/0 via-primary/0 to-primary/[0.03] opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
      
      <div>
        {/* Meta Info */}
        <div className="flex items-center gap-4 text-xs text-on-surface-variant mb-4">
          <span className="flex items-center gap-1.5">
            <Calendar className="h-3.5 w-3.5 text-primary" />
            {formattedDate}
          </span>
          <span className="flex items-center gap-1.5">
            <User className="h-3.5 w-3.5 text-primary" />
            {post.author}
          </span>
        </div>

        {/* Title */}
        <h3 className="text-xl font-bold font-playfair text-on-surface group-hover:text-primary transition-colors duration-300 mb-3 leading-snug line-clamp-2">
          {post.title}
        </h3>

        {/* Summary */}
        <p className="text-on-surface-variant text-sm leading-relaxed mb-6 line-clamp-3">
          {post.summary}
        </p>
      </div>

      {/* Action Link */}
      <Link
        href={`/blog/${post.slug}`}
        className="inline-flex items-center gap-2 text-sm font-semibold text-primary hover:text-gold-light transition-colors group/link self-start mt-auto"
      >
        Read Full Report
        <ArrowRight className="h-4 w-4 transition-transform duration-300 group-hover/link:translate-x-1" />
      </Link>
    </div>
  );
}
