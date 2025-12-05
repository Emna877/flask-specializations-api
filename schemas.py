from marshmallow import Schema, fields

class plain_course_item_schema(Schema):
    id=fields.Str(dump_only=True)
    name=fields.Str(required=True)
    type=fields.Str(required=True)
    specialization_id=fields.Str(required=True)

class plain_specialization_schema(Schema):
    id=fields.Str(dump_only=True)
    name=fields.Str(required=True)

class course_item_update_schema(Schema):
    name=fields.Str(required=True)
    type=fields.Str(required=True)
   

class course_item_schema(plain_course_item_schema):
    specialization=fields.Nested(plain_specialization_schema, dump_only=True)


class specialization_schema(plain_specialization_schema):
    course_items=fields.Nested(plain_course_item_schema, many=True)