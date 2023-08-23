from flask import Flask, render_template, jsonify, session, redirect, send_file, request
from flask_session import Session
from pdfoutput import PDFOutput, generate_universities
from pdfExtract import process_pdf
from Schedule import createSchedule, unverifiedScheduleGenerator, createCSU_GE, createIGETC, replace_nan, createUniversityMap
from outToPDF import write_fillable_pdf, inputSEP
from degree import get_complete_degrees, complete_IGETC, complete_CSU_GE
import pickle
import json
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from models import add_verified_schedule_to_db, find_verified_schedule, schedule_to_dict, print_verified_schedules, db
import uuid
import collections
from decouple import config
import boto3
from botocore.exceptions import NoCredentialsError
import redis 
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import timedelta

# initialize the s3 client
s3 = boto3.client('s3')
# Initialize univ_map & class_dict as global vars
with open('u_map.pkl', 'rb') as f:
    u_map_unpickled = pickle.load(f)
with open('file_dictionaries/class_dict.pkl', 'rb') as f:
    class_dict = pickle.load(f)

load_dotenv() # Load Env Vars
def create_app():
    app = Flask(__name__) # Initialize our Flask Application
    
    @app.before_request
# Function that switches to the HTTPS version of the URL if we are in our production environment 
    def before_request():
        if os.getenv('FLASK_ENV') == 'production' and request.url.startswith('http://'):
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301) 
        
    app.secret_key = os.getenv('SECRET_KEY') # Keep client-side sessions secure

# Use Redis as the Session Backend and store information for only 24 hours:
    # Store data so user can refresh page or exit and enter back without losing their data
    app.config['SESSION_TYPE'] = 'redis'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_REDIS'] = redis.from_url(os.getenv('REDISCLOUD_URL'))
    Session(app)

# Initialzie our PostgreSQL database that stores our verified schedules
    database_url = os.getenv('DATABASE_URL')
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()

# After App is Created, we Return it
    return app

# Initialize app by calling our Function which:
    # Initializes Flask App
    # Sets HTTPS to be used in Production
    # Uses Redis to store user input for 24 hours
    # Initialize our PostgreSQL Database w/ necessary tables
app = create_app()


# Main Purpose of index(): The start of our Flask Application where we use the user's input and backend Python Functions to find what data they need for their corresponding major and university. 
@app.route('/', methods=['GET', 'POST'])
def index():
     # Check if the current request is a POST request.
    if request.method == 'POST': 
        # Debugging statement to indicate that the POST method was called
        print('POST Method Called') 
        # Generate a unique ID for the current tab using UUID
        tab_id = str(uuid.uuid4()) 
        # Debugging statement to indicate the tab_id created
        print(f"Generated Tab ID: {tab_id}")

        # Retrieve the university_id and major from the form data
        university_id = int(request.form.get('university'))
        major = request.form.get('major')

        # Retrieve the school year from the form data
        school_year_str = request.form.get('school_year')
        # Attempt to convert the school year to an integer
        # If it fails, default to 2023
        try:
            school_year = int(school_year_str)
        except (ValueError, TypeError):
            school_year = 2023
        # Generate a list of years for the next 3 years
        years_list = [year for i in range(school_year, school_year + 4) for year in [i] * (2 if i == school_year else 3 if i <= school_year + 2 else 1)]

        # Determine which button was clicked in the form
        button_clicked = request.form.get('button')  
        # Generate a PDF output for the given university and Major
        pdf_output = PDFOutput(university_id, 73) # 73 is school year id for 22-23
        pdf_url = pdf_output.get_pdf_url(major, button_clicked=button_clicked)

        # Create a mapping of university IDs to their respective names
        u_map = createUniversityMap()
        # Initialize session data for the current tab_id & Save content to our unique Session ID and store info in our Session: Redis
        session[tab_id] = {
            'university_name': u_map[str(university_id)], 
            'major': major, 
            'classList': [],
            'subject': collections.defaultdict(),
            'ged': createCSU_GE(),
            'igetc': createIGETC(),
            'year': years_list,
            'class_dict': class_dict,
            'pdf_data': {}
            # Dictionary 4 {textbox location: textbox values} ?
        }
        
        # Check if a PDF URL was successfully generated
        if pdf_url:
            #  Get Schedule: Insert necessary information to our session
            if button_clicked == 'get-schedule':
                classList = process_pdf(pdf_url, university_id, major)
                subjects = createSchedule(classList)
                session[tab_id]['major'] = major
                session[tab_id]['subject'] = subjects
                session[tab_id]['classList'] = classList
                session[tab_id]['class_dict'] = class_dict
                return jsonify(tab_id=tab_id)
            # If the 'get-pdf-button' was clicked, return the PDF URL.
            elif button_clicked == 'get-pdf-button': 
                return pdf_url
        else: # If no PDF was found, return an error message
            return "No PDF found"
    else: 
        # If it's a GET request, generate a list of universities and sort them by name
        #  EX: When the page initially loads in
        universities = generate_universities()
        universities.sort(key=lambda x: x['name'])

    # Render the index.html template with the list of universities
    return render_template('index.html', universities=universities)

