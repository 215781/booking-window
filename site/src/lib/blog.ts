import { getCollection } from 'astro:content';
export function slugOf(p: { id: string; data: { permalink?: string } }) {
  const m = p.data.permalink?.match(/\/blog\/(?:\d{4}\/\d{2}\/\d{2}\/)?([^/]+)\/?$/);
  return m ? m[1] : p.id.replace(/^\d{4}-\d{2}-\d{2}-/, '');
}
// Posts dated in the future are scheduled: they stay out of the build until their date.
// The site rebuilds twice a day (deploy_site.yml), so a post goes live on the first build on/after its date.
// For a local preview of scheduled posts: WTB_NOW=2026-12-31 npx astro build
export function isPublished(p: { data: { date: Date; draft?: boolean } }, now = new Date(process.env.WTB_NOW ?? Date.now())) {
  return !p.data.draft && +p.data.date <= +now;
}
export async function posts() {
  const all = (await getCollection('blog')).filter((p) => isPublished(p));
  // Keep the newest file when two posts share a slug (e.g. Peisey-Vallandry was published twice)
  const bySlug = new Map<string, (typeof all)[number]>();
  for (const p of all.sort((a, b) => +a.data.date - +b.data.date)) bySlug.set(slugOf(p), p);
  return [...bySlug.values()].sort((a, b) => +b.data.date - +a.data.date);
}
