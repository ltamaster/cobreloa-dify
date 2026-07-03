# Diseño del Agente - Cobreloa Membership Assistant 🟠

## 📋 Visión General

**Asistente IA conversacional** que gestiona automáticamente consultas de socios de Cobreloa:
- ✅ Verificación de identidad (RUT)
- ✅ Consulta de estado de membresía
- ✅ Información sobre planes
- ✅ Procesamiento de pagos
- ✅ Inscripción en escuelas
- ✅ Información general (horarios, sede)
- ✅ Escalado a soporte humano

---

## 🏗️ Arquitectura del Agente

```
┌──────────────────────────────────┐
│    USUARIO EN COBRELOA.CL        │
│     (Chat Widget en website)     │
└────────────────┬─────────────────┘
                 │ HTTP/WebSocket
                 ↓
┌──────────────────────────────────┐
│  DIFY (Asistente IA)             │
│  ┌────────────────────────────┐  │
│  │ 1. Intent Classifier       │  │
│  │  (¿Qué necesita usuario?)  │  │
│  └────────────┬───────────────┘  │
│               │                   │
│  ┌────────────▼───────────────┐  │
│  │ 2. Router por Intención    │  │
│  │  ├─ Status Check           │  │
│  │  ├─ Become Member          │  │
│  │  ├─ Payment                │  │
│  │  ├─ Schools                │  │
│  │  ├─ Plans/Info             │  │
│  │  └─ Escalation             │  │
│  └────────────┬───────────────┘  │
│               │                   │
│  ┌────────────▼───────────────┐  │
│  │ 3. HTTP Calls (APIs)       │  │
│  │  ├─ membrezia.com          │  │
│  │  ├─ SendGrid               │  │
│  │  ├─ Mercado Pago           │  │
│  │  └─ Slack                  │  │
│  └────────────┬───────────────┘  │
│               │                   │
│  ┌────────────▼───────────────┐  │
│  │ 4. Knowledge Base          │  │
│  │  ├─ Planes                 │  │
│  │  ├─ Escuelas               │  │
│  │  ├─ Horarios               │  │
│  │  └─ FAQs                   │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
```

---

## 🔄 Flujos Conversacionales

### **FLUJO 1: Verificar Estado de Socio**

```
Usuario: "¿Cuál es mi estado?"
   ↓
Agente: "¿Cuál es tu RUT?"
   ↓
Usuario: "18123456-7"
   ↓
Agente: Consulta membrezia.com
   ↓
membrezia: Devuelve {email, name, plan, status}
   ↓
Agente: Envía código por email (SendGrid)
   ↓
Usuario: Ingresa código
   ↓
Agente: ✅ Verifica identidad
   ↓
Agente: Muestra estado (plan, próximo pago, beneficios)
```

---

### **FLUJO 2: Hacerse Socio**

```
Usuario: "Quiero ser socio"
   ↓
Agente: Muestra planes desde Knowledge Base
   ↓
Usuario: "Plan Premium ($35.000/mes)"
   ↓
Agente: Verifica identidad (Flujo 1)
   ↓
Agente: Genera link Mercado Pago
   ↓
Usuario: Paga en Mercado Pago
   ↓
Agente: Confirma pago ✅
   ↓
Agente: Envía email de bienvenida + datos
```

---

### **FLUJO 3: Pagar Cuota**

```
Usuario: "Quiero pagar mi cuota"
   ↓
Agente: "¿Qué método?"
  Opciones:
   - 💳 Tarjeta débito/crédito
   - 🏦 Transferencia bancaria
   - 📱 Mercado Pago
   - 💵 Efectivo en sede
   ↓
Usuario: "Mercado Pago"
   ↓
Agente: Genera link + monto
   ↓
Usuario: Paga
   ↓
Agente: Confirma en membrezia.com
   ↓
Agente: Envía recibo por email
```

---

### **FLUJO 4: Escuelas de Fútbol**

```
Usuario: "Escuelas de fútbol"
   ↓
Agente: Muestra categorías (KB):
  - U-8: $25.000/mes (Lunes/Miércoles 17:00)
  - U-10: $30.000/mes (Martes/Jueves 17:30)
  - U-12: $35.000/mes (Lunes/Miércoles/Viernes 18:00)
  - U-14/16: $40.000/mes
   ↓
Usuario: "U-10"
   ↓
Agente: Muestra detalles + "¿Inscribir?"
   ↓
Usuario: "Sí"
   ↓
Agente: Pide:
  - Nombre del menor
  - Edad
  - Email de contacto
   ↓
Agente: Envía a escuelas@cobreloa.cl
   ↓
Agente: "Nos contactaremos en 24h"
```

---

### **FLUJO 5: Escalado a Soporte**

```
Usuario: "Quiero hablar con un humano"
   ↓
Agente: Crea ticket automático
   ↓
Agente: Envía email a soporte@cobreloa.cl
   ↓
Agente: Notifica Slack #soporte-escalados
   ↓
Agente: Muestra al usuario:
  📌 Ticket: TKT-2024060115
  ⏱️  Respuesta en: máximo 24 horas
  📧 Email: soporte@cobreloa.cl
```

---

## 🛡️ Seguridad

### **3 Capas de Defensa**

