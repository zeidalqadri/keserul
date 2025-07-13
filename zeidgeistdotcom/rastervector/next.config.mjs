/** @type {import('next').NextConfig} */
const nextConfig = {
  trailingSlash: true,
  skipTrailingSlashRedirect: true,
  assetPrefix: '',
  basePath: '',
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
