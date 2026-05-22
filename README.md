Proyecto: API Flask + Frontend para gestionar lugares y calcular rutas (A* / UCS)

Descripción
-
Este repositorio contiene un servidor Flask que expone una API para gestionar
un grafo de lugares (nodos con latitud/longitud) y conexiones (aristas con costo),
además de un frontend web simple para añadir lugares/aristas y calcular rutas.

Estructura principal
-
- `app.py` — servidor Flask que implementa la API y sirve el frontend.
- `Carretera_A.py` — lógica de distancia y algoritmo A* (reutilizable).
- `data.json` — archivo de persistencia generado en tiempo de ejecución (si existe).
- `templates/index.html` — frontend HTML.
- `static/app.js`, `static/style.css` — assets del frontend.
- `requirements.txt` — dependencias Python.

Instalación y ejecución (Windows PowerShell)
-
1. Crear entorno e instalar dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
```

2. Levantar servidor:

```powershell
python app.py
```

3. Abrir el frontend en el navegador:

```
http://127.0.0.1:5000
```

API
-
Base URL: `http://127.0.0.1:5000`

1) Obtener datos completos
- Endpoint: `GET /api/data`
- Descripción: Devuelve el estado actual con `conexiones` y `coord`.
- Respuesta ejemplo:

```json
{
	"conexiones": { "A": {"B": 120}, "B": {} },
	"coord": { "A": [19.0, -99.0], "B": [20.0, -100.0] }
}
```

2) Agregar lugar (nodo)
- Endpoint: `POST /api/place`
- Payload (JSON): `{ "name": "Nombre", "lat": 19.0, "lon": -99.0 }`
- Respuestas:
	- `200 OK` -> `{ "ok": true, "place": "Nombre" }`
	- `400 Bad Request` -> `{ "error": "faltan campos" }` u otros mensajes de validación

3) Agregar conexión (arista)
- Endpoint: `POST /api/edge`
- Payload (JSON): `{ "from": "A", "to": "B", "cost": 120 }`
- Respuestas:
	- `200 OK` -> `{ "ok": true }`
	- `400 Bad Request` -> `{ "error": "faltan campos" }` u otros mensajes

4) Calcular ruta
- Endpoint: `POST /api/route`
- Payload (JSON): `{ "start": "A", "goal": "B" }`
- Respuesta ejemplo cuando existe ruta:

```json
{ "route": ["A","C","B"], "cost": 523.5 }
```

- Si no hay ruta disponible: `{ "route": null, "cost": null }`

Ejemplos de uso (PowerShell)
-
Agregar lugar:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5000/api/place -Method Post -ContentType "application/json" -Body ('{"name":"Prueba","lat":19.0,"lon":-99.0}')
```

Agregar arista:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5000/api/edge -Method Post -ContentType "application/json" -Body ('{"from":"Prueba","to":"CDMX","cost":120}')
```

Calcular ruta:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5000/api/route -Method Post -ContentType "application/json" -Body ('{"start":"Prueba","goal":"MTY"}')
```

Ejemplos con `curl` (Linux/macOS / Git Bash en Windows)
-
Agregar lugar:

```bash
curl -X POST http://127.0.0.1:5000/api/place -H "Content-Type: application/json" -d '{"name":"Prueba","lat":19.0,"lon":-99.0}'
```

Formateo de `data.json`
-
Al guardar, `coord` se serializa como listas y `conexiones` como objetos JSON. Ejemplo:

```json
{
	"conexiones": { "A": {"B": 120}, "B": {} },
	"coord": { "A": [19.0, -99.0], "B": [20.0, -100.0] }
}
```

Notas de implementación
-
- El algoritmo de ruta y la función de distancia están en `Carretera_A.py` (funciones `a_star`, `geodist`, `add_place`).
- Cambios realizados por la API se persisten en `data.json` inmediatamente.
- El frontend en `templates/index.html` y `static/app.js` consume los endpoints anteriores.

Mejoras sugeridas (opcionales)
-
- Validar nombres duplicados al crear lugares (actualmente `add_place` sobrescribe si existe).
- Endpoints para eliminar/editar lugares y aristas.
- Añadir CORS si piensas consumir la API desde otro dominio.
- Preparar `Dockerfile` para desplegar el servicio fácilmente.

Contacto
-
Si quieres que implemente alguna mejora (validaciones, eliminación, Docker), dime cuál y la hago.
