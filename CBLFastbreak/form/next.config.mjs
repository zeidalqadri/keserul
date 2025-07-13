/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  experimental: {
    serverActions: {
      allowedOrigins: ['localhost:3000', '*.pages.dev', '*.cloudflare.com'],
    },
  },
  images: {
    domains: ['blob.vercel-storage.com'],
    unoptimized: true,
  },
}

export default nextConfig
