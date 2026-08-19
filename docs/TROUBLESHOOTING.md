# Troubleshooting

## Services no inician

```bash
docker-compose logs dify-api
docker-compose restart dify-api
```

## Memory usage alto

```bash
docker stats
```

Aumentar RAM en Docker Desktop Settings.

## Network error

```bash
docker-compose down
docker-compose up -d
```

## Database bloqueada

```bash
docker-compose down -v
docker-compose up -d
```

## dify-web: "TypeError: fetch failed ... ECONNREFUSED 127.0.0.1:5001" (o el navegador se queda colgado en /install)

`dify-web` corre su propio proceso Next.js dentro del contenedor, y ese
mismo proceso sirve dos roles distintos con la misma variable de entorno,
lo cual es la fuente de confusión de este bug:

1. **SSR** (código que corre dentro del contenedor `dify-web`, en su
   propia red Docker).
2. **Bundle del navegador** (código que corre en la máquina del usuario,
   sin ninguna visibilidad de la red Docker).

Si `CONSOLE_API_URL`/`APP_API_URL` no están seteadas, la imagen cae a su
default interno `http://127.0.0.1:5001` — el SSR intenta conectarse al
loopback del propio contenedor `dify-web` (no al de `dify-api`) y falla
con `ECONNREFUSED`. Si en cambio se apuntan al hostname interno de Docker
(`http://dify-api:5001`, lo que este repo probó primero), el SSR queda
arreglado pero el **navegador** hereda ese mismo valor (son variables
`NEXT_PUBLIC_*`, se hornean también en el bundle del cliente) y se queda
colgado en `/install` con un error de red en la consola:
`NetworkError: ... GET http://dify-api:5001/console/api/setup` — el
navegador no puede resolver el hostname interno de Docker.

La solución real usa dos variables distintas (confirmado leyendo el
bundle minificado de `dify-web`, buscando "SERVER_" en
`.next/server/chunks/[root-of-the-server]__*.js`):

- `CONSOLE_API_URL` / `APP_API_URL` en blanco -> el navegador usa rutas
  relativas (`/console/api`, `/api`) resueltas contra el origin que sirvió
  la página (por eso siempre hay que entrar por `http://localhost`, puerto
  80 vía nginx, y nunca por `http://localhost:3000` directo — el puerto
  3000 de `dify-web` a propósito no está publicado al host en
  `docker-compose.yml`, para que este error de cliente confunda menos:
  entrar directo a `:3000` da "connection refused" de una, en vez de una
  página que carga pero falla silenciosamente al llamar a la API).
- `SERVER_CONSOLE_API_URL: http://dify-api:5001` — variable **server-only**
  que el SSR lee con prioridad sobre `CONSOLE_API_URL` (no existe un
  `SERVER_APP_API_URL` equivalente en esta versión de la imagen).

## El link de "Launch"/Public URL de una app (Studio -> Web App) apunta a `http://127.0.0.1:3000/...`

`APP_WEB_URL` (en `dify-api`) es la variable que arma ese link — **distinta**
de `CONSOLE_WEB_URL`, que ya está bien seteada arriba y no cubre este caso.
Sin `APP_WEB_URL` seteada, cae al default de la imagen
(`http://127.0.0.1:3000`), justo el puerto que a propósito no está
publicado al host (ver la entrada de arriba). Fix: `docker-compose.yml`,
servicio `dify-api` — `APP_WEB_URL: ${APP_WEB_URL:-http://localhost}`.

No existe un `SERVER_APP_API_URL`, pero el código que consume
`APP_API_URL`/`NEXT_PUBLIC_PUBLIC_API_PREFIX` no tiene el mismo guard de
"not configured" que `CONSOLE_API_URL` sí tiene — solo cae a rutas
relativas sin tirar error. Verificado en vivo creando una app de prueba y
visitando su link público (`/chatbot/<code>`, la misma familia de rutas
`/chat/[token]`, `/agent/[token]`, `/workflow/[token]` que usaría el
embed del asistente en el sitio de Cobreloa): la página carga sin errores
de consola con `APP_API_URL` en blanco.

