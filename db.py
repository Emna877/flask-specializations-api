from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserModel(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)


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