from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import os
from datetime import datetime
import random
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Mohammad%40khan@localhost:3306/test"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db = SQLAlchemy(app)
jwt = JWTManager(app)
logging.basicConfig(level=logging.INFO)

# models

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20))
    full_name = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(500))
    submitted_by = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_name = db.Column(db.String(100))
    submitted_by = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    class_ = db.Column(db.String(20))
    submitted_by = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    semester = db.Column(db.String(20))
    class_ = db.Column(db.String(20))
    lecture_hours = db.Column(db.Integer)
    submitted_by = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class AttendanceLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    present = db.Column(db.Boolean)
    submitted_by = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

#functions

def create_admin_user():
    if User.query.count() == 0:
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        user = User(
            type='admin',
            full_name='Mohammad Arshad Khan',
            username='admin',
            email='admin@gmail.com',
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        logging.info(f"First admin user created, username: admin, password: {password}")

@app.errorhandler(Exception)
def handle_error(e):
    logging.error(f"Error: {str(e)}")
    return jsonify({"error": str(e)}), 500




@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        token = create_access_token(identity=str(user.id))
        return jsonify({"token": token}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/students', methods=['GET', 'POST'])
@jwt_required()
def students():
    print("hello")
    if request.method == 'GET':
        students = Student.query.all()
        return jsonify([{
            "id": s.id,
            "full_name": s.full_name,
            "department_id": s.department_id,
            "class": s.class_,
            "submitted_by": s.submitted_by,
            "updated_at": s.updated_at.isoformat()
        } for s in students])
    if request.method == 'POST':
        data = request.get_json()
        print(str(get_jwt_identity()))
        print(data,"datatttttt")
        s = Student(
            full_name=data['full_name'],
            department_id=data['department_id'],
            class_=data['class'],
            submitted_by=str(get_jwt_identity())
        )
        db.session.add(s)
        db.session.commit()
        return jsonify({"id": s.id}), 201

@app.route('/departments', methods=['GET', 'POST'])
@jwt_required()
def departments():
    if request.method == 'GET':
        departments = Department.query.all()
        return jsonify([{
            "id": d.id,
            "department_name": d.department_name,
            "submitted_by": d.submitted_by,
            "updated_at": d.updated_at.isoformat()
        } for d in departments])
    if request.method == 'POST':
        data = request.get_json()
        d = Department(
            department_name=data['department_name'],
            submitted_by=str(get_jwt_identity())
        )
        db.session.add(d)
        db.session.commit()
        return jsonify({"id": d.id}), 201

@app.route('/courses', methods=['GET', 'POST'])
@jwt_required()
def courses():
    if request.method == 'GET':
        courses = Course.query.all()
        return jsonify([{
            "id": c.id,
            "course_name": c.course_name,
            "department_id": c.department_id,
            "semester": c.semester,
            "class": c.class_,
            "lecture_hours": c.lecture_hours,
            "submitted_by": c.submitted_by,
            "updated_at": c.updated_at.isoformat()
        } for c in courses])
    if request.method == 'POST':
        data = request.get_json()
        c = Course(
            course_name=data['course_name'],
            department_id=data['department_id'],
            semester=data['semester'],
            class_=data['class'],
            lecture_hours=data['lecture_hours'],
            submitted_by=str(get_jwt_identity())
        )
        db.session.add(c)
        db.session.commit()
        return jsonify({"id": c.id}), 201

@app.route('/attendance', methods=['GET', 'POST'])
@jwt_required()
def attendance():
    if request.method == 'GET':
        logs = AttendanceLog.query.all()
        return jsonify([{
            "id": a.id,
            "student_id": a.student_id,
            "course_id": a.course_id,
            "present": a.present,
            "submitted_by": a.submitted_by,
            "updated_at": a.updated_at.isoformat()
        } for a in logs])
    if request.method == 'POST':
        data = request.get_json()
        a = AttendanceLog(
            student_id=data['student_id'],
            course_id=data['course_id'],
            present=data['present'],
            submitted_by=str(get_jwt_identity())
        )
        db.session.add(a)
        db.session.commit()
        return jsonify({"id": a.id}), 201
    


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_admin_user()
    app.run(debug=True)