Ver `docker-compose.yml`, servicio `dify-web`.

## dify-api: "password authentication failed for user postgres" (o `relation "dify_setups" does not exist`)

Dos bugs distintos que dan síntomas parecidos en un stack recién clonado:

1. **Usuario equivocado**: el código de `dify-api` lee la variable `DB_USERNAME`,
   no `DB_USER` (ver `docker-compose.yml`, servicio `dify-api`). Si solo se
   setea `DB_USER`, Dify la ignora silenciosamente y cae a su default
   hardcodeado `postgres`, que no coincide con el usuario real (`dify`) —
   de ahí el `password authentication failed for user "postgres"`.
2. **Migraciones nunca corren**: el entrypoint de `dify-api` solo ejecuta
   `flask upgrade-db` si `MIGRATION_ENABLED=true`. Sin esa variable, el
   contenedor arranca contra un schema vacío y cualquier query falla con
   `relation "..." does not exist` (típicamente `dify_setups`).

Mismo patrón (variable "inventada" que Dify ignora en silencio) con el
remitente de email: la variable correcta es `MAIL_DEFAULT_SEND_FROM`, no
`SMTP_FROM_EMAIL` — con el nombre viejo, los emails salientes (invitaciones,
reset de password) quedan sin remitente configurado, sin ningún error visible.

Si ya tenías un volumen `postgres_data` de un intento previo con la
contraseña equivocada (Postgres solo aplica `POSTGRES_PASSWORD` la primera
vez que inicializa un volumen vacío — cambiarla en `.env` después no hace
nada), hay que resetearla a mano en vez de solo corregir las env vars:

```bash
docker compose exec postgres psql -U dify -d dify -h localhost \
  -c "ALTER USER dify WITH PASSWORD 'TU_PASSWORD_DE_.ENV';"
```

## dify-web / nginx aparecen "unhealthy" aunque la app funcione

Ambos healthchecks originales usaban `http://localhost/...`, pero:
- `dify-web` (Next.js) escucha en la IP propia del contenedor (su
  `$HOSTNAME`), no en `localhost`/`0.0.0.0` — por eso el healthcheck ahora
  usa `http://$HOSTNAME:3000`.
- `nginx` (Alpine) resuelve `localhost` a `::1` antes que a `127.0.0.1`, y
  solo escucha en IPv4 — por eso el healthcheck ahora apunta directo a
  `http://127.0.0.1/health`.

Si ves `unhealthy` pese a que `curl http://localhost/` desde el host
funciona, es casi seguro este mismo patrón: probá el comando del
healthcheck con `docker compose exec <servicio> <comando>` para confirmarlo
antes de asumir que la app está realmente caída.

## dify-api: "Setup account failed" / `opendal.exceptions.PermissionDenied ... privkeys/.../private.pem`

Al crear la cuenta admin desde `/install`, `dify-api` intenta escribir un
par de llaves RSA en `STORAGE_LOCAL_PATH` (`/app/data`, volumen `dify_data`)
y falla con `PermissionDenied ... Permission denied (os error 13)`.

`dify-api` corre como usuario no-root (`dify`, uid 1001) y su entrypoint
nunca hace `chown` de sus volúmenes — pero Docker crea volúmenes nombrados
nuevos como `root:root`, sin permiso de escritura para otros usuarios. El
servicio `init-permissions` en `docker-compose.yml` corrige esto en cada
`docker compose up` (chown a 1001:1001 antes de que arranque `dify-api`).
Si ya tenías los volúmenes `dify_data`/`dify_logs` de un intento previo con
los permisos rotos, alcanza con levantar el stack de nuevo — el init
corrige los volúmenes existentes también. Para hacerlo a mano:

```bash
docker run --rm -v cobreloa-dify_dify_data:/app/data alpine chown -R 1001:1001 /app/data
docker run --rm -v cobreloa-dify_dify_logs:/app/logs alpine chown -R 1001:1001 /app/logs
```

## Al loguearse aparecen 400 en `.../models/model-types/llm` (`Failed to request plugin daemon`) o en `.../datasets/retrieval-setting` (`Vector store type is not configured`)

