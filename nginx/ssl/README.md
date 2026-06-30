# SSL Certificates

Los certificados SSL deben colocarse aquí:

- `cert.pem` - Certificado (fullchain.pem)
- `key.pem` - Clave privada (privkey.pem)

## Generar con Let's Encrypt

```bash
certbot certonly --standalone \
  -d socios.cobreloa.cl \
  -d api.cobreloa.cl

cp /etc/letsencrypt/live/socios.cobreloa.cl/fullchain.pem cert.pem
cp /etc/letsencrypt/live/socios.cobreloa.cl/privkey.pem key.pem
```
