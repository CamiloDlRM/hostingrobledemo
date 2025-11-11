# 🔄 Cambio de Prefijo: Todos los Endpoints con `/api`

## 📋 Resumen del Cambio

Todos los endpoints de la API ahora comienzan con el prefijo `/api`.

### Antes
```
http://localhost:8000/users
http://localhost:8000/repos
http://localhost:8000/deployments/{id}
http://localhost:8000/webhooks/github
```

### Ahora
```
http://localhost:8000/api/users
http://localhost:8000/api/repos
http://localhost:8000/api/deployments/{id}
http://localhost:8000/api/webhooks/github
```

---

## 🎯 ¿Por Qué Este Cambio?

1. **Organización:** Separar claramente los endpoints de API de otros recursos
2. **Convención:** Práctica estándar en APIs REST
3. **Versionado futuro:** Permite agregar `/api/v1`, `/api/v2` si es necesario
4. **Proxy reverso:** Facilita configuración de Nginx/proxy para routear solo `/api/*`

---

## 📝 Archivos Modificados

### Backend

**`backend/app/main.py`**
- Agregado `prefix="/api"` a todos los `app.include_router()`
```python
app.include_router(
    users_router,
    prefix="/api",
    tags=["Users"]
)
```

**`backend/app/api/routes/deployments.py`**
- Actualizada documentación de endpoints

### Frontend

**Archivos de API (`frontend/src/api/`):**
- `repos.js` - Actualizado para usar `/api`
- `deployments.js` - Actualizado para usar `/api`
- `workflows.js` - Actualizado para usar `/api`

**Componentes:**
- `Dashboard.jsx` - Actualizado fetch call
- `RepoConfig.jsx` - Actualizado fetch calls
- `DeployStatus.jsx` - Actualizado fetch call
- `LogsViewer.jsx` - Actualizado fetch call

### Documentación

**`README.md`**
- Sección de API Endpoints actualizada
- Configuración de webhooks actualizada

---

## ✅ Lista de Endpoints Actualizados

### Usuarios
- `POST /api/users` - Crear usuario
- `GET /api/users/{user_id}` - Obtener usuario

### Repositorios
- `POST /api/repos?user_id={id}` - Fork repo y setup workflow
- `GET /api/repos/user/{user_id}` - Listar repos del usuario
- `GET /api/repos/{repo_id}/settings` - Obtener settings
- `POST /api/repos/{repo_id}/settings` - Guardar settings
- `DELETE /api/repos/{repo_id}?user_id={id}` - Eliminar repo

### Deployments
- `POST /api/repos/{id}/deploy` - Crear deployment
- `GET /api/repos/{repo_id}/deployments` - Listar deployments
- `GET /api/deployments/{id}` - Ver deployment
- `GET /api/deployments/{id}/logs` - Ver logs

### Webhooks
- `POST /api/webhooks/github` - Recibir webhooks de GitHub

---

## 🔧 Configuración de Webhooks en GitHub

**IMPORTANTE:** Actualiza la URL del webhook en tu organización de GitHub.

### Antes
```
Payload URL: https://tu-dominio.com/webhooks/github
```

### Ahora
```
Payload URL: https://tu-dominio.com/api/webhooks/github
```

### Pasos:
1. Ve a: `https://github.com/organizations/TU-ORG/settings/hooks`
2. Edita el webhook existente
3. Cambia Payload URL a: `https://tu-dominio.com/api/webhooks/github`
4. Guarda cambios

---

## 🧪 Verificación

### 1. Verificar Backend

```bash
# Backend debe estar corriendo
docker-compose up -d

# Probar endpoint de health
curl http://localhost:8000/health

# Probar endpoint de API
curl http://localhost:8000/api/users
```

### 2. Verificar Frontend

El frontend automáticamente usa las nuevas rutas si está actualizado.

```bash
# Rebuild frontend con las nuevas rutas
docker-compose up -d --build frontend
```

### 3. Verificar Webhooks

En GitHub → Organization → Settings → Webhooks:
- Verifica que la URL sea: `https://tu-dominio.com/api/webhooks/github`
- Haz click en "Recent Deliveries"
- Redeliver un webhook de prueba
- Verifica que el status sea 200 OK

---

## 🐛 Troubleshooting

### Error 404 en llamadas de API

**Síntoma:** Frontend muestra errores 404 al cargar datos

**Causa:** Frontend no actualizado con nuevas rutas

**Solución:**
```bash
# Rebuild frontend
docker-compose up -d --build frontend

# O si usas npm directamente
cd frontend
npm run dev
```

### Webhooks retornan 404

**Síntoma:** GitHub muestra deliveries con status 404

**Causa:** URL del webhook no actualizada

**Solución:**
1. Ir a GitHub → Organization → Settings → Webhooks
2. Editar webhook
3. Cambiar URL a: `https://tu-dominio.com/api/webhooks/github`
4. Guardar

### API Docs no actualizada

**Síntoma:** Swagger/OpenAPI docs muestra rutas sin `/api`

**Solución:** Esto es normal. FastAPI Swagger docs muestra las rutas relativas al router, no incluye el prefijo global. Las rutas reales tienen el prefijo `/api`.

---

## 📚 Variables de Entorno

No hay cambios en variables de entorno. `BACKEND_URL` sigue siendo:
```env
BACKEND_URL=http://localhost:8000
```

El frontend automáticamente agrega `/api` al hacer las llamadas:
```javascript
const API_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
const API_BASE = `${API_URL}/api`;  // ← Agrega /api automáticamente
```

---

## ✨ Beneficios

1. ✅ **Claridad:** URLs más descriptivas
2. ✅ **Estándar:** Sigue convenciones REST
3. ✅ **Escalabilidad:** Permite agregar otras rutas no-API (`/health`, `/docs`, etc.)
4. ✅ **Proxy:** Más fácil configurar reverse proxy
5. ✅ **Versionado:** Base para futuras versiones (`/api/v2`)

---

## 🔄 Rollback (Si es necesario)

Si necesitas revertir este cambio:

1. **Backend:** Remover `prefix="/api"` en `backend/app/main.py`
2. **Frontend:** Cambiar `${API_URL}/api` a `${API_URL}` en archivos de API
3. **GitHub Webhooks:** Actualizar URL a `https://tu-dominio.com/webhooks/github`
4. **Rebuild:** `docker-compose up -d --build`

---

## 📞 Health Check & Docs

Estos endpoints NO tienen prefijo `/api`:

- ✅ `GET /` - Root endpoint (info de la API)
- ✅ `GET /health` - Health check
- ✅ `GET /docs` - Swagger/OpenAPI docs (FastAPI automático)
- ✅ `GET /redoc` - ReDoc docs (FastAPI automático)

Todos los demás endpoints de negocio tienen el prefijo `/api`.

---

## 🎯 Checklist de Migración

- [x] Backend: Agregar prefix en main.py
- [x] Frontend: Actualizar archivos en src/api/
- [x] Frontend: Actualizar componentes (Dashboard, RepoConfig, etc.)
- [x] Documentación: Actualizar README.md
- [x] Documentación: Crear API_PREFIX_CHANGE.md
- [ ] GitHub Webhooks: Actualizar URL en organización
- [ ] Testing: Verificar que todos los endpoints funcionen
- [ ] Deployment: Aplicar cambios en producción

---

¿Preguntas? Ver [README.md](./README.md) para documentación completa del proyecto.
