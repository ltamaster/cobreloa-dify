# Deploy a Producción

## Requisitos

- VPS con Ubuntu 20.04+
- 8GB RAM
- 20GB SSD
- Dominio apuntado

## Instalación

### 1. SSH

```bash
ssh root@tu_ip_vps
```

### 2. Instalar Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### 3. Clonar

```bash
mkdir -p /opt/cobreloa-dify
cd /opt/cobreloa-dify
git clone https://github.com/ltamaster/cobreloa-dify.git .
```

### 4. Configurar

```bash
cp .env.example .env
nano .env
```

Cambiar valores IMPORTANTES.

### 5. Setup SSL

```bash
apt install certbot -y

certbot certonly --standalone \
  -d socios.cobreloa.cl \
  -d api.cobreloa.cl

cp /etc/letsencrypt/live/socios.cobreloa.cl/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/socios.cobreloa.cl/privkey.pem nginx/ssl/key.pem
```

### 6. Deploy

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 7. Verificar

```bash
curl https://socios.cobreloa.cl
```

## Mantenimiento

### Backups

Automático cada 24h en `/backups`

### Actualizar

```bash
git pull
docker-compose pull
docker-compose down
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```
