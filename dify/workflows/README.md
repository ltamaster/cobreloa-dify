# Workflows de Dify — Cobreloa

Esta carpeta contiene los archivos **DSL** (`.yml`) que se importan directamente
en Dify. Cada archivo es una app/agente completo listo para cargar con un clic.

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `cobreloa-assistant.yml` | Asistente conversacional de membresía (chat). Cubre las 7 intenciones: estado de socio, hacerse socio, pago de cuota, escuelas de fútbol, información general y escalado a soporte, con reglas de seguridad anti prompt-injection. |

## Cómo importarlo

1. Levanta el stack: `docker-compose up -d`
2. Entra a Dify: http://localhost:3000 y crea tu cuenta admin.
3. Ve a **Studio → Create app → Import DSL** y sube `cobreloa-assistant.yml`.
4. En **Settings → Model Provider** carga tu `ANTHROPIC_API_KEY`
   (también puedes definirla en `.env`).
5. Abre el app y prueba en **Preview**.

> El modelo por defecto es `claude-3-5-sonnet-20241022` con `temperature 0.3`,
> `top_p 0.7` y `max_tokens 500`, según `docs/AGENT-DESIGN.md`.

## Knowledge Base (opcional)

El DSL deja la base de conocimiento vacía. Para respuestas con datos de planes,
escuelas y FAQs, crea un Knowledge Base en Dify, sube los documentos y luego
enlázalo al app en la sección **Context**.

## Integraciones externas (membrezia, SendGrid, Mercado Pago, Slack)

La verificación por RUT y los pagos requieren llamadas HTTP a servicios externos.
El asistente base guía esos flujos de forma conversacional; para automatizarlos
end-to-end conviene migrar a un app en modo **Workflow/Agent** y añadir nodos
HTTP con las credenciales reales. Ver `docs/AGENT-DESIGN.md`.
