import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://whentobook.co.uk',
  trailingSlash: 'always',
  integrations: [sitemap({ filter: (page) => !page.includes('/confirmed/') })],
  // Old URLs from the current site -> new pages (static meta-refresh + canonical)
  redirects: {
    '/clubmed': '/club-med/',
    '/summer': '/club-med/#sun',
    '/markwarner': '/mark-warner/',
  },
});
