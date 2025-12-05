import uuid
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
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
    @blp.doc(security=[{"bearerAuth": []}])
    @jwt_required()
    def put(self, specialization_data, specialization_id):
        specialization = SpecializationModel.query.get_or_404(specialization_id)
        
        specialization.name = specialization_data["name"]
        
        db.session.commit()
        return specialization

    @blp.doc(security=[{"bearerAuth": []}])
    @jwt_required()
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
    @blp.doc(security=[{"bearerAuth": []}])
    @jwt_required()
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