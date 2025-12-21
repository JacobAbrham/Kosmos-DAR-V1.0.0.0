/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'standalone',
    rewrites: async () => {
        return [
            {
                source: '/api/:path*',
                destination: 'http://localhost:8000/:path*',
            },
        ]
    },
};

export default nextConfig;
