from db import db

class Course_item_model(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), unique = True, nullable=False)
    typr = db.Column(db.String(80), nullable = False)


    specialization_id = db.Column(db.Integer, db.ForeignKey("specializations.id"), unique = False, nullable = True)
    specialization = db.relationship("specialization_model", back_populates = "course_items", lazy = "dynamic")