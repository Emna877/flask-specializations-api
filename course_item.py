# resources/course_item.py
import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import course_items

blp = Blueprint("course_items", __name__, description="Operations on course_items")


@blp.route("/course_item/<string:course_item_id>")
class CourseItem(MethodView):
    def get(self, course_item_id):
        try:
            return course_items[course_item_id]
        except KeyError:
            abort(404, message="Course_Item not found.")

    def delete(self, course_item_id):
        try:
            del course_items[course_item_id]
            return {"message": "Course_Item deleted."}
        except KeyError:
            abort(404, message="Course_Item not found.")

    def put(self, course_item_id):
        data = request.get_json()
        if course_item_id not in course_items:
            abort(404, message="Course_Item not found.")
        if not data or "name" not in data or "type" not in data or "specialization_id" not in data:
            abort(400, message="Bad request. 'name', 'type', and 'specialization_id' are required.")
        course_items[course_item_id].update(data)
        return course_items[course_item_id]


@blp.route("/course_item")
class CourseItemList(MethodView):
    def get(self):
        return {"course_items": list(course_items.values())}

    def post(self):
        data = request.get_json()
        if not data or "name" not in data or "type" not in data or "specialization_id" not in data:
            abort(400, message="Bad request. 'name', 'type', and 'specialization_id' are required.")
        for item in course_items.values():
            if item["name"] == data["name"] and item["specialization_id"] == data["specialization_id"]:
                abort(400, message="Course_Item already exists.")

        course_item_id = uuid.uuid4().hex
        course_item = {**data, "id": course_item_id}
        course_items[course_item_id] = course_item
        return course_item