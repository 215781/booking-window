import { getCollection } from 'astro:content';
export function slugOf(p: { id: string; data: { permalink?: string } }) {
  const m = p.data.permalink?.match(/\/blog\/(?:\d{4}\/\d{2}\/\d{2}\/)?([^/]+)\/?$/);
  return m ? m[1] : p.id.replace(/^\d{4}-\d{2}-\d{2}-/, '');
}
export async function posts() {
  const all = await getCollection('blog');
  // Keep the newest file when two posts share a slug (e.g. Peisey-Vallandry was published twice)
  const bySlug = new Map<string, (typeof all)[number]>();
  for (const p of all.sort((a, b) => +a.data.date - +b.data.date)) bySlug.set(slugOf(p), p);
  return [...bySlug.values()].sort((a, b) => +b.data.date - +a.data.date);
}
