# resources/specialization.py
import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import specializations

blp = Blueprint("specializations", __name__, description="Operations on specializations")


@blp.route("/specialization/<string:specialization_id>")
class Specialization(MethodView):
    def get(self, specialization_id):
        try:
            return specializations[specialization_id]
        except KeyError:
            abort(404, message="Specialization not found.")

    def delete(self, specialization_id):
        try:
            del specializations[specialization_id]
            return {"message": "Specialization deleted."}
        except KeyError:
            abort(404, message="Specialization not found.")

    def put(self, specialization_id):
        data = request.get_json()
        if specialization_id not in specializations:
            abort(404, message="Specialization not found.")
        if not data or "name" not in data:
            abort(400, message="Bad request. 'name' is required.")
        if specializations[specialization_id]["name"] == data["name"]:
            abort(400, message="Specialization name already exists.")
        specializations[specialization_id]["name"] = data["name"]
        return specializations[specialization_id]


@blp.route("/specialization")
class SpecializationList(MethodView):
    def get(self):
        return {"specializations": list(specializations.values())}

    def post(self):
        data = request.get_json()
        if "name" not in data:
            abort(400, message="Bad request. Ensure 'name' is included in the JSON payload.")
        for specialization in specializations.values():
            if data["name"] == specialization["name"]:
                abort(400, message="Specialization already exists.")

        specialization_id = uuid.uuid4().hex
        specialization = {**data, "id": specialization_id}
        specializations[specialization_id] = specialization
        return specialization