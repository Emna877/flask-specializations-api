import uuid
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from passlib.hash import pbkdf2_sha256
from db import db, UserModel
from schemas import UserSchema, UserRegisterSchema

blp = Blueprint("Users", __name__, description="User authentication operations")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        """Register a new user"""
        # Check if user already exists
        if UserModel.query.filter_by(username=user_data["username"]).first():
            abort(409, message="Username already exists.")
        
        # Create new user with hashed password
        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"])
        )
        
        db.session.add(user)
        db.session.commit()
        
        return user


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserRegisterSchema)
    def post(self, user_data):
        """Login and get access token"""
        # Find user by username
        user = UserModel.query.filter_by(username=user_data["username"]).first()
        
        # Verify user exists and password is correct
        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=str(user.id))
            return {"access_token": access_token, "user_id": user.id, "username": user.username}
        
        abort(401, message="Invalid username or password.")


@blp.route("/user")
class UserProfile(MethodView):
    @blp.response(200, UserSchema)
    @blp.doc(security=[{"bearerAuth": []}])
    @jwt_required()
    def get(self):
        """Get current user profile (requires authentication)"""
        user_id = get_jwt_identity()
        user = UserModel.query.get_or_404(int(user_id))
        return user
