import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  site: 'https://example.pages.dev',
  output: 'static',
  integrations: [tailwind()],
});
