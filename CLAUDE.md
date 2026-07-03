# CLAUDE.md

Guía para agentes que trabajan en este repositorio (**cobreloa-dify**).

## Qué es este proyecto

Stack self-hosted de **Dify** (Docker Compose) para el asistente de membresía de
Cobreloa. Incluye la infraestructura (`docker-compose*.yml`, `nginx/`), los DSL
importables del asistente (`dify/workflows/`), el script de setup
(`dify/init-workflows.py`) y la documentación (`docs/`, `README.md`).

## Flujo de trabajo: SIEMPRE vía Pull Request

A partir de ahora **todos los cambios se entregan mediante un Pull Request**. No
se commitea ni se hace push directo a `main`.

1. **Rama**: crea o usa una rama de trabajo descriptiva (nunca `main`).
   ```
   git checkout -b <tipo>/<descripcion-corta>   # feat/, fix/, docs/, chore/
   ```
2. **Commits**: mensajes claros y en presente ("Add…", "Fix…"). Agrupa cambios
   coherentes; evita commits gigantes sin relación.
3. **Revisión previa (obligatoria)**: antes de abrir o actualizar un PR, invoca
   al subagente **`pr-reviewer`** (ver abajo) para una revisión tipo _pair
   review_ del diff. Aborda o responde cada hallazgo antes de continuar.
4. **Push**: `git push -u origin <rama>`.
5. **PR**: abre el Pull Request contra `main` con título y descripción claros
   (qué cambia, por qué, cómo probarlo). Si existe plantilla en
   `.github/`, respétala.
6. **No** hagas merge sin aprobación explícita del usuario.

> Excepción: si el usuario pide de forma explícita un cambio directo (por ej.
> un hotfix), confírmalo antes de saltarte el flujo de PR.

## Pair review con el subagente `pr-reviewer`

El repo define un subagente en `.claude/agents/pr-reviewer.md` que actúa como
**revisor par**. Úsalo para revisar el diff antes de cada PR (o cuando el
usuario lo pida). Reporta correctitud, seguridad, claridad, tests y consistencia
con el resto del repo, sin modificar archivos: solo entrega hallazgos.

Invócalo con la herramienta `Agent` usando `subagent_type: "pr-reviewer"` y
pásale el rango del diff a revisar (por defecto `main..HEAD`).

## Convenciones del repo

- **Idioma**: documentación y textos de cara al usuario en **español**.
- **Secretos**: nunca hardcodear URLs de negocio, tokens ni credenciales.
  - En la plataforma Dify → variables de `.env` / `docker-compose`.
  - Dentro de un Chatflow → **Environment Variables** de Dify (`{{#env.*#}}`),
    los tokens como tipo `Secret`. Ver `dify/workflows/README.md`.
- **DSL de Dify**: los `.yml` de `dify/workflows/` deben parsear como YAML válido
  antes de commitear. Verifica con:
  `python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" <archivo>`
- **Modelo por defecto del asistente**: `claude-3-5-sonnet-20241022`
  (`temperature 0.3`, `top_p 0.7`, `max_tokens 500`), según `docs/AGENT-DESIGN.md`.
