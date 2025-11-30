/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  // Transpile packages that need to be compiled
  transpilePackages: ['lucide-react'],
  // Turbopack configuration (Next.js 16+ default)
  turbopack: {
    // Turbopack handles module resolution automatically
    // The webpack config is no longer needed with Turbopack
  },
  // Keep webpack config for fallback if needed (when using --webpack flag)
  webpack: (config, { isServer }) => {
    // Fix for module resolution issues
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
    };

    // Improve module resolution for nested packages
    config.resolve.symlinks = false;

    return config;
  },
}

export default nextConfig
