import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    // Documentos de credencialización del médico (PDF/fotos) pueden pesar más
    // del 1MB por defecto de los Server Actions.
    serverActions: { bodySizeLimit: "10mb" },
  },
  async redirects() {
    return [
      { source: "/terminos", destination: "/terminos-y-condiciones", permanent: true },
      { source: "/privacidad", destination: "/aviso-de-privacidad", permanent: true },
      { source: "/patient/recetas", destination: "/patient/protocolos", permanent: true },
    ];
  },
};

export default nextConfig;
