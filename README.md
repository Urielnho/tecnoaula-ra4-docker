# TecnoAula con Docker Compose

Resultado de Aprendizaje Unidad 4. Este proyecto adapta TecnoAula de las unidades 2 y 3: React con Vite, Django con DRF y JWT, y MySQL persistente.

## Requisitos

Docker Desktop instalado y en ejecución, con contenedores Linux y Docker Compose. No hace falta instalar Python, Node ni MySQL en la computadora. La primera construcción necesita Internet.

## Preparación inicial

1. Clonar el repositorio o descargar el ZIP y extraerlo.
2. Abrir una terminal en la carpeta que contiene `docker-compose.yml`.
3. Copiar `.env.example` como `.env`:

```powershell
Copy-Item .env.example .env
```

En Linux o macOS: `cp .env.example .env`.

4. Editar `.env` y reemplazar los valores de `MYSQL_PASSWORD`, `MYSQL_ROOT_PASSWORD` y `DJANGO_SECRET_KEY` por claves propias, distintas y largas. No cambiar las claves después de inicializar la base sin coordinar su actualización en MySQL. `.env` está excluido de Git; se publica únicamente el ejemplo sin secretos reales.

## Arrancar los tres servicios

```sh
docker compose up --build -d --wait
```

Compose construye las imágenes de Django y React, inicia MySQL y ejecuta las migraciones automáticamente. Los controles de salud hacen que Django espere a MySQL y que React espere a Django. En los siguientes arranques, si el código no cambió, se puede usar `docker compose up -d --wait`.

- Frontend: http://localhost:5173
- Swagger del backend: http://localhost:8000 (redirige a `/swagger/`).
- Salud de Django y MySQL: http://localhost:8000/health/

Crear una cuenta desde **Crear cuenta** en React e iniciar sesión. No hay cuentas ni datos personales precargados.

## Organización

- `frontend/Dockerfile`: Node 24 Alpine, `npm ci` y Vite escuchando en `0.0.0.0:5173`.
- `backend/Dockerfile`: Python 3.13, herramientas Linux para compilar mysqlclient y requisitos de Django.
- `backend/entrypoint.sh`: migraciones y servidor Django en `0.0.0.0:8000`.
- `docker-compose.yml`: servicios `db`, `backend` y `frontend`, red compartida y volumen `mysql_data`.
- `.dockerignore` en la raíz y en ambos servicios: excluye entornos, secretos, cachés y dependencias locales.

El backend usa `MYSQL_HOST=db` para conectarse al servicio MySQL por la red de Docker. React se ejecuta en el navegador y usa `http://localhost:8000` como URL de la API. CORS permite los orígenes locales de React en el puerto 5173. `DJANGO_ALLOWED_HOSTS=*` cumple la configuración local del manual. Los puertos publicados se enlazan solo a `127.0.0.1` y MySQL no publica ningún puerto en Windows; no entra en conflicto con el MySQL instalado.

## Comprobar los servicios

```sh
docker ps
docker compose ps
docker compose logs --tail 30 backend
docker compose exec backend python manage.py check
docker compose exec backend python manage.py makemigrations --check --dry-run
docker compose exec frontend npm run build
```

## Demostrar persistencia

1. Registrar un usuario desde React y entrar al dashboard.
2. Consultarlo directamente en MySQL a través del ORM de Django; sustituir el correo del ejemplo por el utilizado:

```sh
docker compose exec backend python verificar_persistencia.py correo@ejemplo.com
```

La consulta muestra motor, ID, correo y matrícula. Nunca muestra contraseña, hash ni tokens.

3. Apagar y recrear los contenedores:

```sh
docker compose down
docker compose up -d --wait
```

4. Recargar React y volver a iniciar sesión si el token de acceso expiró. Repetir la consulta anterior: el usuario debe conservar el mismo ID y datos. El volumen real se llama `tecnoaula-ra4_mysql_data`.

`docker compose down` elimina los contenedores y la red, pero conserva el volumen. No usar `docker compose down -v` si se desea conservar los datos.

## Alcance

Entorno educativo local. Se usan Vite y el servidor de desarrollo de Django para seguir el manual. Se conservan las funciones existentes de TecnoAula: registro, login JWT, perfil, catálogo y consultas externas REST y SOAP. Si un proveedor externo no está disponible, su tarjeta informa el error real.

Proyecto base: https://github.com/Urielnho/tecnoaula-ra-unidad2-3
