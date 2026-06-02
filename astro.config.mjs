import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  site: 'https://mikenac.github.io',
  base: '/pgh_tap_list',
  output: 'static',
  integrations: [tailwind()],
});
