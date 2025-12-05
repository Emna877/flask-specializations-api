from flask import Flask
from flask_smorest import Api
from flask_jwt_extended import JWTManager
import os
from db import db
from resources.course_item import blp as CourseItemBlueprint
from resources.specialization import blp as SpecializationBlueprint
from resources.user import blp as UserBlueprint

def create_app(db_url=None):
    app = Flask(__name__)
    
    app.config["API_TITLE"] = "TBS Web Services API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    
    # JWT Configuration
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    
    # API Security Scheme for Swagger
    app.config["API_SPEC_OPTIONS"] = {
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        }
    }
    
    db.init_app(app)
    jwt = JWTManager(app)
    
    with app.app_context():
        db.create_all()
    
    api = Api(app)

    api.register_blueprint(UserBlueprint)
    api.register_blueprint(SpecializationBlueprint)
    api.register_blueprint(CourseItemBlueprint)

    return app

# Create default app instance
app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)