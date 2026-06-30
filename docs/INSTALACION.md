# Guía de Instalación

## Requisitos

- Docker Desktop o Docker + Docker Compose
- 4GB RAM mínimo
- 10GB disco disponible
- Git

## Pasos

### 1. Clonar

```bash
git clone https://github.com/ltamaster/cobreloa-dify.git
cd cobreloa-dify
```

### 2. Configurar

```bash
cp .env.example .env
nano .env
```

Cambiar al menos:
- `POSTGRES_PASSWORD`
- `REDIS_PASSWORD`
- `SECRET_KEY`
- `ANTHROPIC_API_KEY`

### 3. Levantar

```bash
docker-compose up -d
```

### 4. Esperar

```bash
docker-compose logs -f dify-api
```

Cuando veas "ready", continúa.

### 5. Acceder

http://localhost:3000

### 6. Crear cuenta admin

Sigue el wizard de setup.

## Troubleshooting

### Puertos ya en uso

```bash
docker-compose down
# o cambiar puertos en .env
```

### Database error

```bash
docker-compose down -v
docker-compose up -d
```

### Memory issues

```bash
docker stats
# Aumentar recursos en Docker Desktop settings
```
