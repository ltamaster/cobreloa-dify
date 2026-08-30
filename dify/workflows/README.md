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
2. Entra a Dify: http://localhost (vía nginx) y crea tu cuenta admin.
3. Ve a **Studio → Create app → Import DSL** y sube el `.yml` que quieras.
4. En **Settings → Model Provider** carga tu `OPENAI_API_KEY`
   (también puedes definirla en `.env`).
5. Abre el app y prueba en **Preview**.

> El modelo por defecto es `gpt-5-mini` (`langgenius/openai/openai`) con
> `temperature 0.3`, `top_p 0.7`, `max_tokens 1500` y `reasoning_effort low`,
> según `docs/AGENT-DESIGN.md`.

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
| `SUPPORT_EMAIL` | string | Contacto de soporte |

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

## Cómo probar y depurar el Chatflow

Para depurar el grafo mientras lo editas:

- **Preview** (panel derecho del editor en Studio): corre el flujo completo y
  muestra el input/output de cada nodo — el mejor loop para iterar sobre la
  lógica del clasificador y las ramas.
- **"Run this step"** (clic derecho sobre un nodo): prueba un nodo aislado
  (por ejemplo el HTTP a membrezia.com) sin gastar tokens de LLM en el resto
  del grafo.
- **Logs** de la app (fuera del editor): histórico de conversaciones con
  trace completo por nodo, útil para depurar después del hecho.

Para regresión automatizada contra una app ya publicada, usa el harness en
`dify/workflows/tests/`:

```bash
export DIFY_API_KEY="app-..."                    # API key de la app publicada, nunca la commitees
export DIFY_BASE_URL="https://tu-instancia/v1"   # o http://localhost/v1 para el stack local
python3 dify/workflows/tests/test_chatflow.py            # corre todos los casos
python3 dify/workflows/tests/test_chatflow.py --case escalation --verbose
```

Los casos viven en `dify/workflows/tests/cases.json` (uno por intención, más
casos de prompt-injection y de límites) — agrega ahí nuevos casos sin tocar
el script. Cada caso puede declarar `expect_contains` / `expect_not_contains`;
si alguna expectativa no se cumple el script termina con exit code 1, así que
también sirve como gate en un pipeline de CI, no solo para inspección manual.

## Integraciones externas (membrezia, SendGrid, Mercado Pago, Slack)

La verificación por RUT y los pagos requieren llamadas HTTP a servicios externos.
El asistente base guía esos flujos de forma conversacional; para automatizarlos
end-to-end conviene migrar a un app en modo **Workflow/Agent** y añadir nodos
HTTP con las credenciales reales. Ver `docs/AGENT-DESIGN.md`.
