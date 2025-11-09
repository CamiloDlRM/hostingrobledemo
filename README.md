# GitHub Deployment Automation

Aplicación fullstack que automatiza deployments usando GitHub Apps y GitHub Actions.

## Stack Tecnológico

- Backend: FastAPI + PostgreSQL
- Frontend: React + Vite
- CI/CD: GitHub Actions
- Infraestructura: Docker + Nginx
- Autenticación: GitHub App OAuth

## Configuración Inicial

### 1. Crear GitHub App

1. Ve a GitHub Settings → Developer settings → GitHub Apps → New GitHub App
2. Configura la app con:
   - Homepage URL: http://localhost:8000
   - Callback URL: http://localhost:8000/auth/github/callback
   - Webhook URL: https://tu-dominio.com/webhooks/github
3. Permisos necesarios:
   - Repository: Contents (Read & Write), Workflows (Read & Write)
   - User: Email (Read-only)
4. Subscribe to events: Push, Workflow run
5. Guarda: App ID, Client ID, Client Secret, Private key

### 2. Configurar Variables de Entorno

bash
cd backend
cp .env.example .env

Edita .env con tus valores reales.

### 3. Configurar Webhooks

IMPORTANTE: Los webhooks son ESENCIALES para:
- Actualizar estado de deployments
- Descargar logs de GitHub Actions
- Mostrar errores

Webhook URL: https://tu-dominio.com/webhooks/github
Eventos: push, workflow_run

## Instalación y Ejecución

### Usando Docker Compose

bash
cd mi-app
docker-compose up -d

Acceder a:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Flujo de Uso

1. Autenticación: Conectar con GitHub
2. Configurar Repo: URL, tecnología, branch
3. Variables: Env vars, build args, puerto
4. Deploy: Automático vía GitHub Actions
5. Monitorear: Ver estado y logs en tiempo real

## Estados de Deployment

- pending: Esperando ejecución
- building: Construyendo imagen
- deploying: Desplegando container
- success: Exitoso
- failed: Falló

## API Endpoints

- POST /auth/github - Iniciar OAuth
- GET /auth/github/callback - Callback OAuth
- POST /repos - Guardar repo
- POST /repos/{id}/settings - Guardar configuración
- POST /repos/{id}/deploy - Crear deployment
- GET /deployments/{id} - Ver deployment
- GET /deployments/{id}/logs - Ver logs
- POST /webhooks/github - Recibir webhooks

## Notas Importantes

La app HACE:
- OAuth con GitHub
- Generar workflows básicos
- Recibir webhooks
- Mostrar logs y estado

Usuario MANEJA:
- Asignación de puertos
- Configuración de Nginx
- Templates completos de workflows

## Troubleshooting

Backend no inicia:
bash
docker-compose logs backend

Webhooks no funcionan:
- Verificar URL pública
- Verificar secret coincide

## Licencia

MIT
