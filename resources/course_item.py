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
        # Check if specialization exists
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