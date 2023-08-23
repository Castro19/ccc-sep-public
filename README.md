# Clovis Community College Schedule Builder

A comprehensive Schedule Builder for Clovis Community College designed to create a Student Educational Planner (SEP). 

## Features:
  - **ASSIST API Integration**: Gathers the PDF transfer agreements to display to the user or to          extract transferable classes from the PDF
  - **Extract Classes from PDF:** Functions that read the right side of the PDF agreement and finds      the class item based on font attributes and line spacing.  
  - **Verified Schedules**: Ability to store and retrieve verified schedules from PostgreSQL             Database.
  - **Unverified Schedules:** An algorithm I created to create a SEP based on the classes                extracted from the PDF, "Or" & "AND" Logic, the prerequisites, & the unit count per semester.  
  - **Degree Analytics**: Find completed and nearly completed degrees based on the SEP Schedule           created or imported. 
  - **IGETC/CSU-GE Completion**: Finds what areas have been satisfied and what classes satisfied          them based on their schedule
  - **

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
