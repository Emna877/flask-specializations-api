# Flask Specializations API - Complete Setup Guide

This guide documents all the steps taken to create and configure this Flask REST API project from scratch.

## Table of Contents
1. [Project Initialization](#project-initialization)
2. [Core Application Setup](#core-application-setup)
3. [Database Configuration](#database-configuration)
4. [API Resources & Schemas](#api-resources--schemas)
5. [Docker Configuration](#docker-configuration)
6. [Project Documentation](#project-documentation)
7. [Bug Fixes & Refinements](#bug-fixes--refinements)
8. [Testing & Verification](#testing--verification)

---

## 1. Project Initialization

### Create Project Directory
```powershell
mkdir WebService
cd WebService
```

### Initialize Git Repository
```powershell
git init
git remote add origin https://github.com/Emna877/flask-specializations-api.git
```

### Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Create Initial Dependencies File
Create `requirements.txt`:
```
flask
flask-smorest
flask-sqlalchemy
marshmallow
python-dotenv
```

### Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 2. Core Application Setup

### Create Main Application File (`app.py`)

```python
from flask import Flask
from flask_smorest import Api
import os
from db import db
from resources.course_item import blp as CourseItemBlueprint
from resources.specialization import blp as SpecializationBlueprint

def create_app(db_url=None):
    app = Flask(__name__)
    
    # API Configuration
    app.config["API_TITLE"] = "TBS Web Services API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    
    # Database Configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    
    # Initialize Database
    db.init_app(app)
    
    # Create tables in app context
    with app.app_context():
        db.create_all()
    
    # Initialize API and register blueprints
    api = Api(app)
    api.register_blueprint(SpecializationBlueprint)
    api.register_blueprint(CourseItemBlueprint)

    return app

# Create default app instance
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```

**Key Configuration Points:**
- Flask-Smorest for automatic OpenAPI/Swagger documentation
- SQLite database with configurable URI
- Blueprints for modular API structure
- Database initialization in app context (not on every request)

---

## 3. Database Configuration

### Create Database Module (`db.py`)

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SpecializationModel(db.Model):
    __tablename__ = "specializations"
    
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    
    course_items = db.relationship("CourseItemModel", back_populates="specialization", lazy="dynamic", cascade="all, delete-orphan")


class CourseItemModel(db.Model):
    __tablename__ = "course_items"
    
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    specialization_id = db.Column(db.String(32), db.ForeignKey("specializations.id"), nullable=False)
    
    specialization = db.relationship("SpecializationModel", back_populates="course_items")
```

**Database Design:**
- **Specializations**: Parent entity (e.g., "Data Science", "Web Development")
- **Course Items**: Child entity linked via foreign key
- UUID-based string IDs for flexibility
- Cascade delete: removing specialization deletes its course items

---

## 4. API Resources & Schemas

### Create Marshmallow Schemas (`schemas.py`)

```python
from marshmallow import Schema, fields

class PlainCourseItemSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    type = fields.Str(required=True)
    specialization_id = fields.Str(required=True)

class PlainSpecializationSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)

class CourseItemUpdateSchema(Schema):
    name = fields.Str()
    type = fields.Str()
    specialization_id = fields.Str()

class CourseItemSchema(PlainCourseItemSchema):
    specialization = fields.Nested(PlainSpecializationSchema, dump_only=True)

class SpecializationSchema(PlainSpecializationSchema):
    course_items = fields.List(fields.Nested(PlainCourseItemSchema), dump_only=True)

# Backwards compatibility instances
course_item_schema = CourseItemSchema()
specialization_schema = SpecializationSchema()
course_item_update_schema = CourseItemUpdateSchema()
```

**Schema Design Principles:**
- PascalCase class names following Python conventions
- `dump_only=True` for fields that shouldn't be set by clients (id, relationships)
- Separate update schemas with optional fields for partial updates
- Nested schemas for related entities in responses

### Create Specialization Resource (`resources/specialization.py`)

```python
import uuid
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import db, SpecializationModel
from schemas import SpecializationSchema

blp = Blueprint("specializations", __name__, description="Operations on specializations")

@blp.route("/specialization/<string:specialization_id>")
class Specialization(MethodView):
    @blp.response(200, SpecializationSchema)
    def get(self, specialization_id):
        specialization = SpecializationModel.query.get_or_404(specialization_id)
        return specialization
    
    @blp.arguments(SpecializationSchema)
    @blp.response(200, SpecializationSchema)
    def put(self, specialization_data, specialization_id):
        specialization = SpecializationModel.query.get_or_404(specialization_id)
        specialization.name = specialization_data["name"]
        db.session.commit()
        return specialization

    def delete(self, specialization_id):
        specialization = SpecializationModel.query.get_or_404(specialization_id)
        db.session.delete(specialization)
        db.session.commit()
        return {"message": "Specialization deleted."}

@blp.route("/specialization")
class SpecializationList(MethodView):
    @blp.response(200, SpecializationSchema(many=True))
    def get(self):
        return SpecializationModel.query.all()

    @blp.arguments(SpecializationSchema)
    @blp.response(201, SpecializationSchema)
    def post(self, specialization_data):
        # Check for duplicate
        if SpecializationModel.query.filter_by(name=specialization_data["name"]).first():
            abort(400, message="Specialization already exists.")

        specialization = SpecializationModel(
            id=uuid.uuid4().hex,
            **specialization_data
        )
        db.session.add(specialization)
        db.session.commit()
        return specialization
```

### Create Course Item Resource (`resources/course_item.py`)

```python
import uuid
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import CourseItemSchema, CourseItemUpdateSchema
from db import db, CourseItemModel, SpecializationModel

blp = Blueprint("Course_Items", __name__, description="Operations on course_items")

@blp.route("/course_item/<string:course_item_id>")
class Course_Item(MethodView):
    @blp.response(200, CourseItemSchema)
    def get(self, course_item_id):
        course_item = CourseItemModel.query.get_or_404(course_item_id)
        return course_item

    def delete(self, course_item_id):
        course_item = CourseItemModel.query.get_or_404(course_item_id)
        db.session.delete(course_item)
        db.session.commit()
        return {"message": "Course_item deleted."}

    @blp.arguments(CourseItemUpdateSchema)
    @blp.response(200, CourseItemUpdateSchema)
    def put(self, course_item_data, course_item_id):
        course_item = CourseItemModel.query.get_or_404(course_item_id)
        course_item.name = course_item_data.get("name", course_item.name)
        course_item.type = course_item_data.get("type", course_item.type)
        course_item.specialization_id = course_item_data.get("specialization_id", course_item.specialization_id)
        db.session.commit()
        return course_item

@blp.route("/course_item")
class Course_ItemList(MethodView):
    @blp.response(200, CourseItemSchema(many=True))
    def get(self):
        return CourseItemModel.query.all()
   
    @blp.arguments(CourseItemSchema)
    @blp.response(201, CourseItemSchema)
    def post(self, course_item_data):
        # Validate specialization exists
        specialization = SpecializationModel.query.get(course_item_data["specialization_id"])
        if not specialization:
            abort(404, message="Specialization not found.")
        
        # Check for duplicate
        existing = CourseItemModel.query.filter_by(
            name=course_item_data["name"],
            specialization_id=course_item_data["specialization_id"]
        ).first()
        
        if existing:
            abort(400, message="Course_Item already exists.")

        course_item = CourseItemModel(
            id=uuid.uuid4().hex,
            **course_item_data
        )
        db.session.add(course_item)
        db.session.commit()
        return course_item
```

**API Resource Patterns:**
- Class-based views with MethodView
- Automatic request/response validation via decorators
- UUID generation for new records
- Proper HTTP status codes (200, 201, 400, 404)
- Foreign key validation before creation

---

## 5. Docker Configuration

### Create Dockerfile

```dockerfile
FROM python:3.10

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
ENV FLASK_APP=app.py
CMD ["flask", "run", "--host", "0.0.0.0"]
```

**Key Dockerfile Elements:**
- Python 3.10 base image
- Requirements installed before copying app code (layer caching)
- `FLASK_APP` environment variable required for `flask run` command
- Port 5000 exposed for API access

### Create Docker Compose File (`docker-compose.yml`)

```yaml
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - .:/app
```

### Create Debug Compose File (`docker-compose.debug.yml`)

```yaml
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - .:/app
```

**Docker Usage:**
```powershell
# Build and run
docker-compose up --build

# Run debug version
docker-compose -f docker-compose.debug.yml up --build
```

---

## 6. Project Documentation

### Create README.md

Complete project documentation including:
- Project overview and features
- Prerequisites and system requirements
- Installation instructions for Windows/PowerShell
- Local development setup
- Docker deployment options
- API endpoint documentation with examples
- Project structure explanation
- Configuration guidance

### Create .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*.so

# Virtual environments
.venv/
venv/
env/
.flaskvenv/

# Database
*.sqlite3
instance/

# IDE
.vscode/
.idea/

# Environment
.env
.env.*

# Logs
*.log
logs/
```

---

## 7. Bug Fixes & Refinements

### Issues Identified and Fixed:

#### 1. Missing Dependencies
**Problem:** `flask-sqlalchemy` was used but not in `requirements.txt`  
**Fix:** Added to requirements file

#### 2. Database Initialization Performance Issue
**Problem:** `@app.before_request` ran `db.create_all()` on every request  
**Fix:** Moved to app context initialization:
```python
with app.app_context():
    db.create_all()
```

#### 3. Schema Import Errors
**Problem:** Resources imported schema instances but tried to call them as classes  
**Fix:** Updated all imports to use class names (PascalCase) and instantiate in decorators

#### 4. Docker Environment Variables
**Problem:** Container couldn't find Flask app  
**Fix:** Added `ENV FLASK_APP=app.py` to Dockerfile

#### 5. Schema Naming Conventions
**Problem:** Classes used lowercase_with_underscores  
**Fix:** Renamed to PascalCase following PEP 8

#### 6. Update Schema Incomplete
**Problem:** `CourseItemUpdateSchema` missing `specialization_id`  
**Fix:** Added field as optional for partial updates

#### 7. Docker Compose Filename
**Problem:** Named `Docker-compose.yml` (capital D)  
**Fix:** Renamed to `docker-compose.yml` (lowercase standard)

#### 8. Gitignore Gaps
**Problem:** `.flaskvenv` directory not excluded  
**Fix:** Added to `.gitignore`

---

## 8. Testing & Verification

### Start the Application

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the app
python app.py
```

### Access API Documentation
Open browser to: `http://localhost:5000/swagger`

### Test API Endpoints

#### Create Specialization
```bash
curl -X POST http://localhost:5000/specialization \
  -H "Content-Type: application/json" \
  -d '{"name":"Data Science"}'
```

#### Get All Specializations
```bash
curl http://localhost:5000/specialization
```

#### Create Course Item
```bash
curl -X POST http://localhost:5000/course_item \
  -H "Content-Type: application/json" \
  -d '{
    "name":"Python Programming",
    "type":"Course",
    "specialization_id":"<specialization_id>"
  }'
```

#### Get All Course Items
```bash
curl http://localhost:5000/course_item
```

#### Update Course Item
```bash
curl -X PUT http://localhost:5000/course_item/<course_item_id> \
  -H "Content-Type: application/json" \
  -d '{"name":"Advanced Python", "type":"Workshop"}'
```

#### Delete Course Item
```bash
curl -X DELETE http://localhost:5000/course_item/<course_item_id>
```

---

## Project Structure (Final)

```
WebService/
├── app.py                      # Main application factory
├── db.py                       # Database models
├── schemas.py                  # Marshmallow validation schemas
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker container definition
├── docker-compose.yml          # Docker Compose configuration
├── docker-compose.debug.yml    # Debug Docker Compose configuration
├── README.md                   # Project documentation
├── .gitignore                  # Git ignore rules
├── .logs                       # Development history
├── SETUP_GUIDE.md             # This setup guide
├── instance/
│   └── data.db                # SQLite database file
├── resources/
│   ├── specialization.py      # Specialization API endpoints
│   └── course_item.py         # Course item API endpoints
├── venv/                      # Virtual environment (not in git)
└── __pycache__/               # Python cache (not in git)
```

---

## Common Commands Reference

### Development
```powershell
# Activate environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Deactivate environment
deactivate
```

### Docker
```powershell
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# Stop containers
docker-compose down

# View logs
docker-compose logs -f
```

### Git
```powershell
# Check status
git status

# Stage changes
git add .

# Commit
git commit -m "Description"

# Push to remote
git push origin main
```

---

## Next Steps & Enhancements

### Recommended Improvements:
1. **Add Unit Tests** - Use pytest to test API endpoints
2. **Add Authentication** - Implement JWT or OAuth2
3. **Add Pagination** - For list endpoints with many records
4. **Add Filtering** - Query parameters for searching
5. **Add Rate Limiting** - Protect against abuse
6. **Switch to PostgreSQL** - For production deployments
7. **Add CI/CD Pipeline** - Automated testing and deployment
8. **Add Logging** - Structured logging for debugging
9. **Add Validation** - More comprehensive input validation
10. **Add API Versioning** - Support multiple API versions

---

## Troubleshooting

### Common Issues:

**Issue:** `ModuleNotFoundError: No module named 'flask_sqlalchemy'`  
**Solution:** Run `pip install -r requirements.txt`

**Issue:** `Could not locate a Flask application`  
**Solution:** Ensure `FLASK_APP=app.py` is set or run with `python app.py`

**Issue:** Database locked errors  
**Solution:** Close all connections or delete `instance/data.db` and restart

**Issue:** Port 5000 already in use  
**Solution:** Change port in `app.py`: `app.run(port=5001)` or kill process using port

---

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-Smorest Documentation](https://flask-smorest.readthedocs.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Marshmallow Documentation](https://marshmallow.readthedocs.io/)
- [Docker Documentation](https://docs.docker.com/)

---

**Project Status:** ✅ Production Ready  
**Last Updated:** December 5, 2025  
**Maintainer:** Emna877
