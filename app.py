from flask import Flask, request, abort
from uuid import uuid4
from db import specializations, course_items


app = Flask(__name__)


# SPECIALIZATION ENDPOINTS
@app.get("/specialization")
def get_specializations():
    return {"specializations": list(specializations.values())}

# Create a new specialization
@app.post("/specialization")
def create_specialization():
    data = request.get_json()
    new_id = uuid4().hex
    for specialization in specializations:
        if specializations[specialization]["name"] == data["name"]:
            abort(400, description="Specialization already exists")
    
    new_specialization = {"id": new_id, "name": data["name"]}
    specializations[new_id] = new_specialization
    return new_specialization, 201

# Get a specialization by ID
@app.get("/specialization/<string:specialization_id>")
def get_specialization(specialization_id):
    try:
        return specializations[specialization_id]
    except KeyError:
        abort(404, description="Specialization not found")

# Update a specialization by ID
@app.put("/specialization/<string:specialization_id>")
def update_specialization(specialization_id):
    data = request.get_json()
    if specialization_id not in specializations:
        abort(404, description="Specialization not found")
    if not data or "name" not in data:
        abort(400, description="Bad request. 'name' is required")
    if specializations[specialization_id]["name"] == data["name"]:
        abort(400, description="Specialization name already exists")
    specializations[specialization_id]["name"] = data["name"]
    return specializations[specialization_id]
    
# Delete a specialization by ID
@app.delete("/specialization/<string:specialization_id>")
def delete_specialization(specialization_id):
    try:
        del specializations[specialization_id]
        return {"message": "Specialization deleted"}
    except KeyError:
        abort(404, description="Specialization not found")



# COURSE ITEM ENDPOINTS


@app.get("/course_item")
def get_course_items():
    return {"course_items": list(course_items.values())}


@app.post("/course_item")
def create_course_item():
    data = request.get_json()
    specialization_id = data.get("specialization_id")
    if specialization_id not in specializations:
        abort(404, description="Specialization not found")
    else:
        new_id = str(uuid4().hex)
        for course in course_items:
            if course_items[course]["name"] == data["name"]:
                abort(400, description="Course item already exists")
        new_course_item = {
            "id": new_id,
            "name": data["name"],
            "type": data["type"],
            "specialization_id": specialization_id
        }
        course_items[new_id] = new_course_item
        return new_course_item, 201


@app.get("/course_item/<string:course_id>")
def get_course_item(course_id):
    try:
        return {"course_item": course_items[course_id]}
    except KeyError:
        abort(400, description="Course is not found")

    
@app.put("/course_item/<string:course_id>")
def update_course_item(course_id):
    data = request.get_json()
    if course_id not in course_items:
        abort(404, description="Course is not found")
    if not data or "name" not in data or "type" not in data:
        abort(400, description="The fields 'name' and 'type' are required")
    course_items[course_id]["name"] = data["name"]
    course_items[course_id]["type"] = data["type"]
    return course_items[course_id]
    


@app.delete("/course_item/<string:course_id>")
def delete_course_item(course_id):
    try:
        del course_items[course_id]
        return {"message": "Course item deleted"}
    except KeyError:
        abort(404, description="Course item is not found")


if __name__ == "__main__":
    app.run(debug=True)
