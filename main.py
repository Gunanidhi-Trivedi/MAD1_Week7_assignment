from ast import IfExp
from tkinter import CASCADE
from xmlrpc.server import list_public_methods
from flask import Flask
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask import redirect
# current_dir=os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
# initilise the db and set it in the flask app
db = SQLAlchemy(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"

# importing the bass mordle from sqlalchemy

class Student(db.Model):
    __tablename__ = "student"
    student_id = db.Column(db.Integer(),autoincrement=True,primary_key=True)
    roll_number = db.Column(db.String(), unique=True,nullable=False)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String())
    cources = db.relationship("Course",secondary="enrollments",backref="student")

   
    # def __repr__(self):
    #     return "<User : %r>" % self.username

class Course(db.Model):
    __tablename__ = "course"
    course_id = db.Column(db.Integer(),autoincrement=True,primary_key=True)
    course_code = db.Column(db.String(),unique=True,nullable=False)
    course_name = db.Column(db.String(),nullable=False)
    cource_description = db.Column(db.String())
    # # relationship between auther(user) and article stored in auther_articles table   
    # authors = db.relationship("User",secondary="article_auther")
    # def __repr__(self):
    #     return "<Article : %r>" % self.title

class Enrollments(db.Model):
    __tablename__ = "enrollments"
    enrollment_id = db.Column(db.Integer(),primary_key=True,autoincrement=True)
    estudent_id = db.Column(db.Integer(),db.ForeignKey("student.student_id"),nullable=False)
    ecourse_id = db.Column(db.Integer(),db.ForeignKey("course.course_id"),nullable=False)


# *************** home page ********************* 
@app.route("/",methods=["GET"])
def index():
    try:
        students = Student.query.all()
        # raise Exception("error")
        if len(students) != 0:
            return render_template("index.html",students=students), 200
        else:
            return render_template("error.html"), 200
    except:
        return render_template("error.html"), 200

# ****************************** show courses **************************************
@app.route("/student/<student_id>",methods=["GET"])
def display_student(student_id):
    student=Student.query.filter_by(student_id=student_id).one()
    relation=Enrollments.query.filter_by(estudent_id = student_id).all()
    courses=[]
    for row in relation:
        courses.append(Course.query.filter_by(course_id=row.ecourse_id).one())
    
    return render_template("display.html",student=student,courses=courses), 200


#  ********************* add student *************************
@app.route("/student/create",methods=["GET","POST"])
def add_student():
    if request.method == "GET":
        return render_template("add_student.html"), 200
    elif request.method == "POST":
        try:
            roll=request.form["roll"]
            f_name=request.form["f_name"]
            l_name=request.form["l_name"]
            student_obj=Student(roll_number = roll , first_name = f_name , last_name = l_name  )
            db.session.add(student_obj)
            db.session.commit()
        
            return redirect('/'), 200
        except:
            return render_template("student_exists.html"), 200

# ***************************** update student **********************************
@app.route("/student/<student_id>/update",methods=["GET","POST"])
def update_student(student_id):
    student=Student.query.filter_by(student_id=student_id).one()
    courses=Course.query.all()
    if request.method == "GET":
        return render_template("update.html",student=student,courses=courses), 200
    elif request.method == "POST":
        f_name=request.form["f_name"]
        l_name=request.form["l_name"]
        course = request.form.get('course')
        student.first_name = f_name
        student.last_name = l_name
        course_list = Enrollments.query.filter_by(estudent_id=student_id).all()
        for i in course_list:
            if i.ecourse_id == int(course):
                db.session.commit()
                return redirect('/'), 200
        obj=Enrollments(estudent_id = student_id , ecourse_id = course)
        db.session.add(obj)
        db.session.commit()
        return redirect('/'), 200


# ******************************** delete student *****************************************

@app.route("/student/<student_id>/delete",methods=["GET"])
def delete_student(student_id):
    student=Student.query.filter_by(student_id=student_id).one()
    try:
        db.session.delete(student)
    except:
        list_to_delete=Enrollments.query.filter_by(estudent_id = student_id).all()
        for row in list_to_delete:
            db.session.delete(row)
    db.session.commit()
    return redirect('/'), 200
# error in delete dublicate values

# ************************** withdrow ************************************************
@app.route("/student/<student_id>/withdraw/<course_id>",methods=["GET"])
def withdrow(student_id,course_id):
    to_delete=Enrollments.query.filter_by(estudent_id = student_id,ecourse_id = course_id).one()
    db.session.delete(to_delete)
    db.session.commit()
    return redirect('/') , 200

# ******************************* show courses ************************************************
@app.route("/courses",methods=["GET"])
def course_list():
    try:
        courses=Course.query.all()
        if len(courses) != 0:
            return render_template("course.html",courses=courses), 200
        else:
            return render_template("course_error.html"), 200
    except:
        return render_template("course_error.html"), 200

# ********************************** add courses *****************************************

@app.route("/course/create",methods=["GET","POST"])
def add_course():
    if request.method == "GET":
        return render_template("add_course.html")
    elif request.method == "POST":
        c_code=request.form["code"]
        c_name=request.form["c_name"]
        c_desc=request.form["desc"]
        course=Course.query.filter_by(course_code=c_code).all()
        if len(course)==0:
            course_obj=Course(course_code=c_code,course_name=c_name,cource_description=c_desc)
            db.session.add(course_obj)
            db.session.commit()
            return redirect('/courses'), 200
        else:
            return render_template("course_exists.html"), 200

# ************************************** update course *****************************************************
@app.route("/course/<course_id>/update",methods=["GET","POST"])
def update_course(course_id):
    course=Course.query.get(course_id)
    if request.method == "GET":
        return render_template("update_course.html",course=course), 200
    elif request.method == "POST":
        c_name=request.form["c_name"]
        c_desc=request.form["desc"]
        course.course_name = c_name
        course.cource_description = c_desc
        db.session.commit()
        return redirect('/courses'), 200
        
# *************************************** delete course ***********************************************************************
@app.route("/course/<course_id>/delete",methods=["GET","POST"])
def delete_course(course_id):
    course=Course.query.get(course_id)
    list_to_be_deleted = Enrollments.query.filter_by(ecourse_id=course_id).all()
    for i in list_to_be_deleted:
        db.session.delete(i)
    db.session.delete(course)
    db.session.commit()
    return redirect('/courses'), 200

# ****************************** show course ***************************************
@app.route("/course/<course_id>",methods=["GET"])
def show_course(course_id):
    course=Course.query.get(course_id)
    relation = Enrollments.query.filter_by(ecourse_id=course_id).all()
    student = []
    for i in relation:
        s=Student.query.filter_by(student_id=i.estudent_id).one()
        student.append(s)
    return render_template("show_course.html",course=course,student=student), 200








if __name__=="__main__":
    # run the flask app
    app.run()