Son dos gaps de infraestructura distintos, no bugs de configuración:

1. **Sin `plugin-daemon` no se puede configurar ningún proveedor de modelo**
   (Anthropic/Claude incluido). Dify movió los model providers a una
   arquitectura de plugins que corre en un servicio Go aparte
   (`langgenius/dify-plugin-daemon`), con su propia base de datos
   (`dify_plugin`, creada por `postgres/init/01-create-plugin-db.sql` en un
   volumen nuevo — en uno ya existente hay que crearla a mano una vez:
   `docker compose exec postgres psql -U dify -d dify -h localhost -c "CREATE DATABASE dify_plugin;"`)
   y dos secretos compartidos con `dify-api` (`PLUGIN_DAEMON_KEY` /
   `PLUGIN_DIFY_INNER_API_KEY` en `.env` — deben coincidir con
   `SERVER_KEY` / `DIFY_INNER_API_KEY` del lado de `plugin-daemon` en
   `docker-compose.yml`). Ya está resuelto en este repo (servicio
   `plugin-daemon`); si ves este error igual, revisá que las claves
   coincidan entre ambos servicios y que `plugin-daemon` esté `healthy`
   (`docker compose ps`).

   **Verificado hasta acá**: el endpoint responde `200` y `plugin-daemon`
   queda `healthy`. **No verificado**: instalar un plugin real (p. ej.
   Anthropic) desde el Marketplace ni enviar un mensaje de chat real — si
   falla la instalación, revisar conectividad saliente hacia el
   marketplace de Dify y, solo para depurar, probar con
   `PLUGIN_FORCE_VERIFYING_SIGNATURE=false`.
2. **Vector store sin configurar** — necesario para Knowledge Base/RAG.
   Ya resuelto: el servicio `postgres` usa la imagen `pgvector/pgvector`
   (drop-in de `postgres:15`, mismo formato de datos — el swap de imagen
   no afecta el volumen existente) con la extensión `vector` habilitada
   vía `postgres/init/02-enable-pgvector.sql` en un volumen nuevo, y
   `dify-api` tiene `VECTOR_STORE=pgvector` + `PGVECTOR_*` apuntando al
   mismo Postgres (reutiliza la base `dify`, no una separada). Verificado:
   `GET /console/api/datasets/retrieval-setting` responde `200` en vez
   del `400 Vector store type is not configured`.

   **En un volumen ya existente** hay dos pasos manuales (el init script
   solo corre en la primera inicialización de un volumen vacío):

   ```bash
   # 1. Habilitar la extensión en ambas bases
   docker compose exec postgres psql -U dify -d dify -h localhost -c "CREATE EXTENSION IF NOT EXISTS vector;"
   docker compose exec postgres psql -U dify -d dify_plugin -h localhost -c "CREATE EXTENSION IF NOT EXISTS vector;"

   # 2. REINDEX: postgres:15-alpine usa musl libc, pgvector/pgvector es
   # Debian (glibc). La colación "en_US.utf8" tiene un comparador distinto
   # en cada una, y este cluster no trackea versión de colación
   # (pg_database.datcollversion vacío) — Postgres no puede avisar del
   # cambio. Sin este paso, los índices de texto (ej. accounts.email)
   # quedan potencialmente desordenados para el comparador nuevo, con
   # riesgo de búsquedas/unicidad incorrectas sin ningún error visible.
   docker compose exec postgres psql -U dify -d dify -h localhost -c "REINDEX DATABASE dify;"
   docker compose exec postgres psql -U dify -d dify_plugin -h localhost -c "REINDEX DATABASE dify_plugin;"
   ```

## Editor de workflows: se queda pegado en "Syncing data, just a few seconds" y no se puede editar nada

