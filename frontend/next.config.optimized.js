/** @type {import('next').NextConfig} */
const nextConfig = {
  // Optimize for production
  output: 'standalone', // Creates a minimal production build
  compress: true,
  poweredByHeader: false,
  
  // Reduce bundle size
  swcMinify: true,
  
  // Optimize images
  images: {
    formats: ['image/avif', 'image/webp'],
    minimumCacheTTL: 60,
  },
  
  // Reduce build output
  generateBuildId: async () => {
    return process.env.BUILD_ID || 'production'
  },
  
  // Exclude unnecessary files from build
  webpack: (config, { isServer }) => {
    // Reduce bundle size
    if (!isServer) {
      config.optimization = {
        ...config.optimization,
        usedExports: true,
        sideEffects: false,
      }
    }
    
    return config
  },
  
  // Experimental optimizations
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['lucide-react', '@radix-ui/react-dialog'],
  },
}

module.exports = nextConfig



