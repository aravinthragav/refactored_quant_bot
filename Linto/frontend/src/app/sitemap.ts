import { MetadataRoute } from 'next';

export const dynamic = 'force-dynamic';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = 'https://aigoldforecast.com';
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.aigoldforecast.com';

  const sitemaps: MetadataRoute.Sitemap = [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'always',
      priority: 1.0,
    },
    {
      url: `${baseUrl}/strategies`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.8,
    },
    {
      url: `${baseUrl}/blog`,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 0.8,
    },
  ];

  try {
    // Dynamic fetch from backend blog API
    const res = await fetch(`${apiUrl}/api/blog`, { cache: 'no-store' });
    const data = await res.json();
    if (data.success && data.posts) {
      data.posts.forEach((post: any) => {
        sitemaps.push({
          url: `${baseUrl}/blog/${post.slug}`,
          lastModified: new Date(post.created_at),
          changeFrequency: 'weekly',
          priority: 0.6,
        });
      });
    }
  } catch (err) {
    console.error('Failed to append blog posts to sitemap:', err);
  }

  return sitemaps;
}
