import type { NextConfig } from "next";

// En producción el sitio vive bajo /coco-vet-engine/ (nombre del repo GitHub)
// En desarrollo local no hay basePath
const isProd = process.env.NODE_ENV === "production";
const repoName = "coco-vet-engine"; // ← cambia esto si tu repo tiene otro nombre

const nextConfig: NextConfig = {
  // Genera HTML/CSS/JS estático en la carpeta "out/" para GitHub Pages
  output: "export",

  // Prefijo de ruta necesario cuando GitHub Pages sirve desde /repo-name/
  basePath: isProd ? `/${repoName}` : "",
  assetPrefix: isProd ? `/${repoName}/` : "",

  // Esencial para GitHub Pages: genera carpetas con index.html (ej. /analyze/index.html)
  // para que las rutas directas funcionen sin devolver 404.
  trailingSlash: true,

  // GitHub Pages no puede optimizar imágenes en el servidor
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
