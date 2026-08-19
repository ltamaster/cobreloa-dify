# Deploy en VPS dedicada con Dokploy

Alternativa a `docs/PRODUCCION.md` (VPS + nginx propio + certbot manual):
acá Dokploy maneja el reverse proxy (Traefik) y el certificado SSL solo,
así que hay menos pasos manuales. Usa una **VPS dedicada solo a este
stack** — si necesitas compartir la VPS con otro sitio (ej. un WordPress
ya instalado ahí), este documento no aplica tal cual, ver la sección
"VPS compartida" más abajo.

## Por qué un compose distinto

`docker-compose.dokploy.yml` es una variante autocontenida de
`docker-compose.yml`, no un override:

- `nginx` usa `expose` en vez de `ports: 80:80/443:443` — Traefik llega por
  la red de Docker, no por un puerto publicado al host. `nginx.conf` no
  cambia: sigue enrutando `/`, `/console/api`, `/api`, `/v1`, `/files`,
  `/socket.io` internamente igual que en local.
- `postgres`/`redis`/`dify-api` usan `expose` en vez de publicar a
  `127.0.0.1` — en una VPS dedicada nadie necesita entrar por esos puertos
  desde el host.
- `restart: always` + el servicio `postgres-backup` (antes en
  `docker-compose.prod.yml`, que sigue existiendo para el flujo de
  `docs/PRODUCCION.md`).

Si tocas algo en `docker-compose.yml`, replicalo acá — no hay mecanismo
automático que los mantenga en sync.

## 1. Instalar Dokploy

En una VPS Ubuntu limpia:

```bash
curl -sSL https://dokploy.com/install.sh | sh
```

Accede al panel en `http://IP_DE_LA_VPS:3000` y crea el usuario admin.

## 2. DNS

Registro **A** apuntando a la IP de la VPS. Ejemplo usado en este doc:
`dify-dev.cobreloa.cl`.

## 3. Crear el proyecto

En Dokploy: **Create Project** → **Docker Compose** → fuente Git
(`git@github.com:ltamaster/cobreloa-dify.git`, rama `main`) → **Compose
Path**: `docker-compose.dokploy.yml`.

## 4. Variables de entorno

Pegar en la pestaña **Environment** (mismo set que `.env.example`, con
estos valores distintos al default local):

```bash
POSTGRES_PASSWORD=<password fuerte, no el default>
REDIS_PASSWORD=<password fuerte, no el default>
SECRET_KEY=<random, min 32 chars>
PLUGIN_DAEMON_KEY=<random, min 32 chars>
PLUGIN_DIFY_INNER_API_KEY=<random, min 32 chars — distinto del anterior>
ANTHROPIC_API_KEY=sk-ant-...

CONSOLE_WEB_URL=https://dify-dev.cobreloa.cl
CONSOLE_API_URL=https://dify-dev.cobreloa.cl
SERVICE_API_URL=https://dify-dev.cobreloa.cl
APP_WEB_URL=https://dify-dev.cobreloa.cl
CONSOLE_CORS_ALLOW_ORIGINS=https://dify-dev.cobreloa.cl
# Agregar acá el origin del WordPress que va a embeber el widget:
WEB_API_CORS_ALLOW_ORIGINS=https://dify-dev.cobreloa.cl,https://dev.cobreloa.cl
NEXT_PUBLIC_SOCKET_URL=wss://dify-dev.cobreloa.cl
```

Genera los valores random con `openssl rand -hex 32`.

## 5. Dominio

Pestaña **Domains** del proyecto → agregar `dify-dev.cobreloa.cl` →
servicio `nginx`, puerto `80`, HTTPS on (Let's Encrypt automático).

## 6. Deploy

Botón **Deploy**. Revisa logs por servicio si algo no levanta — los
healthchecks (`postgres`, `redis`, `plugin-daemon`, `dify-api`, `dify-web`,
`nginx`) están todos definidos, así que un servicio caído se ve rápido en
la UI.

## 7. Verificar

```bash
curl -I https://dify-dev.cobreloa.cl/health
curl -I https://dify-dev.cobreloa.cl/embed.min.js
```

## 8. Recrear el asistente

Esta es una base de datos nueva — nada migra solo desde tu Dify local:

1. Studio → **Create from DSL** → subir `dify/workflows/cobreloa-assistant-chatflow.yml`.
2. Volver a subir el escudo de Cobreloa como ícono de la app y fijar
   `Chat color theme` = `#FF5A1F` (Edit App Info / Branding — no viaja con
   el DSL).
3. Copiar el token nuevo del embed (`Publish → Embed Into Site`) — va a
   ser distinto al de tu instancia local.

## 9. Apuntar el WordPress al Dify nuevo

En el sitio que embebe el widget (WPCode → snippet del chatbot), actualizar:

- `baseUrl: 'https://dify-dev.cobreloa.cl'`
- `token`/`id`: el nuevo token del paso anterior
- `src="https://dify-dev.cobreloa.cl/embed.min.js"`

## VPS compartida (con otro sitio ya corriendo en 80/443)

Si la VPS ya sirve otro sitio en los puertos 80/443 (ej. un WordPress vía
Apache/nginx/OpenLiteSpeed fuera de Docker), Dokploy igual puede convivir
ahí — su Traefik también necesita esos puertos, así que hay que decidir
cuál de los dos los posee. Lo más simple sigue siendo una VPS dedicada;
si no es posible, hay que revisar puerto por puerto qué proceso ya escucha
(`sudo ss -tlnp | grep -E ':80|:443'`) antes de instalar Dokploy.

## Migrando una VPS que ya corría `docs/PRODUCCION.md` a Dokploy

`docker-compose.dokploy.yml` usa los mismos `container_name` que
`docker-compose.yml` (Docker los trata como nombres globales, no los
namespacea el proyecto/directorio). **No corras ambos compose al mismo
tiempo en el mismo host** — `docker compose up` falla por nombre
duplicado, y si además coincide el nombre de proyecto puede pisar el
volumen `postgres_data` equivocado. Antes de desplegar vía Dokploy en una
VPS que ya tenía el stack viejo arriba:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml down
```
