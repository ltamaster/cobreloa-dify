#!/usr/bin/env python3
"""
Cobreloa Dify - Auto-Setup Script
Verifica que Dify esté listo y guía la configuración manual del agente
"""

import requests
import time
import os
import sys

DIFY_BASE_URL = os.getenv("DIFY_URL", "http://dify-api:5001")
DIFY_WEB_URL = os.getenv("DIFY_WEB_URL", "http://dify-web:3000")
MAX_RETRIES = 60  # 2 minutos máximo

class DifySetup:
    def __init__(self):
        self.base_url = DIFY_BASE_URL
        self.web_url = DIFY_WEB_URL
    
    def health_check(self):
        """Esperar a que Dify esté listo"""
        print("\n🔍 Esperando que Dify API esté listo...")
        print("   (esto puede tomar 30-60 segundos la primera vez)\n")
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.get(
                    f"{self.base_url}/health",
                    timeout=5
                )
                if response.status_code == 200:
                    print(f"✅ Dify API listo en intento {attempt}")
                    return True
            except Exception as e:
                pass
            
            if attempt % 10 == 0:
                print(f"⏳ Intento {attempt}/{MAX_RETRIES}...")
            
            time.sleep(2)
        
        print("❌ Timeout - Dify no respondió")
        return False
    
    def check_web(self):
        """Verificar que la interfaz web esté lista"""
        print("\n🔍 Esperando Dify Web UI...")
        
        for attempt in range(1, 30):
            try:
                response = requests.get(
                    f"{self.web_url}",
                    timeout=5
                )
                if response.status_code == 200:
                    print(f"✅ Dify Web UI listo")
                    return True
            except:
                pass
            
            time.sleep(1)
        
        return False
    
    def log(self, message, icon="ℹ️ "):
        """Logging formateado"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {icon} {message}")

def print_banner():
    """Imprimir banner de bienvenida"""
    banner = """
╔════════════════════════════════════════════════════╗
║                                                    ║
║   🟠 COBRELOA DIFY - AUTO SETUP                   ║
║   Asistente IA para Membresía                     ║
║                                                    ║
╚════════════════════════════════════════════════════╝
"""
    print(banner)

def print_next_steps():
    """Imprimir pasos a seguir"""
    steps = """
╔════════════════════════════════════════════════════╗
║                                                    ║
║  ✅ DIFY ESTÁ LISTO                               ║
║                                                    ║
║  🌐 Accede a:  http://localhost:3000              ║
║                                                    ║
╠════════════════════════════════════════════════════╣
║                                                    ║
║  📋 PRÓXIMOS PASOS:                               ║
║                                                    ║
║  1. Crea tu cuenta admin en Dify                  ║
║     http://localhost:3000                         ║
║                                                    ║
║  2. Lee la documentación:                         ║
║     docs/AGENT-DESIGN.md                          ║
║                                                    ║
║  3. Importa Knowledge Base:                       ║
║     - Ve a Settings → Knowledge Base              ║
║     - Sube archivos desde docs/                   ║
║       └─ planes.md                                ║
║       └─ escuelas.md                              ║
║       └─ horarios.md                              ║
║       └─ faqs.md                                  ║
║                                                    ║
║  4. Crea workflows en la UI:                      ║
║     - Main Intent Router                          ║
║     - RUT Verification                            ║
║     - Member Status                               ║
║     - Become Member                               ║
║     - Payment Flow                                ║
║     - Schools Enrollment                          ║
║     - Escalation to Support                       ║
║                                                    ║
║  5. Configura integraciones (APIs):               ║
║     - Anthropic (Claude)                          ║
║     - SendGrid (emails)                           ║
║     - membrezia.com (custom)                      ║
║     - Mercado Pago (opcional)                     ║
║     - Slack (opcional)                            ║
║                                                    ║
║  6. Prueba el agente:                             ║
║     - Chat en preview                             ║
║     - Simula conversaciones                       ║
║                                                    ║
╠════════════════════════════════════════════════════╣
║                                                    ║
║  📚 DOCUMENTACIÓN:                                ║
║     /docs/AGENT-DESIGN.md    (Arquitectura)       ║
║     /docs/INSTALACION.md     (Setup)              ║
║     /docs/PRODUCCION.md      (Deploy)             ║
║     /docs/TROUBLESHOOTING.md (Problemas)          ║
║                                                    ║
║  🆘 SOPORTE:                                      ║
║     GitHub Issues:  GitHub Issues                 ║
║     Discussions:    GitHub Discussions            ║
║                                                    ║
║  🛠️  COMANDOS ÚTILES:                             ║
║     docker-compose ps      (Ver servicios)        ║
║     docker-compose logs -f (Ver logs)             ║
║     docker-compose down    (Detener)              ║
║     docker-compose down -v (Limpiar todo)         ║
║                                                    ║
╚════════════════════════════════════════════════════╝
"""
    print(steps)

def main():
    setup = DifySetup()
    
    print_banner()
    
    # Step 1: Health check
    if not setup.health_check():
        print("\n❌ ERROR: No se pudo conectar a Dify API")
        print("   Verifica que docker-compose esté corriendo:")
        print("   $ docker-compose ps")
        return False
    
    # Step 2: Check Web UI
    if not setup.check_web():
        print("\n⚠️  Web UI aún no está completamente listo")
        print("   Pero la API funciona, espera unos segundos más...")
    
    # Step 3: Print next steps
    print_next_steps()
    
    print("\n🎉 Setup completado exitosamente!\n")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Cancelado por usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
