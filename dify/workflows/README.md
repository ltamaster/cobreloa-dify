# Workflows de Dify — Cobreloa

Esta carpeta contiene los archivos **DSL** (`.yml`) que se importan directamente
en Dify. Cada archivo es una app/agente completo listo para cargar con un clic.

## Archivos

| Archivo | Modo | Descripción |
|---------|------|-------------|
| `cobreloa-assistant.yml` | `chat` | Asistente conversacional simple. Cubre las 7 intenciones con un system prompt en español y reglas anti prompt-injection. Import garantizado, sin variables ni nodos. Úsalo como base rápida o fallback. |
| `cobreloa-assistant-chatflow.yml` | `advanced-chat` (Chatflow) | Versión con **grafo de nodos**: clasificador de intención → ramas por flujo, con **Environment Variables** (URLs/tokens) y **Conversation Variables** (estado de sesión). Incluye un nodo HTTP de ejemplo a membrezia.com. |

## Cómo importarlo

1. Levanta el stack: `docker-compose up -d`
2. Entra a Dify: http://localhost:3000 y crea tu cuenta admin.
3. Ve a **Studio → Create app → Import DSL** y sube el `.yml` que quieras.
4. En **Settings → Model Provider** carga tu `ANTHROPIC_API_KEY`
   (también puedes definirla en `.env`).
5. Abre el app y prueba en **Preview**.

> El modelo por defecto es `claude-3-5-sonnet-20241022` con `temperature 0.3`,
> `top_p 0.7` y `max_tokens 500`, según `docs/AGENT-DESIGN.md`.

## Variables del Chatflow (URLs y tokens)

En el Chatflow, las URLs y tokens **no están hardcodeados**: viven como
**Environment Variables** dentro del app y se referencian con `{{#env.NOMBRE#}}`
en los nodos (HTTP, LLM). Los tokens son de tipo `Secret` y se importan vacíos:
pégalos tras importar en **el panel de variables de entorno** del Chatflow.

| Variable | Tipo | Uso |
|----------|------|-----|
| `MEMBREZIA_API_URL` | string | Base URL de la API de socios |
| `MEMBREZIA_API_TOKEN` | secret | Bearer token de membrezia.com |
| `SENDGRID_API_KEY` | secret | Envío de emails |
| `MERCADOPAGO_ACCESS_TOKEN` | secret | Links de pago |
| `SLACK_WEBHOOK_URL` | secret | Notificaciones de escalado |
| `SOCIOS_PORTAL_URL` | string | Portal público de socios |
| `SUPPORT_EMAIL` | string | Contacto de soporte |
| `SCHOOLS_EMAIL` | string | Contacto de escuelas |

**Conversation Variables** (estado que persiste durante el chat, `{{#conversation.NOMBRE#}}`):
`user_rut`, `user_email`, `user_name`, `verified`, `member_id`, `current_plan`, `intent`.

> ⚠️ Estas variables se definen **dentro del app de Dify**, no se leen del `.env`
> del contenedor. El `.env`/`docker-compose` solo alimenta a la plataforma Dify
> (base de datos, SMTP, `ANTHROPIC_API_KEY`).

> Tras importar, verifica el grafo en el editor. El nodo HTTP a membrezia.com es
> un ejemplo funcional; los flujos de SendGrid, Mercado Pago y Slack se agregan
> como nodos HTTP adicionales usando sus respectivas variables de entorno.

## Knowledge Base (opcional)

El DSL deja la base de conocimiento vacía. Para respuestas con datos de planes,
escuelas y FAQs, crea un Knowledge Base en Dify, sube los documentos y luego
enlázalo al app en la sección **Context**.

## Integraciones externas (membrezia, SendGrid, Mercado Pago, Slack)

La verificación por RUT y los pagos requieren llamadas HTTP a servicios externos.
El asistente base guía esos flujos de forma conversacional; para automatizarlos
end-to-end conviene migrar a un app en modo **Workflow/Agent** y añadir nodos
HTTP con las credenciales reales. Ver `docs/AGENT-DESIGN.md`.
