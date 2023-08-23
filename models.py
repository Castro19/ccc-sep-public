from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize an instance of SQLAlchemy
db = SQLAlchemy()

# Define the Course model representing a course in the database
class Course(db.Model):
    __tablename__ = 'courses'  # Name of the table in the database
    id = db.Column(db.String, primary_key=True)  # Unique identifier for the course
    units = db.Column(db.String)  # Number of units of the course
    subject = db.Column(db.String)  # Subject of the course
    prerequisites = db.Column(db.String)  # Prerequisite courses for this course
    corequisites = db.Column(db.String)  # Corequisite courses for this course

# Define the VerifiedSchedule model representing a verified schedule in the database
class VerifiedSchedule(db.Model):
    __tablename__ = 'verified_schedules'  # Name of the table in the database
    major = db.Column(db.String, primary_key=True)  # Major of study
    university = db.Column(db.String, primary_key=True)  # Name of the university
    class_list = db.Column(db.PickleType)  # List of classes (serialized)
    textbox_location = db.Column(db.PickleType)  # Locations of textboxes (serialized)
    completed_degrees = db.Column(db.PickleType)  # List of completed degrees (serialized)

# Define the ReportedError model representing reported errors in the database
class ReportedError(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the reported error
    tab_id = db.Column(db.String(50), nullable=False)  # Tab ID related to the error
    description = db.Column(db.Text, nullable=False)  # Description of the error
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp when the error was reported

# Function to add a verified schedule to the database
def add_verified_schedule_to_db(major, university, data, degrees):
    # Extract class list and textbox locations from the data
    class_list = [v for k, v in data.items() if v]  # get classes from dict
    textbox_location = [k for k, v in data.items() if v]  # get textbox locations
    # Create a new VerifiedSchedule instance
    new_schedule = VerifiedSchedule(
        major=major,
        university=university,
        class_list=class_list,
        textbox_location=textbox_location,
        completed_degrees=degrees
    )
    # Add the new schedule to the database session and commit changes
    db.session.add(new_schedule)
    db.session.commit()

# Function to retrieve a verified schedule from the database
def find_verified_schedule(major, university):
    return db.session.query(VerifiedSchedule).filter_by(major=major, university=university).first()

# Function to convert a schedule object into dictionary format
def schedule_to_dict(schedule): 
    data_dict = dict(zip(schedule.textbox_location, schedule.class_list))
    return {
        'major': schedule.major,
        'university': schedule.university,
        'class_list': schedule.class_list,
        'textbox_location': schedule.textbox_location,
        'completed_degrees': schedule.completed_degrees,
        'data_dict': data_dict
    }

# Test function to print all the verified schedules from the database
def print_verified_schedules():
    verified_schedules = db.session.query(VerifiedSchedule).all()  # Retrieve all verified schedules
    for schedule in verified_schedules:
        print(f'Major: {schedule.major}')
        print(f'University: {schedule.university}')
        print(f'Class List: {schedule.class_list}')  # This will automatically de-serialize the PickleType
        print(f'Textbox Location: {schedule.textbox_location}')  # This will automatically de-serialize the PickleType
        print(f'Completed Degrees: {schedule.completed_degrees}')  # This will automatically de-serialize the PickleType


### QUESTIONS I had when learning hot to use DataBases: 

## 1.) What is SQLAlchemy?
# An Object-Relational Mapping (ORM) library for Python that lets you easily interact with databases by using the API of ORM instead of using SQL code.

## 2.) What is 'db.Model'?
# 'db.Model' is the base class provided by the Flask-SQLAlchemy extension for defining database models in a Flask application. 
# Inheriting from 'db.Model', allows the option to define the structure of your database tables using Python classes. 
# It also provides essential methods and behaviors to easily perform database operations like querying, inserting, updating, and deleting records without the need for raw SQL.
# Each attribute of the class representing a column in the table. 
# Acts as a bridge between Python code and the underlying database, allowing for an object-oriented approach to database interactions

## 3.) What is a query?
# Query: A request for data from the database. 
# Instead of writing raw SQL statements, The query API can construct and execute queries.

## 4.) What does it mean to use db.session.query? 
# db.session.query: Creates a new query object that allows you to filter, order, and retrieve data from the database. C
# Constructing a SQL statement without writing the actual SQL code.


