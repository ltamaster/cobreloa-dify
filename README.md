# Cobreloa Dify - Assistant de Socios 🟠

**Asistente IA para membresía de Cobreloa usando Dify self-hosted**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://www.docker.com/)
[![Dify](https://img.shields.io/badge/Dify-Self--Hosted-FF6B35)](https://dify.ai)

## ✨ Características

✅ **Asistente IA Completo**
- Membresía y planes
- Pagos y cuotas
- Escuelas de fútbol
- Información de sede
- Escalado a soporte

✅ **Self-Hosted (On-Premise)**
- Control total de datos
- Sin dependencias en cloud
- Privacidad garantizada

✅ **Production Ready**
- SSL/TLS con Let's Encrypt
- Backups automáticos
- Rate limiting
- Monitoreo de salud

## 🔧 Requisitos

- Docker Desktop o Docker + Docker Compose
- 4GB RAM mínimo
- 10GB disco disponible
- Git

## 🚀 Inicio Rápido

### 1. Clonar repositorio

```bash
git clone https://github.com/ltamaster/cobreloa-dify.git
cd cobreloa-dify
```

### 2. Configurar variables

```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 3. Levantar servicios

```bash
docker-compose up -d
```

### 4. Acceder a Dify

```
Web: http://localhost:3000
API: http://localhost:5001
```

### 5. Crear cuenta admin

La primera vez te pide crear una cuenta de administrador.

## 📚 Documentación

- [INSTALACION.md](docs/INSTALACION.md) - Guía detallada
- [PRODUCCION.md](docs/PRODUCCION.md) - Deploy a VPS
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Solución de problemas

## 🐳 Comandos Útiles

```bash
# Levantar
docker-compose up -d

# Ver logs
docker-compose logs -f dify-api

# Detener
docker-compose down

# Limpiar todo
docker-compose down -v
```

## 📝 Licencia

MIT License - ver [LICENSE](LICENSE)

## 🙏 Créditos

- [Dify.AI](https://dify.ai) - Plataforma de IA
- [Anthropic Claude](https://anthropic.com) - Modelo LLM
- [Docker](https://www.docker.com/) - Containerización

---

**Hecho con ❤️ para Cobreloa**
