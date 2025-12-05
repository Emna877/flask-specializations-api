
from db import db


class specializations_model(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), unique = True, nullable=False)
    type = db.Column(db.String(80), nullable = False)


    specialization_id = db.Column(db.Integer, unique = False, nullable = True)