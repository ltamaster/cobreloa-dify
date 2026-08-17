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

## dify-web: "TypeError: fetch failed ... ECONNREFUSED 127.0.0.1:5001"

`dify-web` corre su propio proceso Next.js dentro del contenedor; cuando
renderiza en el servidor (SSR) usa `CONSOLE_API_URL`/`APP_API_URL` para
llamar a la API. Si esas variables no están seteadas para el servicio
`dify-web`, la imagen cae a su default interno `http://127.0.0.1:5001` —
el SSR intenta conectarse al loopback del propio contenedor `dify-web`
(no al de `dify-api`, que es otro contenedor) y falla con `ECONNREFUSED`.

Dejarlas en blanco tampoco sirve: esta versión de la imagen exige una URL
absoluta configurada para SSR (falla con "Server console API URL is not
configured" si quedan vacías). La solución (ver `docker-compose.yml`,
servicio `dify-web`) es apuntarlas al nombre de servicio Docker interno:
`CONSOLE_API_URL: http://dify-api:5001` / `APP_API_URL: http://dify-api:5001`.
El navegador, en cambio, sigue usando rutas relativas (`/console/api`,
`/api`, `/v1`, `/files`) resueltas contra el origin que sirvió la página —
por eso siempre hay que acceder por `http://localhost` (puerto 80, vía
nginx) y nunca por `http://localhost:3000` directo, ya que nginx es quien
enruta esas rutas relativas hacia `dify-api`.

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

## SSL certificate error

```bash
certbot renew --force-renewal
cp /etc/letsencrypt/live/.../fullchain.pem nginx/ssl/cert.pem
docker-compose restart nginx
```
