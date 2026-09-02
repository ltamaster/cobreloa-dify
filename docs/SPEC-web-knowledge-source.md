# Spec: cobreloa.cl como fuente de la Knowledge Base

**Estado**: pendiente de implementar — falta que alguien cree la cuenta del
proveedor de crawling y pegue la API key en Dify Studio.

## Objetivo

Que el asistente pueda responder con contenido del sitio oficial
**https://cobreloa.cl**, sin tener que transcribirlo a mano a un `.md` en
`dify/knowledge/` (como se hizo con `hacerse_socio.md`, `escuelas.md`, etc.
a partir de las páginas de Membrezía).

## Decisión

- **Fuente**: `https://cobreloa.cl` (sitio oficial, no las páginas de
  Membrezía — esas siguen documentándose a mano porque son formularios,
  no contenido navegable).
- **Modo**: snapshot importado a la Knowledge Base (no consulta en vivo).
  Igual que los `.md` existentes: hay que re-importar manualmente cuando
  el sitio cambie, no hay sincronización automática.
- **Dónde vive**: como documento nuevo dentro del dataset ya existente
  **"Cobreloa - Base de Conocimiento"** — el mismo que usan los nodos
  *Knowledge Retrieval* del chatflow (`dify/workflows/cobreloa-assistant-chatflow.yml`).
  No requiere cambios en el DSL del Chatflow.

## Cómo implementarlo

1. Crear una cuenta y sacar una API key en uno de los proveedores de
   crawling que soporta esta versión de Dify (confirmado revisando
   `core/rag/extractor/` en el contenedor `dify-api`):
   - **Jina Reader** (https://jina.ai/reader) — recomendado para partir,
     tiene tier gratuito.
   - Firecrawl — alternativa.
   - Watercrawl — alternativa.

   Esto es una cuenta de terceros — lo tiene que hacer una persona, no un
   agente.

2. En Dify Studio → **Knowledge** → abrir el dataset
   "Cobreloa - Base de Conocimiento".
3. **Add file** / **Añadir documento** → fuente **"Website"**.
4. Configurar el proveedor elegido con la API key del paso 1 (solo la
   primera vez).
5. Ingresar `https://cobreloa.cl` y definir el alcance del crawl
   (profundidad, páginas máximas) — a decidir cuánto del sitio conviene
   traer.
6. Correr el import. Queda disponible automáticamente para todos los
   nodos de Knowledge Retrieval del chatflow.

## Mantenimiento

Como es snapshot, si el sitio cambia hay que volver a correr el import
manualmente. No hay recordatorio automático — agregarlo a la rutina de
mantenimiento de la Knowledge Base junto con la revisión de los `.md`.

## Abierto / por decidir

- Qué páginas específicas de cobreloa.cl conviene traer (¿todo el sitio?
  ¿solo secciones institucionales/noticias?) y con qué profundidad de
  crawl.
- Qué proveedor usar en definitiva (Jina Reader vs Firecrawl vs
  Watercrawl) — depende de cuál cuenta termine creando el club.
