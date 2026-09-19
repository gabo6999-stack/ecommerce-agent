# Hero con shader — integración

## Estado del proyecto (verificado, no supuesto)

El prompt de 21st.dev asume un proyecto React con shadcn, Tailwind y TypeScript.
Este repositorio **no lo es**:

| Requisito | Aquí |
|---|---|
| `components.json` (shadcn) | no existe |
| `tailwind.config.*` | no existe |
| `tsconfig.json` | no existe |
| `package.json` | no existe |
| Carpeta `/components/ui` | no existe |

Es una app Flask en Python más un prototipo HTML de una sola página. Copiar el
`.tsx` a `/components/ui` no habría hecho nada: no hay nada que lo compile.

## Lo que se hizo en su lugar

El shader **no necesita React**. Es un `<canvas>` con WebGL y un fragment shader;
el componente de React solo aporta el ciclo de vida (montar, observar, limpiar).
Se portó a JS plano dentro de `rediseno/index.html`:

- **El GLSL es idéntico**, incluido el empaquetado en 7 `vec4` que mantiene el
  shader por debajo del mínimo garantizado de uniforms de WebGL1.
- **Recoloreado a la paleta de PYS**: el preset venía en cian y violeta. Ahora va
  de fondo de marca a aqua `#02F6C8` a magenta `#FF047E`.
- **`prefers-reduced-motion`**: el original no lo contempla. Aquí, con esa
  preferencia activa, se pinta **un solo fotograma** y no se anima.
- DPR limitado a 1.5 y techo de 1.4 Mpx (el original usa 2 y 2 Mpx).
- Pausa fuera de pantalla y con la pestaña oculta, igual que el original.
- Si WebGL no está disponible o el programa no enlaza, el canvas se oculta y el
  hero queda con su fondo normal.

## Si algún día se monta el front en Next.js

Ahí sí aplica el prompt tal cual:

```bash
npx create-next-app@latest pys-front --typescript --tailwind --app
cd pys-front
npx shadcn@latest init
```

`shadcn init` crea `components.json` y fija los alias. El componente va en
`components/ui/hero-fusion-web.tsx`, y **la carpeta importa**: `components.json`
resuelve `@/components/ui` a esa ruta, así que los componentes que instale el CLI
y los que pegues a mano tienen que convivir ahí o los imports `@/components/ui/…`
no resuelven.

## Advertencia de rendimiento, que sigue en pie

Un shader a pantalla completa consume GPU de forma continua. Por eso aquí:

- vive **solo en el hero**, no de fondo de toda la página;
- se detiene al salir de pantalla;
- respeta `prefers-reduced-motion`.

En un ecommerce conviene medirlo en un Android de gama media antes de darlo por
bueno: el INP y el consumo de batería no salen en el Lighthouse de escritorio.

Shader original: Shader Builder de 21st.dev sobre Paper Shaders (Apache-2.0),
https://shaders.paper.design/neuro-noise
