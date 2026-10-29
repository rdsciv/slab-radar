import type { NextConfig } from 'next';

// Static export for GitHub Pages; BASE_PATH=/slab-radar in CI.
const config: NextConfig = {
  output: 'export',
  basePath: process.env.BASE_PATH || '',
  images: { unoptimized: true },
  trailingSlash: true,
  turbopack: { root: process.cwd() },
};

export default config;