`dify-api` corre su propio servidor Socket.IO (`ext_socketio.py`) para la
colaboración en tiempo real del editor (varios usuarios viendo/editando el
mismo workflow). Sin `CONSOLE_CORS_ALLOW_ORIGINS` seteado, cae al default
de la imagen (`http://localhost:3000`), que no coincide con el origin real
del navegador (`http://localhost`, vía nginx — ver la entrada de arriba
sobre `CONSOLE_API_URL`). El servidor rechaza la conexión WebSocket con
`"http://localhost is not an accepted origin"` (visible en los logs de
`dify-api`, no en los del navegador — el cliente solo reporta un
`WebSocket connection error: Error: timeout` genérico), y el store de
colaboración del editor se queda esperando ese handshake para siempre,
bloqueando toda la UI (drag de nodos, edición de prompts, todo).

Fix: `docker-compose.yml`, servicio `dify-api` —
`CONSOLE_CORS_ALLOW_ORIGINS: ${CONSOLE_CORS_ALLOW_ORIGINS:-http://localhost}`.

Para diagnosticar este tipo de problema sin pelear con el cliente
Socket.IO del navegador, probá el handshake a mano:

```bash
# Handshake de polling (primer paso, sin websocket todavía)
curl -sS "http://localhost:5001/socket.io/?EIO=4&transport=polling"
# Si devuelve un JSON con "sid" -> el server está bien.
# Buscá en los logs de dify-api algo como "... is not an accepted origin"
# durante el intento real desde el navegador.
docker compose logs dify-api | grep -i origin
```

Nota aparte: `dify-api` también tiene un loop separado y no crítico de
`ERROR [redis_manager.py] Cannot receive from redis... retrying in 1 secs`
en los logs — es el mismo `RedisManager` de Socket.IO haciendo polling con
un `socket_timeout` corto sobre una conexión de `pubsub.listen()` que por
diseño se queda escuchando indefinidamente. Es ruidoso pero no bloquea
nada con un solo worker (`SERVER_WORKER_AMOUNT=1`, el default de este
compose) — solo importaría si en algún momento se escala a más de un
worker/réplica de `dify-api`.

### Mismo síntoma, causa #2: nginx rate-limita el burst de carga inicial (503)

El editor de workflows dispara ~25-30 llamadas a `/console/api/*` de
golpe al cargar (app info, model-providers, tools, `workflows/draft`,
`workflows/draft/system-variables`, `workflows/draft/conversation-variables`,
etc.). Con `nginx.conf` en su configuración por defecto
(`limit_req_zone ... rate=10r/s` y `limit_req zone=api_limit burst=20
nodelay;`), ese burst supera el límite y nginx devuelve `503` a varias de
esas llamadas — visible en
`docker exec dify-nginx tail -n 50 /var/log/nginx/error.log` como
`limiting requests, excess: ... by zone "api_limit"`. Si el 503 le toca a
`system-variables` o `conversation-variables`, el store del editor nunca
termina de considerarse "sincronizado" y queda pegado en "Syncing data"
igual que la causa #1, aunque acá no hay ningún error de CORS/WebSocket de
por medio.

Fix: subir `rate=10r/s` → `rate=30r/s` en la zona `api_limit`, y los cuatro
`burst=20` (`/console/api`, `/api`, `/v1`, `/files`) → `burst=60`, en
`nginx/nginx.conf`. Después de editar, `docker compose restart nginx`
(no uses `nginx -s reload` acá — con el bind mount de este compose da
`[emerg] open() "/etc/nginx/nginx.conf" failed (2: No such file or
directory)` de forma intermitente; el restart completo del contenedor sí
funciona de forma confiable).

### Mismo síntoma, causa #3: el cliente de colaboración en tiempo real nunca llega a "ready"

Con las causas #1 y #2 ya resueltas (CORS bien, sin 503s), el editor puede
seguir pegado en "Syncing data" — pero ahora es un overlay realmente
bloqueante (`div` con `absolute inset-0 z-50 pointer-events:auto`,
`data-testid="collaboration-graph-loading"`) que tapa todo el canvas y el
panel lateral, no solo un toast. Se puede confirmar con
`document.elementFromPoint(x, y)` desde la consola del navegador sobre
cualquier coordenada del editor: siempre devuelve ese div, nunca el nodo
o el textarea de debajo — por eso ni los clicks ni el tipeo hacen nada.

