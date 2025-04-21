from flask import Flask, request, jsonify
import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os
from flasgger import Swagger, swag_from

app = Flask(__name__)
Swagger(app)

# Load environment variables
load_dotenv('config.env')
database_name = os.getenv('data')
collection_name = os.getenv('collection')

# Connect to MongoDB
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client[database_name]
employee_collection = db[collection_name]

# Auto-increment function
def get_next_emp_id():
    counter = db["counters"].find_one_and_update(
        {"emp_id": "employee_id"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=pymongo.ReturnDocument.AFTER
    )
    return counter["sequence_value"]

# POST: Create Employee
@app.route('/userpost', methods=['POST'])
@swag_from({
    'tags': ['Employee'],
    'parameters': [{
        'in': 'body',
        'name': 'body',
        'required': True,
        'schema': {
            'example': {
                'emp_name': 'syam',
                'emp_salary': 8000
            }
        }
    }],
    'responses': {
        201: {'description': 'Employee created successfully'}
    }
})
def create_employee():
    data = request.get_json()
    data['emp_id'] = get_next_emp_id()  # Auto-generated ID
    result = employee_collection.insert_one(data)
    return jsonify({"message": "Employee added successfully", "id": str(result.inserted_id), "emp_id": data['emp_id']}), 201

# GET all employees
@app.route('/userget', methods=['GET'])
@swag_from({
    'tags': ['Employee'],
    'description': 'Get list of employees',
    'responses': {
        200: {
            'description': 'List of employees',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'emp_id': {'type': 'integer'},
                        'emp_name': {'type': 'string'},
                        'emp_salary': {'type': 'integer'}
                    }
                }
            }
        }
    }
})
def get_employees():
    employees = []
    for emp in employee_collection.find():
        emp['_id'] = str(emp['_id'])  # Convert ObjectId to string
        employees.append(emp)
    return jsonify(employees)

# GET employee by emp_id
@app.route('/userget/<int:emp_id>', methods=['GET'])
@swag_from({
    'tags': ['Employee'],
    'parameters': [{'name': 'emp_id', 'in': 'path', 'type': 'integer', 'required': True}],
    'responses': {
        200: {'description': 'Employee found'},
        404: {'description': 'Employee not found'}
    }
})
def get_employee_by_id(emp_id):
    emp = employee_collection.find_one({'emp_id': emp_id})
    if emp:
        emp['_id'] = str(emp['_id'])
        return jsonify(emp)
    return jsonify({"error": "Employee not found"}), 404

# PUT: Update entire employee
@app.route('/userput/<int:emp_id>', methods=['PUT'])
@swag_from({
    'tags': ['Employee'],
    'parameters': [
        {'name': 'emp_id', 'in': 'path', 'type': 'integer', 'required': True},
        {'name': 'body', 'in': 'body', 'schema': {
            'type': 'object',
            'properties': {
                'emp_name': {'type': 'string'},
                'emp_salary': {'type': 'integer'}
            }
        }}
    ],
    'responses': {
        200: {'description': 'Employee updated successfully'},
        404: {'description': 'Employee not found'}
    }
})
def update_employee(emp_id):
    data = request.get_json()
    result = employee_collection.update_one({'emp_id': emp_id}, {'$set': data})
    if result.matched_count:
        return jsonify({"message": "Employee updated successfully"})
    return jsonify({"error": "Employee not found"}), 404

# PATCH: Partial update
@app.route('/userpatch/<int:emp_id>', methods=['PATCH'])
@swag_from({
    'tags': ['Employee'],
    'parameters': [
        {'name': 'emp_id', 'in': 'path', 'type': 'integer', 'required': True},
        {'name': 'body', 'in': 'body', 'schema': {
            'type': 'object',
            'properties': {
                'emp_name': {'type': 'string'},
                'emp_salary': {'type': 'integer'}
            }
        }}
    ],
    'responses': {
        200: {'description': 'Employee partially updated'},
        404: {'description': 'Employee not found'}
    }
})
def patch_employee(emp_id):
    data = request.get_json()
    result = employee_collection.update_one({'emp_id': emp_id}, {'$set': data})
    if result.matched_count:
        return jsonify({"message": "Employee partially updated"})
    return jsonify({"error": "Employee not found"}), 404

# DELETE employee
@app.route('/userdel/<int:emp_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Employee'],
    'parameters': [{'name': 'emp_id', 'in': 'path', 'type': 'integer', 'required': True}],
    'responses': {
        200: {'description': 'Employee deleted successfully'},
        404: {'description': 'Employee not found'}
    }
})
def delete_employee(emp_id):
    result = employee_collection.delete_one({'emp_id': emp_id})
    if result.deleted_count:
        return jsonify({"message": "Employee deleted successfully"})
    return jsonify({"error": "Employee not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
