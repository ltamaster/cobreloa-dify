#!/usr/bin/env python3
"""
Sube un DSL de Chatflow a una app ya existente en Dify y publica el resultado,
usando la API de consola (login por email/password, no la API key de la app).

Uso:
    export DIFY_ADMIN_EMAIL="tu-cuenta-admin@..."
    export DIFY_ADMIN_PASSWORD="..."          # nunca lo commitees
    export DIFY_BASE_URL="http://localhost"   # sin /v1 (raiz del sitio, no del Service API)
    export DIFY_APP_ID="c975767d-c444-478b-bc74-dfad7c2e494b"
    python3 deploy_dsl.py dify/workflows/cobreloa-assistant-chatflow.yml

Hace, en orden:
  1. POST {base}/console/api/login (password en Base64, ver libs/encryption.py
     en dify-api)     -> cookies de sesion (access_token, csrf_token; el login
     NO devuelve el token en el body, Dify lo entrega por Set-Cookie)
  2. POST {base}/console/api/apps/imports   -> sobreescribe el borrador de
     DIFY_APP_ID (mode=yaml-content)
  3. POST {base}/console/api/apps/imports/{import_id}/confirm  (solo si el
     import queda en estado 'pending', p.ej. por dependencias de plugins)
  4. POST {base}/console/api/apps/{app_id}/workflows/publish   -> publica el
     borrador

Las rutas /console/api/* exigen ademas el header X-CSRF-Token igual al valor
de la cookie csrf_token (doble-submit CSRF), por eso se usa un CookieJar en
vez de mandar un Bearer token suelto.

Si algo fallara a mitad de camino, el borrador queda modificado pero no
publicado: lo que sirve /v1/chat-messages no cambia hasta el paso 4.
"""
import base64
import http.cookiejar
import json
import os
import sys
import urllib.request
import urllib.error


def env_or_die(name):
    value = os.environ.get(name)
    if not value:
        print(f"ERROR: falta la variable de entorno {name}", file=sys.stderr)
        sys.exit(1)
    return value


def csrf_header(cookie_jar, base_url):
    for cookie in cookie_jar:
        if cookie.name.endswith("csrf_token"):
            return {"X-CSRF-Token": cookie.value}
    return {}


def request(opener, cookie_jar, base_url, method, path, payload=None):
    url = f"{base_url}{path}"
    headers = {"Content-Type": "application/json", **csrf_header(cookie_jar, base_url)}
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with opener.open(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, (json.loads(body) if body else {})
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, {"raw": body}


def main():
    if len(sys.argv) != 2:
        print("Uso: python3 deploy_dsl.py <ruta-al-dsl.yml>", file=sys.stderr)
        sys.exit(1)

    yaml_path = sys.argv[1]
    with open(yaml_path, encoding="utf-8") as f:
        yaml_content = f.read()

    base_url = env_or_die("DIFY_BASE_URL").rstrip("/")
    if base_url.endswith("/v1"):
        # DIFY_BASE_URL is shared with test_chatflow.py, which needs the
        # /v1 (Service API) suffix; this script needs the console API at
        # the site root, so tolerate a stray /v1 instead of failing.
        base_url = base_url[: -len("/v1")]
    app_id = env_or_die("DIFY_APP_ID")
    email = env_or_die("DIFY_ADMIN_EMAIL")
    password = env_or_die("DIFY_ADMIN_PASSWORD")

    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

    print(f"[1/4] Login en {base_url} como {email}...")
    # El endpoint de login exige el campo 'password' en Base64 (no es cifrado
    # real, solo ofuscacion de transporte: ver libs/encryption.py en dify-api,
    # confia en HTTPS para la seguridad real).
    encoded_password = base64.b64encode(password.encode("utf-8")).decode("ascii")
    status, body = request(
        opener, cookie_jar, base_url, "POST", "/console/api/login",
        payload={"email": email, "password": encoded_password, "remember_me": False},
    )
    if status != 200 or body.get("result") != "success":
        print(f"ERROR en login: HTTP {status} {body}", file=sys.stderr)
        sys.exit(1)
    if not any(c.name.endswith("access_token") for c in cookie_jar):
        print(f"ERROR: login respondio success pero no llego la cookie access_token: {body}", file=sys.stderr)
        sys.exit(1)
    print("      OK")

    print(f"[2/4] Importando DSL sobre app_id={app_id}...")
    status, body = request(
        opener, cookie_jar, base_url, "POST", "/console/api/apps/imports",
        payload={"mode": "yaml-content", "yaml_content": yaml_content, "app_id": app_id},
    )
    if status not in (200, 202):
        print(f"ERROR en import: HTTP {status} {body}", file=sys.stderr)
        sys.exit(1)
    import_status = body.get("status")
    import_id = body.get("id")
    print(f"      status={import_status} import_id={import_id}")

    if status == 202 or import_status == "pending":
        print("[3/4] Import pendiente de confirmacion (dependencias/plugins), confirmando...")
        status, body = request(
            opener, cookie_jar, base_url, "POST", f"/console/api/apps/imports/{import_id}/confirm",
        )
        if status != 200:
            print(f"ERROR confirmando import: HTTP {status} {body}", file=sys.stderr)
            sys.exit(1)
        print(f"      status={body.get('status')}")
    else:
        print("[3/4] No requiere confirmacion, se salta.")

    print(f"[4/4] Publicando app_id={app_id}...")
    status, body = request(
        opener, cookie_jar, base_url, "POST", f"/console/api/apps/{app_id}/workflows/publish",
        payload={},
    )
    if status not in (200, 201):
        print(f"ERROR publicando: HTTP {status} {body}", file=sys.stderr)
        sys.exit(1)
    print("      OK, version publicada.")
    print("\nListo. Corre test_chatflow.py contra este mismo DIFY_BASE_URL (+ /v1) para verificar.")


if __name__ == "__main__":
    main()
