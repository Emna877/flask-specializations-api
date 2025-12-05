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

# User schemas for authentication
class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)

class UserRegisterSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

# Backwards compatibility - create lowercase instances
course_item_schema = CourseItemSchema()
specialization_schema = SpecializationSchema()
course_item_update_schema = CourseItemUpdateSchema()