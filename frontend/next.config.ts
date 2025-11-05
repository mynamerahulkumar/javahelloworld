import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Production optimizations
  output: "standalone", // Enable standalone output for Docker/production deployments
  compress: true, // Enable compression
  poweredByHeader: false, // Remove X-Powered-By header for security
  reactStrictMode: true,
  
  // Environment-based configuration
  ...(process.env.NODE_ENV === "production" && {
    // Production-only optimizations
    swcMinify: true,
    productionBrowserSourceMaps: false,
  }),
};

export default nextConfig;
