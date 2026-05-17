# TintWrap Backend

API base en FastAPI con CRUD para `blogs`, `sliders`, `services` y `service_galleries`.

## Instalar

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Base de datos

Por defecto conecta a MySQL en localhost, usuario `root`, sin contraseña, base `tintwrap`:

```text
mysql+pymysql://root@localhost/tintwrap
```

Para cambiar la conexion, define la variable de entorno `DATABASE_URL`.

## Ejecutar

```bash
uvicorn main:app --reload
```

## URLs

- Base API: `http://127.0.0.1:8030/api/`
- Documentacion: `http://127.0.0.1:8030/api/docs`

## Endpoints

- `GET /api/blogs/`
- `GET /api/blogs/{blog_id}`
- `POST /api/blogs/`
- `PUT /api/blogs/{blog_id}`
- `PATCH /api/blogs/{blog_id}`
- `DELETE /api/blogs/{blog_id}`
- `GET /api/sliders/`
- `GET /api/sliders/{slider_id}`
- `POST /api/sliders/`
- `PUT /api/sliders/{slider_id}`
- `PATCH /api/sliders/{slider_id}`
- `DELETE /api/sliders/{slider_id}`
- `GET /api/services/`
- `GET /api/services/{service_id}`
- `POST /api/services/`
- `PUT /api/services/{service_id}`
- `PATCH /api/services/{service_id}`
- `DELETE /api/services/{service_id}`
- `GET /api/service-galleries/`
- `GET /api/service-galleries/service/{service_id}`
- `GET /api/service-galleries/{gallery_id}`
- `POST /api/service-galleries/`
- `PUT /api/service-galleries/{gallery_id}`
- `PATCH /api/service-galleries/{gallery_id}`
- `DELETE /api/service-galleries/{gallery_id}`