# Main Purpose of schedule(): Retrieve the stored session data with the key value of our tab_id and render our HTML temlate to display this data 
@app.route('/schedule', methods=['GET'])
def schedule():
    # Retrieve the 'tab_id' parameter from the request's query parameters
    tab_id = request.args.get('tab_id')
     # Check if the requested 'tab_id' exists in the session
    if tab_id in session:
        # Fetch various pieces of data associated with the 'tab_id' from the session.
        university_name = session[tab_id].get('university_name')
        major = session[tab_id].get('major')
        years_list = session[tab_id].get('year')
        classList = session[tab_id].get('classList')
        class_dict = session[tab_id].get('class_dict', {})
        subjects = session[tab_id].get('subject', {})  
        ged = session[tab_id].get('ged', {})
        IGETC = session[tab_id].get('igetc', {})
        pdf_data = session[tab_id].get('pdf_data', {})
        # Store the university name in the session for potential future use
        session['university'] = university_name
    else:
    # If the 'tab_id' doesn't exist in the session, return an error message with a 404 status code.
        return "No data for this tab id", 404

    # Render the 'schedule.html' template with the fetched data, so the user can view their schedule w/ the correct information
    return render_template('schedule.html', ged=ged, IGETC=IGETC,classList=classList, subjects=subjects, university=university_name, major=major, years_list=years_list,pdf_data=pdf_data, tab_id=tab_id, class_dict=class_dict)

# Main purpose of upload_file(): Allows users to upload a PDF of their SEP to our AWS S3 Bucket where the backend function "inputSEP()" finds the texbox values and locations and assigns it appropriately to our schedule.html
@app.route('/upload', methods=['POST'])
def upload_file():
    # Generate a unique ID for the current session/tab using UUID
    tab_id = str(uuid.uuid4())  
     # Initialize session data for the current tab_id with default values
    session[tab_id] = {
    'university_name': 'Unknown University', 
    'major': 'Unknown Major', 
    'subject': collections.defaultdict(),
    'ged': createCSU_GE(),
    'igetc': createIGETC(),
    'class_dict': class_dict,
    'pdf_data': {}
    # Dictionary 4 {textbox location: textbox values}
    }
    # Check if the 'pdf_file' is part of the uploaded files in the request
    if 'pdf_file' not in request.files:
        return 'No file part'
    file = request.files['pdf_file']

    # Check if a file was actually selected for upload
    if file.filename == '':
        return 'No selected file'
    # Check if the uploaded file is a PDF
    if file and file.filename.endswith('.pdf'):
        # Secure the filename to ensure it doesn't contain any unsafe characters
        filename = secure_filename(file.filename)
        
        try:
            # Attempt to upload the file to my AWS S3 bucket.
            s3.upload_fileobj(file, 'ccc-sep-pdf', filename)  # Upload files to S3 instead
        except NoCredentialsError:
            # Return an error if AWS credentials are not found.
            return 'No AWS credentials found'
        
        # Assuming the inputSEP function can take an S3 path or URL
        # Process the uploaded PDF and retrieve relevant data
        data_tuples = inputSEP(filename)
        
        # Store Processed Data in the Redis Session
        session[tab_id]['pdf_data'] = data_tuples

    # Return a JSON response containing the tab_id
    return jsonify({'tab_id': tab_id})

# An admin (counselor or myself) can verify a schedule to be sent to our Postgre SQL database after a schedule has been double-checked to meet all the transfer requirements so it can be easily re-used next time 
@app.route('/submit_schedule', methods=['POST'])
def submit_schedule():
    data = request.json.get('data')  # Get the schedule data from the request
    major = request.json.get('major')  # Get the major from the request
    university = request.json.get('university')  # Get the university from the request
    # print(university, major, tab_id)
    degrees = session.get('completed_degrees', [])  # Get the completed degrees from the session

    add_verified_schedule_to_db(major, university, data, degrees)  # Add the schedule to the db

    return jsonify({'status': 'success'}), 200  # Return a success response

