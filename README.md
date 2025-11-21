# WebService

A small Flask-based example Web Service that manages "specializations" and "course items" in-memory. Includes Docker Compose files for containerized runs and a debug compose configuration.

**Features**
- **API**: CRUD endpoints for `specialization` and `course_item`.
- **Lightweight**: Uses in-memory data in `db.py` for easy testing and learning.
- **Docker**: `docker-compose.yml` and `docker-compose.debug.yml` included.

**Prerequisites**
- **Python**: 3.8+ recommended.
- **Docker** (optional): for running the service in containers.
- **Pip dependencies**: listed in `requirements.txt`.

**Install**
- Create and activate a virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Run locally**
- Start the app in development mode:

```powershell
python app.py
```

- By default the Flask app starts with `debug=True` and binds to `127.0.0.1:5000`.

**Run with Docker Compose**
- Build and start with Docker Compose:

```powershell
docker-compose up --build
```

- To use the debug compose configuration:

```powershell
docker-compose -f docker-compose.debug.yml up --build
```

**API Endpoints (overview)**
- `GET /specialization` — list specializations
- `POST /specialization` — create a specialization (JSON body: `{ "name": "..." }`)
- `GET /specialization/<id>` — get by ID
- `PUT /specialization/<id>` — update (JSON body: `{ "name": "..." }`)
- `DELETE /specialization/<id>` — delete

- `GET /course_item` — list course items
- `POST /course_item` — create a course item (JSON body: `{ "name": "...", "type": "...", "specialization_id": "..." }`)
- `GET /course_item/<id>` — get by ID
- `PUT /course_item/<id>` — update (JSON body: `{ "name": "...", "type": "..." }`)
- `DELETE /course_item/<id>` — delete

Example `curl` (create specialization):

```bash
curl -X POST http://127.0.0.1:5000/specialization \
  -H "Content-Type: application/json" \
  -d '{"name":"Data Science"}'
```

**Project Structure**
- `app.py` — Flask application and route definitions.
- `db.py` — in-memory storage (`specializations`, `course_items`).
- `requirements.txt` — Python dependencies.
- `docker-compose.yml` — production/dev compose file.
- `docker-compose.debug.yml` — compose config for debugging.

**Environment / Configuration**
- The project is simple and reads no required environment variables by default. If you add a `.env`, `python-dotenv` is available to load it.

