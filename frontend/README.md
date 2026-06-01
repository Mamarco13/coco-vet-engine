# COCO Frontend

Frontend para la plataforma de deteccion de enfermedades caninas. Esta version incluye landing, flujo de analisis de imagenes y pantalla de resultados con un mock local mientras no exista API HTTP.

## Stack

- Next.js (App Router)
- React + TypeScript
- Tailwind CSS
- Framer Motion

## Requisitos

- Node.js 18+
- npm

## Instalacion

```bash
npm install
```

## Desarrollo

```bash
npm run dev
```

Abrir http://localhost:3000

## Produccion

```bash
npm run build
npm start
```

## Variables de entorno

No hay variables obligatorias por ahora. Cuando exista API HTTP, se recomienda:

```
NEXT_PUBLIC_API_BASE=https://tu-api
```

## Estructura relevante

- src/app/page.tsx -> Landing
- src/app/analyze/page.tsx -> Analisis
- src/app/results/page.tsx -> Resultados
- src/components/ui -> Componentes reutilizables
- src/lib -> Configuracion y mocks

## Notas

- Todas las imagenes provienen de /public.
- El mock de analisis se encuentra en src/lib/api.ts (reemplazar cuando haya backend).
