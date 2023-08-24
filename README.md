# Clovis Community College Schedule Builder

## Introductory:
This web application is a comprehensive one-stop tool for counselors, students, and faculty at CCC to use when trying to build SEPs, finding completed degrees/almost completed degrees, checking IGETC/CSU-GE completion, and more! 

A SEP is a schedule for 2-3 years that outlines a suggested course of study for the individual student based on major, transfer plan, and sequence of courses. Every student at CCC needs a SEP after enrolling, and the website [Assist](https://assist.org/) is used to find the courses they need to take based on their transfer university and major. Here is an example of my [SEP schedule](https://drive.google.com/file/d/123zufUVYME2e0x0yxGqaUfAPpxhuxSAS/view?usp=sharing) at CCC.

The Degree finder feature is a very helpful tool to instantly find what degrees a student will earn based on the classes in their SEP. The tool also finds degrees that are almost completed, lists the leftover required classes, and allows the user to add the class to their SEP with a simple click. 

## Why I built this: 

### Schedule Builder

I created this web application because new students struggle to understand these PDF agreement and it can take them a couple of hours to find what classes to take and when to take them. Here is an example of my [ASSIST PDF Agreement](https://assist.org/transfer/report/26539871) where I transferred from CCC to CalPoly SLO: 

![ASSIST PDF Snippet](https://github.com/Castro19/ccc-sep-public/assets/74516049/715311d1-098d-400f-8fce-cb35b7c875ed) 

The outline and configuration can be very intimidating and confusing to new students, so my goal was to make the process much easier and user-friendly. 

Besides the confusing PDF agreements, students need to check for prerequisites of those classes through the 259 page [catalog](https://www.cloviscollege.edu/_uploaded-files/_documents/admissions-and-aid/catalogs/college-catalog-23-24.pdf). There are over 450 courses available at CCC, and here is an example of how these classes are constructed in the catalog: 

![catalog-example](https://github.com/Castro19/ccc-sep-public/assets/74516049/23c2375c-490e-4232-b6b5-492f65e34477") 

For new students, this process can be very stressful, intimidating, and time-consuming. On average students can take multiple hours to do this by themselves. Counselors can create a SEP for the student, however, it can take 30 minutes to an hour to complete. My application creates the SEP in seconds while providing a friendly UI and offering other helpful features. 

### Degree Finder

Students at CCC, also need to apply for degrees during their last year, which can be very time-consuming as they have to go through each major from this [link](https://www.cloviscollege.edu/academics/majors/2022-2023-majors-list.html). 

Most of my classmates I knew only graduated with 2-3 degrees when they actually earned 5+ degrees because they never checked the other degrees or applied for them. When I was searching for my completed degrees, the process took me about 30 minutes. The feature I implemented in my web application finds the earned degrees instantly, and it also finds the degrees almost completed along with the classes leftover. 

This feature helps maximize the number of degrees a student can earn and it has the potential to build the most optimal schedule as it combines transfer requirements, degree requirements, and IGETC/CSU-GE requirements all together. 

Some degree requirements can be very complicated, as well. Here is an example of a degree's requirements at CCC:

![simple degree req](https://github.com/Castro19/ccc-sep-public/assets/74516049/d3b27305-b312-4c73-99cf-54016e8218c1)

### SideNote 
This repository serves as a showcase of my work on the Clovis Community College Schedule Builder. It highlights key features, the technologies used, and the purpose of the application. However, it is missing some necessary files and functions to get the web application running. 

### To access the Schedule Builder, visit
**https://www.ccc-sep.com**

## **Features:**

### **ASSIST API Integration**: 
Gathers the PDF transfer agreements to display to the user or to extract transferable classes from the PDF. The API was also used to create a Dictionary that contains Universities and a list of their majors. Creating this dictionary improved the response time for the dropdown menu that lists the majors of the university. Here is the Dropdown Functionality: ![gif](https://github.com/Castro19/ccc-sep-public/assets/74516049/b774eab0-14f8-4b29-8ed1-e588cf2de17b)

Once the user selects the transfer university and major, the program uses the ASSIST API...

### **Extract Classes from PDF:** 
Functions that read the right side of the PDF agreement and finds the class item based on font attributes and line spacing. It keeps the configurations of "AND" & "OR" so another function can logically choose which classes are required to take. 

### **Uploading SEPs:** 
Users can upload their SEP PDF that is sent to my AWS S3 Bucket where my function downloads it from. After downloading, the function extracts the corresponding textbox locations and values from the PDF, and then automatically inserts them into the textboxes on the webpage. 

### **Retrieving Verified Schedules**: 
Ability to store and retrieve verified schedules from a PostgreSQL Database. A green checkmark appears at the top of the page to indicate it is a verified schedule. 

### **Uploading Verified Schedules:** 
Counselors can easily upload a completed SEP schedule to the PostGreSQL database by inserting a passcode. 
### **Unverified Schedules:** 
An algorithm I created to create a SEP based on the classes extracted from the PDF, "Or" & "AND" Conjunction Logic, the prerequisites, & the unit countnper semester.

### **A dynamic UI:** 
Users can easily insert, delete, move, and swap classes for each semester with ease. Class Buttons also change color to indicate that the class has been used.

### **Prerequisite/Corequisite Panels:** 
Each class button has a hidden panel that displays the prerequisites and corequisites of that class when hovering over the panel icon. 

### **Error Warnings:** 
The Text-Box color changes to red if the class is invalid, either the class is not at CCC or the class does not have the same format. Text-Box color changes to orange if it is a duplicate class. 

### **Degree Analytics**: 
Find completed and nearly completed degrees based on the SEP Schedule created or imported. 

### **IGETC/CSU-GE Completion**: 
Finds what areas have been satisfied and what classes satisfied them based on their schedule. Area dropdown buttons will change to green to indicate completing along with the subject dropdown so the user can locate what class satisfied the area.

### **Export the SEP to the Formal SEP PDF:** 
After the schedule has been finalized, users can export the schedule to the standard PDF for SEP schedules.
### **Report Error:** 
Users can report any errors they have and the error message will be sent to my E-mail and automatically include the university and major in the message, as well. 

## Tools & Libraries Used:
### PYTHON
  - Flask: Served as the primary web framework, handling routing, template rendering, and core 
    application logic.
  - Flask-Session: Managed user sessions, ensuring data consistency and state persistence 
    throughout user interactions.
  - flask_sqlalchemy: Provided Object-Relational Mapping (ORM) capabilities, facilitating seamless 
    interactions with the PostgreSQL database.
  - dotenv: Managed environment variables, ensuring secure and configurable application settings.
  - werkzeug: Assisted in password hashing and security, as well as utility functions for the WSGI 
    application.
  - boto3: Enabled interactions with AWS services, likely for data storage or caching.
  - redis: Managing session data to optimize application performance.
  - sendgrid: Managed email notifications from users to report any errors on the web application
  - pdfplumber: Extracted data from PDF agreements sourced from the Assist API.
  - pandas: Handled and manipulated large datasets of classes and degree requirements, especially       when analyzing or processing class details.
  - re and string: Processed and manipulated strings, especially during data extraction and             validation.
  - urllib: Managed URL operations, potentially for fetching data from external sources.
  - collections: Organized and managed data, especially when dealing with structured data like          schedules.
  - numpy: Handled numerical operations, potentially used in conjunction with pandas for data           analysis.
  - json and pickle: Serialized and deserialized data for storage or transmission.
  - Requests: Made HTTP requests, likely for fetching data or interacting with external APIs.

### SQL
  - PostgreSQL: Managed relational data storage for the SEP application.
  - SQLAlchemy: Streamlined database interactions and ensured data integrity through ORM.
  - pgAdmin4: Employed for database management, schema design, and query execution.
  - Flask-SQLAlchemy: Integrated Flask with PostgreSQL for dynamic data interactions.
  - Data Modeling: Crafted data models to represent entities and maintain data consistency.

### JavaScript
  - Fetch API: Web requests.
  - Promises: Asynchronous operations.
  - DOM Manipulation: Web content interaction.
  - ES6 Features: Modern JavaScript.
  - Error Handling & Logging: Debugging and issue tracking.
  - jQuery: Web interaction and dynamic content manipulation.
  - jQuery UI: Enhancing UI components, specifically the autocomplete feature.
  - JSON: Data serialization and parsing.

### HTML
  - HTML5: Modern web markup.
  - CSS: Web styling and design.
  - Bootstrap: Responsive design framework with interactive components.
  - jQuery: Dynamic content creation and manipulation.
  - FontAwesome: Web icons and styling.
  - Flask Templating (Jinja2): Dynamic web content generation.

### CSS
  - Typography: Text styling & alignment.
  - Layout: Flexbox & box model mastery.
  - Interactivity: Enhancements via hover & active states.
  - Effects: Shadow & transitions for UI polish.
  - Positioning: Precise element placement.
