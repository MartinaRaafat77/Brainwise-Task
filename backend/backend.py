from flask import Flask, request, jsonify
import pymysql
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash  
app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='company_management',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

@app.route('/api/user_account/login', methods=['POST'])
def login_user():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    print(f"Received login data: email = {email}, password = {password}")

    connection = get_db_connection()
    with connection.cursor() as cursor:
        query = "SELECT id, email, password, employee_id FROM user_account WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user and user['password'] == password:
            return jsonify({'message': 'Login successful!', 'user': user}), 200
        else:
            return jsonify({'message': 'Invalid email or password.'}), 401


# @app.route('/api/user_account/register', methods=['POST'])
# def register_user():
#     data = request.json
#     name = data.get('name')
#     email = data.get('email')
#     password = data.get('password')

#     connection = get_db_connection()
#     with connection.cursor() as cursor:
#         query = "SELECT * FROM user_account WHERE email = %s"
#         cursor.execute(query, (email,))
#         user = cursor.fetchone()
        
#         if user:
#             return jsonify({'message': 'Email already registered.'}), 409
        
#         query = "INSERT INTO user_account (name, email, password) VALUES (%s, %s, %s)"
#         cursor.execute(query, (name, email, password))
#         connection.commit()

    
# Employee
@app.route('/api/employee', methods=['POST', 'GET'])
def manage_employee():
    if request.method == 'POST':
        data = request.json
        employee_name = data.get('employee_name')
        email = data.get('email')
        mobile_number = data.get('mobile_number')
        address = data.get('address')
        position = data.get('position')
        hired_on = data.get('hired_on')
        company_name = data.get('company_name')
        department_name = data.get('department_name')
        password = data.get('password')
        
        connection = get_db_connection()
        with connection.cursor() as cursor:
            query = """INSERT INTO employee (employee_name, email_address, mobile_number, address, designation, hired_on, company_name, department_name, password)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (employee_name, email, mobile_number, address, position, hired_on, company_name, department_name, password))
            connection.commit()

        connection.close()
        return jsonify({'message': 'Employee added successfully!'}), 201

    elif request.method == 'GET':
        employee_name = request.args.get('employee_name')
        connection = get_db_connection()
        with connection.cursor() as cursor:
            if employee_name:
                query = "SELECT * FROM employee WHERE employee_name LIKE %s"
                cursor.execute(query, ('%' + employee_name + '%',))
            else:
                query = "SELECT * FROM employee"
                cursor.execute(query)
            employees = cursor.fetchall()
        connection.close()
        return jsonify(employees)

@app.route('/api/employee/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def employee_details(id):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        if request.method == 'GET':
            query = "SELECT * FROM employee WHERE employee_id = %s"
            cursor.execute(query, (id,))
            employee = cursor.fetchone()
            return jsonify(employee)

        elif request.method == 'PATCH':
            data = request.json
            employee_name = data.get('employee_name')
            email = data.get('email')
            mobile_number = data.get('mobile_number')
            address = data.get('address')
            position = data.get('position')
            hired_on = data.get('hired_on')
            company_name = data.get('company_name')

            query = """UPDATE employee
                        SET employee_name = %s, email_address = %s, mobile_number = %s, address = %s,
                            designation = %s, hired_on = %s, company_name = %s
                        WHERE employee_id = %s"""
            cursor.execute(query, (employee_name, email, mobile_number, address, position, hired_on, company_name, id))
            connection.commit()
            return jsonify({'message': 'Employee updated successfully!'})

        elif request.method == 'DELETE':
            query = "DELETE FROM employee WHERE employee_id = %s"
            cursor.execute(query, (id,))
            connection.commit()
            return jsonify({'message': 'Employee deleted successfully!'})

    connection.close()

# Companies
@app.route('/api/companies', methods=['GET'])
def get_companies():
    company_name = request.args.get('company_name')
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if company_name:
                cursor.execute("SELECT * FROM companies WHERE company_name LIKE %s", ('%' + company_name + '%',))
            else:
                cursor.execute("SELECT * FROM companies")
            companies = cursor.fetchall()
        return jsonify(companies) if companies else jsonify([]), 200
    finally:
        conn.close()

@app.route('/api/companies/<int:company_id>', methods=['GET'])
def get_company(company_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM companies WHERE id = %s", (company_id,))
            company = cursor.fetchone()
        return jsonify(company) if company else jsonify({"message": "Company not found!"}), 404
    finally:
        conn.close()

# Departments
@app.route('/api/departments', methods=['GET'])
def get_departments():
    department_name = request.args.get('department_name')
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if department_name:
                cursor.execute("SELECT * FROM departments WHERE department_name LIKE %s", ('%' + department_name + '%',))
            else:
                cursor.execute("SELECT * FROM departments")
            departments = cursor.fetchall()
        return jsonify(departments) if departments else jsonify([]), 200
    finally:
        conn.close()

@app.route('/api/departments/<int:department_id>', methods=['GET'])
def get_department_by_id(department_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM departments WHERE id = %s", (department_id,))
            department = cursor.fetchone()
        return jsonify(department) if department else jsonify({"message": "Department not found!"}), 404
    finally:
        conn.close()

# Projects
@app.route('/api/projects', methods=['POST', 'GET'])
def manage_projects():
    if request.method == 'POST':
        data = request.json
        project_name = data.get('project_name')
        description = data.get('description')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        company_name = data.get('company_name')
        department_name = data.get('department_name')

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM companies WHERE company_name = %s", (company_name,))
                company = cursor.fetchone()
                if not company:
                    return jsonify({"message": "Company not found!"}), 404
                company_id = company['id']

            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM departments WHERE department_name = %s", (department_name,))
                department = cursor.fetchone()
                if not department:
                    return jsonify({"message": "Department not found!"}), 404
                department_id = department['id']

            with conn.cursor() as cursor:
                cursor.execute(""" 
                    INSERT INTO projects (project_name, description, start_date, end_date, company_id, department_id, company_name, department_name)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (project_name, description, start_date, end_date, company_id, department_id, company_name, department_name))
                project_id = cursor.lastrowid

                for id in data.get('assigned_employee', []):
                    cursor.execute(""" 
                        INSERT INTO project_assignments (project_id, id) 
                        VALUES (%s, %s)
                    """, (project_id, id))

                conn.commit()
            return jsonify({"message": "Project created successfully!"}), 201
        finally:
            conn.close()

    if request.method == 'GET':
        project_name = request.args.get('project_name')
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                if project_name:
                    cursor.execute("SELECT * FROM projects WHERE project_name LIKE %s", ('%' + project_name + '%',))
                else:
                    cursor.execute("SELECT * FROM projects")
                projects = cursor.fetchall()
            return jsonify(projects) if projects else jsonify([]), 200
        finally:
            conn.close()

@app.route('/api/projects/<int:project_id>', methods=['GET', 'PATCH', 'DELETE'])
def project_operations(project_id):
    conn = get_db_connection()
    try:
        if request.method == 'GET':
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
                project = cursor.fetchone()
            return jsonify(project) if project else jsonify({"message": "Project not found!"}), 404

        if request.method == 'PATCH':
            data = request.json
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE projects
                    SET project_name = %s, description = %s, start_date = %s, end_date = %s
                    WHERE id = %s
                """, (data['project_name'], data['description'], data['start_date'], data['end_date'], project_id))
                conn.commit()
            return jsonify({"message": "Project updated successfully!"})

        if request.method == 'DELETE':
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM projects WHERE id = %s", (project_id,))
                conn.commit()
            return jsonify({"message": "Project deleted successfully!"})
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