#### **1️⃣ Input Validation**
- Detecta intentos de prompt injection
- Bloquea keywords: `ignora`, `jailbreak`, `dan`, `system prompt`
- Limita tamaño a 5000 caracteres
- Rechaza URLs sospechosas

#### **2️⃣ Intent Classification**
- Solo 7 intenciones válidas permitidas
- Confidence threshold mínimo 0.7
- Rechaza "out of scope"
- Rate limiting (10 req/segundo por IP)

#### **3️⃣ System Prompt Restrictivo**
- Claude recibe instrucciones claras
- Temperatura baja (0.3) = respuestas consistentes
- Max tokens limitado (500)
- Solo responde sobre membresía

---

## 🔌 Integraciones Externas

### **membrezia.com**
```
POST /v1/members/lookup
  Input: {rut}
  Output: {email, name, plan, status, member_id}

POST /v1/members/create
  Input: {rut, email, name, plan}
  Output: {success, member_id}

PUT /v1/members/{member_id}
  Input: {status, plan, quota_paid_date}
  Output: {updated}
```

### **SendGrid Email**
```
Verificación:     Código 6 dígitos (10 min TTL)
Bienvenida:       Datos de socio + acceso
Recibo Pago:      Comprobante + próximo pago
Escalado:         Ticket + contexto conversación
Inscripción:      Datos menor → escuelas@cobreloa.cl
```

### **Mercado Pago**
```
Genera: Link de pago con monto
Usuario: Paga en sitio Mercado Pago
Callback: Confirma transacción
Agente: Actualiza estado
```

### **Slack Notification**
```
Channel: #soporte-escalados
Mensaje: "Nueva escalación - Usuario X - Ticket TKT-XXX"
Link: A detalles en sistema
```

---

## 📚 Knowledge Base (en Dify)

| Documento | Contenido | Búsqueda |
|-----------|-----------|----------|
| planes.md | 3 planes, precios, beneficios | "plan", "precio", "premium" |
| escuelas.md | 4 categorías U-8 a U-16 | "escuela", "fútbol", "menor" |
| horarios.md | Sede, dirección, teléfono | "horario", "dirección", "sede" |
| faqs.md | 10+ preguntas frecuentes | "cambiar", "transferir", "cancelar" |
| formas_pago.md | 4 métodos de pago | "pagar", "tarjeta", "transferencia" |

**Búsqueda:** Hybrid (semántica + palabras clave)
**Top-K:** 5 documentos más relevantes
**Score Threshold:** 0.5

---

## 💾 Variables de Sesión

Durante la conversación, Dify mantiene:

```json
{
  "user_rut": "18123456-7",
  "user_email": "usuario@example.com",
  "user_name": "Juan García",
  "verification_code": "123456",
  "verified": true,
  "member_id": "mem_12345",
  "current_plan": "Premium",
  "member_status": "active",
  "last_payment_date": "2024-06-15",
  "next_payment_date": "2024-07-15",
  "conversation_intent": "status_check",
  "escalation_ticket_id": "TKT-2024061501"
}
```

---

## ⚙️ Configuración Recomendada (Dify)

| Parámetro | Valor | Razón |
|-----------|-------|-------|
| **Model** | Claude 3.5 Sonnet | Mejor calidad respuestas |
| **Temperature** | 0.3 | Conservador, seguro |
| **Top P** | 0.7 | Variabilidad controlada |
| **Max Tokens** | 500 | Respuestas concisas |
| **Timeout** | 30s | APIs externas |
| **Language** | Español | Localización |

---

## 📊 Flujo de Deploy

```
docker-compose up -d
   ↓ (30-60 segundos)
PostgreSQL inicia
   ↓
Redis inicia
   ↓
Dify API inicia
   ↓
Dify Web inicia
   ↓
Nginx inicia
   ↓
✅ Agente listo en http://localhost:3000
```

**Primera vez:**
1. Crea cuenta admin
2. Importa Knowledge Base
3. Crea workflows en UI
4. Configura integraciones (API keys)

---

## 🎯 Casos de Uso

### **Usuario 1: Nuevo Socio**
```
"Hola, quiero saber cómo hacerme socio"
→ Agente muestra planes
→ Usuario elige Premium
→ Verifica identidad
→ Genera link de pago
→ Usuario paga
→ ✅ Acceso inmediato
```

### **Usuario 2: Socio Existente**
```
"¿Cuándo vence mi cuota?"
→ Agente pide RUT
→ Verifica identidad
→ Muestra: próximo pago 15 julio
→ Ofrece pagar ahora
→ Usuario paga
→ ✅ Recibe recibo
```

### **Usuario 3: Quiere Inscribir Hijo**
```
"Escuelas de fútbol para mi hijo"
→ Agente muestra categorías
→ Usuario elige U-10
→ Muestra: lunes/jueves, $30k
→ Usuario pide inscribir
→ Agente recopila datos
→ ✅ Envía a escuelas@cobreloa.cl
```

---

## 🔮 Futuro

- [ ] Soporte multiidioma (EN/ES)
- [ ] Análisis de sentimiento
- [ ] Recomendaciones personalizadas
- [ ] Dashboard de analytics
- [ ] Integración WhatsApp
- [ ] Mobile app
- [ ] AI para recomendación de planes

---

**Última actualización:** Junio 2024 | v1.0
