import flask
from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flasgger import Swagger,swag_from

app = Flask(__name__)
Swagger(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:esha%40123@localhost:5432/PRACTICE'

db = SQLAlchemy(app)
ma=Marshmallow(app)



class employee_tb (db.Model):
    __tablename__ = 'employee_tb'
    emp_id=db.Column(db.Integer, primary_key=True,autoincrement=True)
    emp_name=db.Column(db.String(200),nullable=False)
    emp_salary=db.Column(db.Integer)
class employee_tbSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = employee_tb
        load_instance = True

    emp_id=ma.auto_field()
    emp_name=ma.auto_field()
    emp_salary=ma.auto_field()
employee_tb_schema= employee_tbSchema()
employee_tb_schemas= employee_tbSchema(many=True)

with app.app_context():
    db.create_all()

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
        201: {
            'description': 'Employee created successfully'
        }
    }
})
def create_employee():
    data = request.get_json()
    user=employee_tb_schema.load(data)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Employee added successfully"}), 201


@app.route('/userget',methods=['GET'])
@swag_from({
    'tags':['Employee'],
    'description':'get list of employees',
    'responses':{
        200:{
            'description':'list of employees',
            'schema':{
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
                
def get_employee():
    emp=employee_tb.query.all()
    return employee_tb_schemas.dump(emp)

@app.route('/userget/<int:emp_id>',methods=['GET'])
@swag_from({
    'tags':['Employee'],
    'description': 'get employee by id',
    'parameters': [
        {
            'name': 'emp_id',
            'in': 'path',
            'type': 'integer',
            'required': True
        }
    ],
    'responses': {
        200: {'description': 'Employee found'},
        404: {'description': 'Employee not found'}
    }
})
def get_users(emp_id):
    emp=employee_tb.query.get_or_404(emp_id)
    return employee_tb_schema.dump(emp)

@app.route('/userput/<int:emp_id>', methods=['PUT'])
@swag_from({
    'tags': ['Employee'],
    'description': 'Update an employee',
    'parameters': [
        {'name': 'emp_id', 'in': 'path', 'type': 'integer', 'required': True},
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'emp_name': {'type': 'string'},
                    'emp_salary': {'type': 'integer'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Employee updated successfully'},
        404: {'description': 'Employee not found'}
    }
})

def update_employee(emp_id):
    emp = employee_tb.query.get_or_404(emp_id)
    data = request.get_json()
    updated_emp = employee_tb.load(data, instance=emp, partial=True)
    db.session.commit()
    return jsonify({"message": "Employee updated", "data": employee_tb_schemas.dump(updated_emp)})

@app.route('/userpatch/<int:emp_id>', methods=['PATCH'])
@swag_from({
    'tags': ['Employee'],
    'description': 'Update an employee',
    'parameters': [
        {'name': 'emp_id', 'in': 'path', 'type': 'integer', 'required': True},
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'emp_name': {'type': 'string'},
                    'emp_salary': {'type': 'integer'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Employee updated successfully'},
        404: {'description': 'Employee not found'}
    }
})

def patch_employee(emp_id):
    emp = employee_tb.query.get_or_404(emp_id)
    data = request.get_json()
    patched_emp = employee_tb_schema.load(data, instance=emp, partial=True)
    db.session.commit()
    return jsonify({"message": "Employee partially updated", "data": employee_tb_schema.dump(patched_emp)})


@app.route('/userdel/<int:emp_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Employee'],
    'description': 'Delete an employee',
    'parameters': [
        {'name': 'emp_id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Employee deleted successfully'},
        404: {'description': 'Employee not found'}
    }
})
def delete_employee(emp_id):
    emp = employee_tb.query.get_or_404(emp_id)
    db.session.delete(emp)
    db.session.commit()
    return jsonify({"message": "Employee deleted successfully"})






if __name__ == '__main__':
    app.run(debug=True)


