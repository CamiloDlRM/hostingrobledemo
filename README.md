# GitHub Deployment Automation

Aplicación fullstack que automatiza deployments mediante fork de repositorios a una organización y configuración automática de GitHub Actions workflows con cron scheduling.

## Stack Tecnológico

- **Backend:** FastAPI + PostgreSQL
- **Frontend:** React + Vite
- **CI/CD:** GitHub Actions (con cron scheduling)
- **Infraestructura:** Docker + Nginx
- **Gestión de Repos:** Fork automático a organización

## Nuevo Flujo de Trabajo

### ¿Qué hace esta aplicación?

1. **Usuario ingresa URL de repositorio:** El usuario proporciona la URL de cualquier repositorio público de GitHub
2. **Fork automático:** La aplicación hace fork del repositorio a una organización configurada
3. **Setup de workflow:** Se agrega automáticamente un workflow de GitHub Actions con:
   - Trigger on push (deployment automático al hacer push)
   - Cron schedule (deployment programado, ej: cada 6 horas)
   - Manual trigger (workflow_dispatch para ejecución manual)
4. **Deployment:** El workflow construye la imagen Docker, la sube a Docker Hub y la despliega en el servidor

### Cambios vs Versión Anterior

- ❌ **Eliminado:** GitHub App OAuth (ya no se requiere autenticación de usuario con GitHub)
- ✅ **Nuevo:** Fork automático a organización usando token de org
- ✅ **Nuevo:** Workflow con cron schedule automático
- ✅ **Simplificado:** Solo se ingresa URL del repo, todo lo demás es automático

## Configuración Inicial

### 1. Crear Token de GitHub para Organización

Necesitas un Personal Access Token (PAT) o GitHub App token con permisos para:
- Hacer fork de repositorios a la organización
- Crear/modificar archivos (para agregar workflows)

**Opción A: Personal Access Token (Classic)**
1. Ve a GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token con scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
   - `admin:org` (si necesitas crear repos en la org)
3. Guarda el token generado

**Opción B: GitHub App (Recomendado para producción)**
1. Crea una GitHub App en tu organización
2. Permisos necesarios:
   - Repository: Contents (Read & Write), Workflows (Read & Write)
   - Organization: Read & Write (para hacer fork)
3. Instala la app en tu organización
4. Genera un installation token

### 2. Configurar Variables de Entorno

```bash
cd backend
cp .env.example .env
```

Edita `.env` con tus valores:

```env
# Database
DATABASE_URL=postgresql://deployuser:deploypass@db:5432/deployments_db

# GitHub Organization (NUEVO)
GITHUB_ORG_NAME=tu-organizacion        # Nombre de tu org en GitHub
GITHUB_ORG_TOKEN=ghp_xxxxxxxxxxxxx     # Token con permisos de fork
GITHUB_WEBHOOK_SECRET=tu-webhook-secret

# Docker Hub (para subir imágenes)
DOCKER_HUB_USERNAME=tu-usuario
DOCKER_HUB_PASSWORD=tu-password
DOCKER_HUB_REPO=tu-usuario/deployments

# Server SSH (para deployment)
SERVER_SSH_HOST=tu-servidor.com
SERVER_SSH_USER=deploy
SERVER_SSH_KEY_PATH=/path/to/ssh-key

# Domain
DOMAIN_BASE=hostingroble.com

# App URLs
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173

# Security
SECRET_KEY=tu-secret-key-cambiar-en-produccion
```

### 3. Configurar Secrets en GitHub Organization

Para que los workflows funcionen, necesitas configurar secrets a nivel de organización:

1. Ve a tu Organización → Settings → Secrets and variables → Actions
2. Crea los siguientes secrets:
   - `DOCKER_HUB_USERNAME`: Tu usuario de Docker Hub
   - `DOCKER_HUB_PASSWORD`: Tu contraseña o token de Docker Hub
   - Otros secrets necesarios para tus deployments

### 4. Configurar Webhooks (CRÍTICO para estado en tiempo real)

Los webhooks permiten que la aplicación sepa cuándo los workflows terminan.

**Configurar a nivel de organización:**

1. Ve a: `https://github.com/organizations/TU-ORG/settings/hooks`
2. Click "Add webhook"
3. Configurar:
   ```
   Payload URL: https://tu-dominio.com/api/webhooks/github
   Content type: application/json
   Secret: [mismo que GITHUB_WEBHOOK_SECRET en .env]
   ```
4. Seleccionar eventos:
   - ☑️ **Workflow runs** (CRÍTICO)
   - ☑️ **Pushes** (Recomendado)
5. Activar webhook y guardar

Ver [WEBHOOKS_CONFIG.md](./WEBHOOKS_CONFIG.md) para configuración detallada.

## Instalación y Ejecución

### Desarrollo Local con Docker Compose (Recomendado)

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Rebuild si cambias configuración
docker-compose up -d --build
```

**Nota Importante sobre Frontend:**
Las variables de entorno del frontend (como `VITE_BACKEND_URL`) se necesitan en **build time**.
Ver [FRONTEND_BUILD_EXPLAINED.md](./FRONTEND_BUILD_EXPLAINED.md) para más detalles.

### Producción

```bash
# Build e iniciar en modo producción
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### Desarrollo Manual (Sin Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Acceder a la Aplicación

- **Frontend:** http://localhost:5173
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## Flujo de Uso

### 1. Agregar Repositorio

1. En el frontend, click en "New Deployment"
2. Ingresa:
   - URL del repositorio (ej: `https://github.com/facebook/react`)
   - Branch a monitorear (default: `main`)
   - Tecnología (React+Vite, FastAPI, NestJS)
   - Cron schedule (default: `0 */6 * * *` = cada 6 horas)
