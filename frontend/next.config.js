/** @type {import('next').NextConfig} */
const nextConfig = {
  trailingSlash: false,
  experimental: {
    serverComponentsExternalPackages: ['better-auth'],
  },

  // Standalone output for optimized Docker images
  output: 'standalone',

  images: {
    domains: ['localhost', 'lh3.googleusercontent.com'],
  },

  // Optimize for production
  compress: true,
  poweredByHeader: false,

  // Production-ready settings
  productionBrowserSourceMaps: false,

  // Add headers for better auth compatibility in containerized environments
  async headers() {
    return [
      {
        source: '/api/auth/(.*)',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,POST,PUT,DELETE,OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type, Authorization' },
          { key: 'Access-Control-Allow-Credentials', value: 'true' },
        ],
      },
    ];
  },
}

module.exports = nextConfig;