# Retrieve a schedule (verified or unverified) based on the user's input for Transfer University and Major. If a schedule is in our verified schedule database then retireve and return. IF NOT then create an unverified schedule based on the algorithm I created: 
@app.route('/generate_schedule', methods=['GET'])
def generate_schedule():
    # Retrieve the 'tab_id', 'major', and 'university' from the request's query parameters.
    tab_id = request.args.get('tab_id')
    major = request.args.get('major')  # Get the major from the query parameters
    university = request.args.get('university')  # Get the university from the

    # Retrieve the session data associated with the given 'tab_id'.
    session_data = session.get(tab_id, {})
    classList = session_data.get('classList', [])

    # Look for a previously verified schedule in the database that matches the provided major and university.
    schedule = find_verified_schedule(major, university)  # Look for the schedule in the Verified Schedule DataBase
    if schedule is None:
        # If no verified schedule is found, generate a new unverified schedule
        unverified_schedule = unverifiedScheduleGenerator(classList)
        return jsonify({'status': 'error', 'message': 'No verified schedule found.', 'data_dict': unverified_schedule}), 200  
    else:
        # If a verified schedule is found, return it
        return jsonify({'status': 'success', 'data_dict': schedule_to_dict(schedule)}), 200  # If a schedule was found, return it

#  Use a Back-End Python Function to find the degrees completed & almost completed based on the classes in the user's inputted Schedule 
@app.route('/calculate-degrees', methods=['POST'])
def calculate_degrees():
    # Retrieve the JSON payload from the incoming request
    data = request.get_json()
     # Extract the user's classes from the data and store them in the session
    user_classes = list(data.values())
    session['user_classes'] = user_classes

    # Use Backend Python Function that determines which degrees the user has completed and which they've almost completed based on their classes
    completed_degrees, almost_completed_degrees = get_complete_degrees(user_classes)
    session['completed_degrees'] = completed_degrees

    # Construct a result dictionary with the completed and almost completed degrees
    result = {
        'completed_degrees': completed_degrees,
        'almost_completed_degrees': almost_completed_degrees
    }

    # Return the result as a JSON response
    return jsonify(result)

# Use a Back-End Python Function to find what areas have been completed for the IGETC Transfer Requirements based on the  user's inputted Schedule 
@app.route('/complete_IGETC', methods=['POST'])
def api_complete_IGETC():
    # Retrieve the JSON payload from the incoming request
    data = request.get_json()

    # Extract the user's classes from the data and store them in the session.
    user_classes = list(data.values())
    session['user_classes'] = user_classes

    # Call a function to determine the user's IGETC completion status based on their classes
    IGETC_tup = complete_IGETC(user_classes)

    # Flask's jsonify can handle the tuple to turn it into a JSON object
    return jsonify({'IGETC_results': IGETC_tup})

# Use a Back-End Python Function to find what areas have been completed for the CSU-GE Transfer Requirements based on the  user's inputted Schedule 
@app.route('/complete_CSU_GE', methods=['POST'])
def api_complete_CSU_GE():
    # Retrieve the JSON payload from the incoming request
    data = request.get_json()

    # Extract the user's classes from the data and store them in the session
    user_classes = list(data.values())
    session['user_classes'] = user_classes

    # Call a function to determine the user's CSU GE completion status based on their classes
    ret_tup = complete_CSU_GE(user_classes)

    # Flask's jsonify can handle the tuple to turn it into a JSON object
    return jsonify({'results': ret_tup})

# Use the user's inputted Schedule and store the class data into a formal PDF the College uses in the correct format based on the textbox locations:
@app.route('/modify-pdf', methods=['POST'])
def modify_pdf():
    # Retrieve the JSON payload from the incoming request, which contains data to be written to the PDF
    data = request.get_json()

    # Define a path where the modified PDF will be saved
    output_pdf_path = 'output.pdf'

    # Call the function to modify a fillable input PDF ('SEP.pdf') by writing the provided data to it
    # The modified PDF is saved to the specified output path
    write_fillable_pdf('SEP.pdf', output_pdf_path, data)

    # Send the modified PDF as a response to the client, setting its MIME type to 'application/pdf'
    return send_file(output_pdf_path, mimetype='application/pdf')