Este overlay depende de dos cosas nuevas en Dify (colaboración
multiusuario tipo Figma — cursores, presencia, un CRDT compartido) que no
tienen que ver con el Socket.IO "clásico" del resto de la app:

1. **`NEXT_PUBLIC_SOCKET_URL`** (browser-facing, servicio `dify-web`): si
   no está seteada, el cliente cae al default `ws://localhost:5001` —
   igual que con `CONSOLE_API_URL`, el navegador no puede resolver ni el
   puerto 5001 (no publicado al host) ni el hostname interno de Docker.
   A diferencia de `CONSOLE_API_URL`, acá dejarla en blanco NO alcanza:
   el código hace `NEXT_PUBLIC_SOCKET_URL || "ws://localhost:5001"`, y un
   string vacío es falsy, así que sigue cayendo al default malo. Hace
   falta un valor real: `ws://localhost` (mismo origin que nginx).
2. **Ruta `/socket.io` en nginx**: el servidor Socket.IO real vive en
   `dify-api:5001` (`ext_socketio.py`, path por defecto `socket.io`), pero
   sin un `location /socket.io` explícito esa ruta cae en el `location /`
   genérico, que apunta a `dify-web:3000` — que no sirve ese path.

Con esas dos cosas corregidas, se puede confirmar que la conexión WebSocket
en sí funciona a mano desde la consola del navegador:

```js
const ws = new WebSocket('ws://localhost/socket.io/?EIO=4&transport=websocket');
ws.onopen = () => console.log('conectado');
// y en docker exec dify-nginx tail -f /var/log/nginx/access.log
// debería verse "GET /socket.io/?EIO=4&transport=websocket ... 101"
```

Pero aun así el editor puede seguir trabado: la app nunca inicia su
*propio* intento de conexión (`docker exec dify-nginx tail
/var/log/nginx/access.log | grep socket.io` no muestra ningún hit propio
de la app, solo el de la prueba manual de arriba). No vale la pena perseguir
ese bug de frontend en un stack de un solo usuario/admin local que no
necesita cursores compartidos ni edición simultánea — la salida más simple
es apagar la funcionalidad server-side:

Fix: `docker-compose.yml`, servicio `dify-api` (dentro del bloque
`&dify-api-env`, así que también aplica a `dify-worker`) —
`ENABLE_COLLABORATION_MODE: "false"`. Esto pone en `false` el
`isCollaborationEnabled` que gatilla el overlay
(`services/feature_service.py` → `system_features.enable_collaboration_mode`
→ `/console/api/features` o similar → frontend), así que el editor nunca
muestra ni espera ese estado.

