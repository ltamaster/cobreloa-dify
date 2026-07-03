# Cobreloa Dify - Assistant de Socios 🟠

**Asistente IA conversacional para gestionar membresía de Cobreloa usando Dify self-hosted**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://www.docker.com/)
[![Dify](https://img.shields.io/badge/Dify-Self--Hosted-FF6B35)](https://dify.ai)
[![Claude](https://img.shields.io/badge/Claude-3.5%20Sonnet-202124?logo=anthropic)](https://anthropic.com)

---

## ¿Qué Hace el Agente? 🤖

### **Asistente Conversacional Inteligente en Español**

El agente maneja automáticamente todos los servicios de membresía:

✅ **Mi Estado** - Consulta plan, próximo pago, beneficios activos  
✅ **Nuevos Socios** - Registro completo + pago online  
✅ **Pagar Cuota** - Múltiples métodos (tarjeta, transferencia, MP)  
✅ **Escuelas** - Info e inscripción de menores en 4 categorías  
✅ **Planes** - Detalles de los 3 planes disponibles  
✅ **Información** - Horarios, dirección, teléfono, FAQs  
✅ **Soporte** - Escala a humanos automáticamente  

### **Características Clave**

🔐 **Verificación de Identidad**
- Validación por RUT
- Código de 6 dígitos por email
- Sesión segura

💬 **Conversación Natural**
- Entiende qué quiere el usuario
- Responde en lenguaje conversacional
- Sin necesidad de código

🌐 **Integrado con APIs Reales**
- membrezia.com (gestión de socios)
- SendGrid (envío de emails)
- Mercado Pago (procesamiento de pagos)
- Slack (notificaciones de escalados)

📚 **Knowledge Base Actualizable**
- Planes y precios
- Escuelas de fútbol
- Horarios y ubicación
- Preguntas frecuentes

---

## 📖 Documentación Completa

**👉 LEE PRIMERO:** [AGENT-DESIGN.md](docs/AGENT-DESIGN.md)
- Arquitectura completa del agente
- Flujos conversacionales detallados
- Cómo funciona cada integración
- Seguridad y protecciones

Otros documentos:
- [INSTALACION.md](docs/INSTALACION.md) - Guía de instalación
- [PRODUCCION.md](docs/PRODUCCION.md) - Deploy en servidor
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Solución de problemas

---

## 🚀 Inicio Rápido

### **Opción 1: Desarrollo Local (Recomendado)**

```bash
# 1. Clonar repositorio
git clone https://github.com/ltamaster/cobreloa-dify.git
cd cobreloa-dify

# 2. Configurar variables de entorno
cp .env.example .env

# 3. Levantar servicios (espera 30-60 segundos)
docker-compose up -d

# 4. Acceder a Dify
# Web:  http://localhost:3000
# API:  http://localhost:5001

# 5. Ver logs (para verificar que todo está ok)
docker-compose logs -f dify-api
```

**Primera vez:**
1. Accede a `http://localhost:3000`
2. Crea cuenta admin
3. Lee [AGENT-DESIGN.md](docs/AGENT-DESIGN.md) para entender la arquitectura
4. Importa Knowledge Base desde la carpeta `docs/`
5. Crea workflows en la UI de Dify

### **Opción 2: Producción en VPS**

```bash
# 1. Conectar a servidor
ssh root@tu_ip_vps

# 2. Clonar
mkdir -p /opt/cobreloa-dify
cd /opt/cobreloa-dify
git clone https://github.com/ltamaster/cobreloa-dify.git .

# 3. Configurar con credenciales reales
cp .env.example .env
nano .env  # Editar con tus valores

# 4. Setup SSL (Let's Encrypt)
apt install certbot -y
certbot certonly --standalone -d socios.cobreloa.cl
cp /etc/letsencrypt/live/socios.cobreloa.cl/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/socios.cobreloa.cl/privkey.pem nginx/ssl/key.pem

# 5. Deploy con stack de producción
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 6. Verificar
curl https://socios.cobreloa.cl
```

---

## 🏗️ Arquitectura

```
┌─────────────────────┐
│  Usuario (cobreloa) │ ← Pregunta en chat
└────────────┬────────┘
             │
             ↓
┌─────────────────────────────────────┐
│ Dify (Agente IA - Claude Sonnet)    │
│ ├─ Intent Detection                 │
│ ├─ Knowledge Base                   │
│ └─ API Integrations                 │
└────────────┬────────────────────────┘
             │
    ┌────────┼────────┬──────────────┐
    ↓        ↓        ↓              ↓
┌────────┬────────┬─────────┬──────────────┐
│ Memb.  │SendGrid│ Mercado │    Slack     │
│ Manage │ Email  │  Pago   │ Notif        │
└────────┴────────┴─────────┴──────────────┘
```

**Stack Tecnológico:**
- 🐳 **Docker Compose** - Orquestación de contenedores
- 🗄️ **PostgreSQL 15** - Base de datos
- 🔴 **Redis 7** - Cache
- 🤖 **Claude 3.5 Sonnet** - Modelo de IA (Anthropic)
- 📚 **Dify** - Plataforma (sin-código para workflows)
- 🌐 **Nginx** - Reverse proxy + SSL

---

## 🔧 Requisitos

### Mínimos
- Docker Desktop o Docker + Docker Compose
- 4GB RAM
- 10GB disco disponible
- Git

### Recomendados (Producción)
- VPS con Ubuntu 20.04+
- 8GB RAM
- Dominio propio
- API Keys:
  - Anthropic (para Claude)
  - SendGrid (para emails)
  - membrezia.com (acceso API)

---

## ⚙️ Configuración

Todos los parámetros se configuran en `.env`:

```bash
# Base de datos
POSTGRES_PASSWORD=tu_password_seguro

# Caché
REDIS_PASSWORD=tu_redis_password

# Seguridad
SECRET_KEY=clave_aleatoria_32_chars_min

# APIs Externas
ANTHROPIC_API_KEY=sk-ant-xxxxx
SENDGRID_API_KEY=SG.xxxxx
MEMBREZIA_API_KEY=sk_membrezia_xxxxx

# URLs
CONSOLE_WEB_URL=http://localhost:3000
CONSOLE_API_URL=http://localhost:5001
```

Ver `.env.example` para todas las opciones.

---

## 🛡️ Seguridad

✅ **3 capas de protección:**
1. Validación de entrada (bloquea ataques comunes)
2. Clasificación de intención (solo permite 7 tipos)
3. System prompt restrictivo (Claude limitado a membresía)

✅ **Verificación de identidad** obligatoria con RUT  
✅ **Rate limiting** en APIs (máximo 10 req/segundo por IP)  
✅ **SSL/TLS** en producción  
✅ **Logs de seguridad** de todos los eventos  

---

## 🐳 Comandos Útiles

```bash
# Ver estado
docker-compose ps

# Ver logs (API)
docker-compose logs -f dify-api

# Ver logs (Web)
docker-compose logs -f dify-web

# Entrar a contenedor
docker-compose exec dify-api bash

# Entrar a base de datos
docker-compose exec postgres psql -U dify

# Detener servicios
docker-compose down

# Hacer backup
docker-compose exec postgres pg_dump -U dify dify > backup.sql

# Limpiar todo (CUIDADO - elimina datos)
docker-compose down -v
```

---

## 📊 Monitoreo

Dify proporciona dashboards con:
- Número de conversaciones
- Intenciones más frecuentes
- Errores y excepciones
- Tiempo promedio de respuesta
- Escalados realizados

---

## 🔌 Integraciones

### **membrezia.com**
Gestión de socios - lookup, creación, actualización

### **SendGrid**
Envío de emails:
- Códigos de verificación
- Confirmaciones de pago
- Recibos
- Notificaciones de escalado

### **Mercado Pago**
Procesamiento de pagos:
- Generación de links de pago
- Webhook de confirmación
- Múltiples métodos

### **Slack**
Notificaciones:
- Escalados a soporte
- Errores críticos

---

## 🤝 Contribuir

```bash
# Fork y clone
git clone https://github.com/tu-usuario/cobreloa-dify.git

# Crea rama
git checkout -b feature/tu-mejora

# Commit
git commit -m "Agregar mejora X"

# Push
git push origin feature/tu-mejora

# Abre Pull Request en GitHub
```

---

## 📝 Licencia

MIT License - [LICENSE](LICENSE)

---

## 🆘 Soporte

- 📖 **Lee:** [AGENT-DESIGN.md](docs/AGENT-DESIGN.md)
- 🐛 **Issues:** https://github.com/ltamaster/cobreloa-dify/issues
- 💬 **Discussions:** https://github.com/ltamaster/cobreloa-dify/discussions

---

## 🙏 Créditos

- [Dify.AI](https://dify.ai) - Plataforma de workflows IA
- [Anthropic Claude](https://anthropic.com) - Modelo LLM
- [Docker](https://docker.com) - Containerización
- [PostgreSQL](https://postgresql.org) - Base de datos
- [Redis](https://redis.io) - Cache

---

## 🎯 Roadmap

- [ ] Soporte multiidioma (EN/FR/PT)
- [ ] Análisis de sentimiento
- [ ] Recomendaciones personalizadas
- [ ] Dashboard de analytics avanzado
- [ ] Integración WhatsApp
- [ ] Mobile app
- [ ] IA para recomendación inteligente de planes

---

**Hecho con ❤️ para Cobreloa**

Versión 1.0 | Junio 2024 | Licensed MIT
