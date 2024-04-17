import dotenv from 'dotenv'
import findConfig from 'find-config'

/** @type {import('next').NextConfig} */
const nextConfig = {
  redirects: async () => [
    { source: '/', destination: '/sounds', permanent: true },
  ],
  images: {
    unoptimized: true, // Only because of bun
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'cdn.discordapp.com',
      },
    ],
  },
}

dotenv.config({ path: findConfig('.env') })
export default nextConfig
