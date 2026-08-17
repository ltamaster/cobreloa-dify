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
  80 vía nginx, y nunca por `http://localhost:3000` directo).
- `SERVER_CONSOLE_API_URL: http://dify-api:5001` — variable **server-only**
  que el SSR lee con prioridad sobre `CONSOLE_API_URL` (no existe un
  `SERVER_APP_API_URL` equivalente en esta versión de la imagen).

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

## SSL certificate error

```bash
certbot renew --force-renewal
cp /etc/letsencrypt/live/.../fullchain.pem nginx/ssl/cert.pem
docker-compose restart nginx
```
