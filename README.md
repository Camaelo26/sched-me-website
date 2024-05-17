Sched Me Website
Sched Me Website is a comprehensive web application designed to help users manage their schedules, appointments, and tasks efficiently. This project provides a user-friendly interface to streamline the scheduling process and ensure effective time management.

Features
User Authentication: Secure login system for accessing personalized schedules.
Appointment Scheduling: Users can schedule appointments with specific details such as department, doctor, date, and time.
Task Management: Users can add, edit, and delete tasks easily.
Interactive Dashboard: Provides a visual representation of tasks and appointments for better management.
Department Selection: Users can choose from various departments when scheduling appointments.
Database Integration: Efficient data handling and storage using SQLite.
Technologies Used
Python: Backend logic and server-side scripting.
Flask: Web framework for building the application.
HTML/CSS: Structure and styling of the web pages.
JavaScript: Interactivity and dynamic features.
SQLite: Database for storing user and schedule data.
Project Structure
app.py: Main application file that sets up the Flask server and routes.
appointment.py: Handles appointment scheduling functionalities.
connection.py: Manages the database connection.
department.py: Manages department-related operations.
executequery.py: Contains functions to execute database queries.
register.py: Handles user registration functionalities.
update.py: Manages the updating of user information and schedules.
templates/: Directory containing HTML templates.
static/: Directory containing static files such as CSS and JavaScript.
How to Run the Project
Clone the repository:

bash
Copy code
git clone https://github.com/yourusername/sched-me-website.git
Navigate to the project directory:

bash
Copy code
cd sched-me-website
Install the required dependencies:

bash
Copy code
pip install -r requirements.txt
Set up the database:

bash
Copy code
python executequery.py
Run the Flask application:

bash
Copy code
python app.py
Open your web browser and navigate to:

text
Copy code
http://localhost:5000
to access the Sched Me Website.

Detailed Description of Key Files
app.py:

Initializes the Flask application.
Sets up the main routes for the web application.
Manages user sessions and overall application flow.
appointment.py:

Contains functions and classes for handling appointment scheduling.
Interfaces with the database to create, retrieve, update, and delete appointment records.
connection.py:

Manages the connection to the SQLite database.
Provides utility functions for executing SQL queries and managing transactions.
department.py:

Manages department-related data and operations.
Interfaces with the database to retrieve department information.
executequery.py:

Contains various database query functions.
Used for initializing and managing database schema and records.
register.py:

Handles user registration functionalities.
Manages the creation of new user records in the database.
update.py:

Provides functionalities for updating user information and schedules.
Ensures that user data is kept up-to-date in the database.
Contact
For any questions or inquiries, please contact:

Name: Macarthur Diby
Phone: 972-217-0322
Email: dibycamael@gmail.com
LinkedIn: linkedin.com/in/macarthurdiby
GitHub: Camaelo26
License
This project is licensed under the Apache License 2.0. See the LICENSE file for more information.
