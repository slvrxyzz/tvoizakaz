import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Отключаем ESLint на этапе прод-сборки, чтобы деплой не падал из-за предупреждений/any
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
