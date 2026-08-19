# Knowledge Base — Cobreloa

Contenido fuente de los documentos que alimentan el dataset **"Cobreloa -
Base de Conocimiento"** en Dify (usado por los nodos *Knowledge Retrieval*
del chatflow, ver `dify/workflows/cobreloa-assistant-chatflow.yml`).

No hay un script que los suba automáticamente — a diferencia de
`dify/workflows/*.yml`, que sí se importan como DSL. Para poblar (o
repoblar, ej. en una instancia nueva) el dataset:

1. Dify Studio → **Knowledge** → crear/abrir el dataset
   "Cobreloa - Base de Conocimiento".
2. Subir estos 5 archivos `.md` tal cual.

## Archivos

- `planes.md` — planes de socio y precios
- `formas_pago.md` — métodos de pago
- `horarios.md` — sede, horario de atención, contacto
- `escuelas.md` — escuelas de fútbol (categorías, valores, inscripción)
- `faqs.md` — preguntas frecuentes

Varios documentos tienen una nota `> **Nota para quien mantiene este
documento**` marcando información deliberadamente incompleta (datos
bancarios, beneficios detallados por plan) — no completar con datos
sensibles en texto plano; ver el comentario en cada archivo.
