import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

// Existing Jekyll posts are reused as-is from ../_posts (same /blog/<slug>/ URLs as the live site).
const blog = defineCollection({
  loader: glob({ pattern: '*.md', base: '../_posts' }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    last_modified_at: z.coerce.date().optional(),
    description: z.string().optional(),
    permalink: z.string().optional(),
  }).passthrough(),
});
export const collections = { blog };