3. Click en "Fork & Setup Workflow"

### 2. Proceso Automático

La aplicación automáticamente:
1. ✅ Verifica que el repositorio existe
2. ✅ Hace fork a tu organización
3. ✅ Genera workflow con:
   - Build de imagen Docker
   - Push a Docker Hub
   - Deployment al servidor
   - Triggers: push, cron schedule, manual
4. ✅ Hace commit del workflow al repo forked
5. ✅ Guarda la información en la base de datos

### 3. Resultado

- **Repositorio forked** en tu organización
- **Workflow automático** con 3 triggers:
  - Push al branch configurado
  - Cron schedule (ej: cada 6 horas)
  - Manual (workflow_dispatch)
- **Visible en el dashboard** con link al fork

## Estructura del Workflow Generado

El workflow generado incluye:

```yaml
name: Deploy App

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 */6 * * *'  # Cada 6 horas
  workflow_dispatch:  # Ejecución manual

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - Checkout code
      - Setup Docker Buildx
      - Login to Docker Hub
      - Build Docker image
      - Push Docker image
      - Deploy to server
```

## API Endpoints

**Nota:** Todos los endpoints comienzan con el prefijo `/api`

### Usuarios
- `POST /api/users` - Crear usuario
- `GET /api/users/{user_id}` - Obtener usuario

### Repositorios
- `POST /api/repos?user_id={id}` - Fork repo y setup workflow
- `GET /api/repos/user/{user_id}` - Listar repos del usuario
- `DELETE /api/repos/{repo_id}?user_id={id}` - Eliminar repo (solo BD, no GitHub)

### Deployments
- `POST /api/repos/{id}/deploy` - Crear deployment
- `GET /api/deployments/{id}` - Ver deployment
- `GET /api/deployments/{id}/logs` - Ver logs
- `POST /api/webhooks/github` - Recibir webhooks

## Modelo de Datos

### Tabla `users`
- `id` (UUID)
- `username` (string, único)
- `email` (string, opcional)

### Tabla `repos`
- `id` (UUID)
- `user_id` (FK a users)
- `original_owner` (owner del repo original)
- `original_repo_name` (nombre del repo original)
- `original_repo_url` (URL completa del repo original)
- `forked_repo_name` (nombre del fork en la org)
- `forked_repo_url` (URL del fork)
- `branch` (branch a monitorear)
- `technology` (react-vite, fastapi, nestjs)
- `cron_schedule` (expresión cron)

## Migración desde Versión Anterior

Si vienes de la versión con GitHub App OAuth:

### Cambios en Base de Datos

**Tabla `users`:**
- ❌ Eliminado: `github_user_id`
- ❌ Eliminado: `github_token`

**Tabla `repos`:**
- ❌ Eliminado: `repo_owner`, `repo_name`, `repo_url`
- ✅ Agregado: `original_owner`, `original_repo_name`, `original_repo_url`
- ✅ Agregado: `forked_repo_name`, `forked_repo_url`
- ✅ Agregado: `cron_schedule`

### Script de Migración

Si tienes datos existentes, ejecuta:

```sql
-- Respaldar datos existentes
CREATE TABLE repos_backup AS SELECT * FROM repos;
CREATE TABLE users_backup AS SELECT * FROM users;

-- Eliminar tablas
DROP TABLE IF EXISTS deployments CASCADE;
DROP TABLE IF EXISTS settings CASCADE;
DROP TABLE IF EXISTS repos CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Reiniciar la aplicación para recrear tablas con nueva estructura
```

## Expresiones Cron

Ejemplos de cron schedules:

- `0 */6 * * *` - Cada 6 horas
- `0 0 * * *` - Diariamente a medianoche
- `0 */12 * * *` - Cada 12 horas
- `0 0 * * 1` - Cada lunes a medianoche
- `0 0 1 * *` - Primer día de cada mes

## Troubleshooting

### Backend no inicia
```bash
docker-compose logs backend

# Verificar que las variables están configuradas
docker-compose exec backend env | grep GITHUB_ORG
```

### Frontend no conecta al backend
```bash
# Verificar la variable de entorno
docker-compose logs frontend

# Rebuild el frontend con las variables correctas
docker-compose up -d --build frontend
```

### Fork falla
- Verifica que el token tenga permisos de fork
- Verifica que la organización exista
- Verifica que el token tenga acceso a la organización

### Workflow no se crea
- Verifica permisos de `workflow` en el token
- Verifica que el branch especificado existe en el repo

### Webhooks no funcionan
- Verifica URL pública configurada
- Verifica que el webhook secret coincida

### "import.meta.env is undefined"
El frontend necesita rebuild. Las variables se inyectan en build time:
```bash
docker-compose down
docker-compose up -d --build
```

Ver [FRONTEND_BUILD_EXPLAINED.md](./FRONTEND_BUILD_EXPLAINED.md) para más detalles.

## Notas de Desarrollo

### La app HACE:
- ✅ Fork de repos a organización
- ✅ Generación automática de workflows con cron
- ✅ Commit de workflows al repo forkeado
- ✅ Tracking de repos y deployments
- ✅ Recepción de webhooks
- ✅ Logs y estado en tiempo real

### Usuario MANEJA:
- ⚠️ Configuración de secrets en GitHub Organization
- ⚠️ Configuración de servidor SSH para deployment
- ⚠️ Configuración de Nginx/proxy reverso
- ⚠️ Asignación de puertos para containers

## Licencia

MIT