Con la colaboración apagada server-side, `NEXT_PUBLIC_SOCKET_URL` y el
`location /socket.io` de nginx (causas #1 y #2) dejan de ser necesarios
para *este* síntoma puntual — quedan como código muerto útil solo si en
algún momento se reactiva `ENABLE_COLLABORATION_MODE`.

Las tres causas son independientes entre sí y pueden darse en cualquier
combinación — si el editor sigue trabado después de aplicar un fix,
revisá las otras dos antes de asumir que es un problema nuevo.

## Un chat o la ejecución de un workflow se queda colgado para siempre (sin error visible en el navegador)

En esta versión de Dify, `dify-api` no ejecuta el chat/workflow
sincrónicamente dentro del request HTTP — lo despacha a una tarea de
Celery (`workflow_based_app_execution_task.delay(...)`, en
`services/app_generate_service.py`) y streamea la respuesta de vuelta a
medida que esa tarea progresa. Sin dos piezas de infraestructura, la
tarea se encola pero nunca se ejecuta, y el chat queda esperando para
siempre sin ningún error del lado del navegador (el error real solo
aparece en `docker compose logs dify-api`):

1. **`CELERY_BROKER_URL` sin configurar** — Celery cae a su default
   hardcodeado `amqp://guest@localhost:5672` (RabbitMQ), que por
   supuesto no existe acá: `kombu.exceptions.OperationalError: [Errno 111]
   Connection refused`. Fix: apuntarlo a Redis (mismo patrón que el
   compose oficial de Dify) — `CELERY_BROKER_URL:
   redis://:${REDIS_PASSWORD}@redis:6379/1` (DB 1, separada de la DB 0
   de uso general, para no mezclar keys).
2. **Ningún worker de Celery corriendo** — encolar la tarea correctamente
   no sirve de nada si nadie la consume. Se agregó el servicio
   `dify-worker`: la misma imagen `langgenius/dify-api:latest` que
   `dify-api`, con `MODE: worker` (ver `docker/entrypoint.sh` de la
   imagen — arranca `celery -A celery_entrypoint.celery worker`).
   Comparte el resto del `environment` con `dify-api` vía un YAML anchor
   (`&dify-api-env` / `<<: *dify-api-env`) para no duplicar ~25 variables
   que tienen que coincidir entre ambos.

Para confirmar que el worker está realmente consumiendo la cola:

```bash
docker compose logs dify-worker | grep -i "ready\|received\|succeeded"
```

## Login queda en loop con `{"code":"unauthorized","message":"CSRF token is missing or invalid."}`

Se ve solo cuando el sitio se sirve por HTTPS (ej. detrás de Traefik en un
deploy vía Dokploy, ver `docs/DOKPLOY.md`) — no aparece en local sobre
HTTP. Causa: un mismatch entre el nombre de cookie que `dify-api` escribe
y el que `dify-web` busca.

`libs/token.py` en `dify-api` decide el nombre real de la cookie según:

```python
def is_secure() -> bool:
    return dify_config.CONSOLE_WEB_URL.startswith("https") and dify_config.CONSOLE_API_URL.startswith("https")

def _real_cookie_name(cookie_name):
    if is_secure() and _cookie_domain() is None:
        return "__Host-" + cookie_name
    return cookie_name
```

Con `CONSOLE_WEB_URL`/`CONSOLE_API_URL` en `https://...` (correcto, es la
URL pública real), `is_secure()` da `True` y el backend guarda la cookie
como `__Host-csrf_token`.

El bundle del navegador de `dify-web` decide el nombre que *busca* con la
misma lógica, pero mirando su propia variable `NEXT_PUBLIC_API_PREFIX`
(armada por el `entrypoint.sh` de la imagen como
`${CONSOLE_API_URL}/console/api`). Antes de este fix, `CONSOLE_API_URL`
de `dify-web` estaba en blanco a propósito (para que el navegador use
rutas relativas) — eso deja `NEXT_PUBLIC_API_PREFIX="/console/api"`, que
no empieza con `https://`, así que el frontend busca la cookie con el
nombre viejo `csrf_token`. Esa cookie no existe (el backend guardó
`__Host-csrf_token`), el frontend nunca manda el header `X-CSRF-Token`,
`check_csrf_token()` (double-submit-cookie puro, no mira `Origin` ni
`Referer`) rechaza la request con 401, la SPA lo interpreta como "no
autenticado" y redirige a `/signin` — loop infinito.

Fix: `docker-compose.yml`/`docker-compose.dokploy.yml`, servicio
`dify-web` — `CONSOLE_API_URL`/`APP_API_URL` pasan de `""` a
`${CONSOLE_API_URL:-http://localhost}` (el mismo valor público que ya usa
`dify-api`, nunca el hostname interno de Docker `http://dify-api:5001`:
ese mismo valor se hornea en el bundle del navegador, que no puede
resolver ese hostname). Así ambos servicios calculan el mismo nombre de
cookie a partir del mismo scheme.

Para confirmar en un deploy que ya falla: abrir DevTools → Application →
Cookies después de intentar loguearse, y revisar si existe
`__Host-csrf_token` (correcto) o `csrf_token` (mismatch) — o si el
request que responde 401 manda el header `X-CSRF-Token` con algún valor.

## SSL certificate error

```bash
certbot renew --force-renewal
cp /etc/letsencrypt/live/.../fullchain.pem nginx/ssl/cert.pem
docker-compose restart nginx
```
