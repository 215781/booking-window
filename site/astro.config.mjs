import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://whentobook.co.uk',
  trailingSlash: 'always',
  integrations: [sitemap()],
  // Old URLs from the current site -> new pages (static meta-refresh + canonical)
  redirects: {
    '/clubmed': '/club-med/',
    '/summer': '/club-med/',
    '/markwarner': '/',
  },
});
