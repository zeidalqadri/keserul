/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  distDir: 'out',
  trailingSlash: true,
  skipTrailingSlashRedirect: true,
  assetPrefix: '',
  basePath: '',
  generateBuildId: () => 'build',
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    domains: ['blob.v0.dev'],
    unoptimized: true,
  },
  env: {
    RASTERVECTOR_API_URL: process.env.RASTERVECTOR_API_URL || 'https://rastervector-api.zeidalqadri.workers.dev'
  }
}

export default nextConfig