# Allow the user to view the content of the PDF created in the browser. 
@app.route('/display_pdf', methods=['GET'])
def display_pdf():
    # Retrieve the PDF content stored in the session. If no content is found, a default empty string is used
    pdf_content = session.get('pdf_content', '')  # Retrieve the content from the session

    # Render an HTML template named 'pdf_extract.html', passing the retrieved PDF content to it
    return render_template('pdf_extract.html', pdf_content=pdf_content)

# Retrieves a list of majors associated with a given university ID and sorts them before returning it as a JSON response
@app.route('/majors', methods=['GET'])
def get_majors():
    # Retrieve the 'university_id' from the request's query parameters and convert it to an integer
    university_id = int(request.args.get('university_id'))
    
    # Fetch the list of majors associated with the given university ID from the unpickled university map
    # Then sort the list of majors by alphabetical order
    majors = sorted(u_map_unpickled[university_id]['majors'])

    # Return the sorted list of majors as a JSON response
    return jsonify(majors)  

# Using our class_dict, we want to remove any NaN values and return it as a JSON response
@app.route('/class_dict', methods=['GET'])
def get_class_dict():
    # Replace any NaN values in the 'class_dict' with appropriate values
    class_dict_no_nan = replace_nan(class_dict)

    # Convert the updated dictionary into a JSON string
    json_class_dict_no_nan = json.dumps(class_dict_no_nan)  

    # Return the JSON string as the response
    return json_class_dict_no_nan

@app.route('/favicon.ico')
def favicon():
    # Define the path to the favicon file located in the 'static' directory.
    favicon_path = os.path.join(app.root_path, 'static', 'blank.ico')
    
    # Send the favicon file as the response with the appropriate MIME type.
    return send_file(favicon_path, mimetype='image/vnd.microsoft.icon')

# Users can submit an error that is sent to my E-mail address and it automatically includes the university and major. 
@app.route('/report_error', methods=['POST'])
def report_error():
    # Retrieve the error description and tab_id from the form data in the request
    error_description = request.form.get('description')
    tab_id = request.form.get('tab_id')

    # Check if the provided 'tab_id' exists in the session.
    if tab_id in session:
        # Fetch the university name and major associated with the 'tab_id' from the session
        university_name = session[tab_id].get('university_name')
        major = session[tab_id].get('major')
        
        # Compose the content of the email using the fetched university name, major, and error description
        email_content = f"University: {university_name}\nMajor: {major}\nDescription: {error_description}"

        # Define the subject and recipient email for the error report
        subject = "Error Notification"
        to_email = "castro698469@gmail.com"  # Recipient's email address

        # Call the 'send_email' function to send the error report via email
        send_email(subject, to_email, email_content)

        # Return a success message to the client
        return "Error reported successfully!"
    else:
        # If the 'tab_id' doesn't exist in the session, return an error message
        return "Error reporting failed. Invalid tab id.", 400
    
def send_email(subject, to_email, content):
    # Create a new email message using the SendGrid Mail object
    message = Mail(
        from_email='Castro698469@gmail.com',
        to_emails=to_email,
        subject=subject,
        plain_text_content=content
    )
    try:
        # Instantiate the SendGrid client using the API key from the environment variables
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))

        # Send the email message using the SendGrid client
        response = sg.send(message)

        # Print the status code, body, and headers of the response for debugging purposes
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        # If there's an error while sending the email, print the error message for debugging
        print(e.message)

if __name__ == "__main__":
    if os.environ.get('FLASK_ENV') == 'production':
        app.run(debug=False) # Turn off debug in our production environment for safety procedures 
    else:
        app.run(debug=True) # Else we have it turned on to easily find bugs 

# This Flask application is a web-based tool for students to plan their educational paths at Clovis community college, focusing on transfer goals to UC or CSU universities. The app provides various features:

    # 1.) Secure Configuration: The app ensures it uses HTTPS in production, obtains configurations from environment variables, and uses Redis for session management.

    # 2.) Data Interaction: Users can input their educational details, which the app uses to generate or retrieve schedules, calculate degree completion status, and more.

    # 3.) PDF Operations: The app can modify and extract data from PDFs, which is a significant part of its functionality, dealing with educational forms or schedules in PDF format.

    # 4.) Email Notifications: Errors or issues can be reported by users, which are then emailed to administrators or relevant stakeholders.

    # 5.) Dynamic Content Rendering: Based on user input and session data, the app generates dynamic content, such as lists of majors, class dictionaries, and more, and presents it to the user.

# In conclusion, this Flask app serves as a comprehensive tool for students to navigate their educational journey, backed by functionalities that ensure data accuracy, user convenience, and timely error reporting.
