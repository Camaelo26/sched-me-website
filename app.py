from flask import Flask, request, render_template, redirect, url_for, flash, session
from mysql.connector import Error
from register import register_user,verify_password
from connection import create_connection
import logging

app = Flask(__name__)
app.secret_key = 'Camelo123' 
logging.basicConfig(level=logging.DEBUG)


@app.route('/')
def home():
    return render_template('index.html')

# Adjust the signup route to pass form directly
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        connection = create_connection()
        if connection is None:
            return "Error connecting to the database", 500

        # Log received form data for debugging
        app.logger.debug(f"Received form data: {request.form}")

        # Register user and handle errors or success
        if register_user(connection, request.form):
            return redirect(url_for('home'))
        else:
            app.logger.debug(f"Failed registration with data: {request.form}")
            return "Registration failed, please try again.", 500
    else:
        return render_template('sign_up.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('login.html')

        connection = create_connection()
        try:
            cursor = connection.cursor(buffered=True)
            cursor.execute("SELECT UserID, PasswordHash, Role FROM Users WHERE Username = %s", (username,))
            result = cursor.fetchone()
            if result:
                user_id, stored_password, role = result
                print(f"Role: {role}, User ID: {user_id}")  # Debugging print statement
                try:
                    if verify_password(stored_password, password):
                        session['user_id'] = user_id
                        session['role'] = role
                        if role == 'Doctor':
                            print("Redirecting to doctor's menu")
                            print("Session Role:", session.get('role'))
                            return redirect('/doctor/menu', code=302)
                        elif role == 'Patient':
                            print("Redirecting to patient's menu")
                            return redirect(url_for('patient_menu'))
                        else:
                            print("Redirecting to generic menu")
                            return redirect(url_for('generic_menu'))
                    else:
                        flash('Invalid username or password', 'error')
                        print("invalid password or password")
                except Exception as e:
                    flash(str(e), 'error')
            else:
                flash('Invalid username or password', 'error')
                print("invalid password or password")
        except Exception as e:
            flash(str(e), 'error')
        finally:
            if connection.is_connected():
                connection.close()
            
    else:
        return render_template('login.html')




@app.route('/doctor/menu')
def doctor_menu():
    if 'role' in session and session['role'] == 'Doctor':
        return render_template('doctor_menu.html')
    else:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('login'))



@app.route('/patient/menu')
def patient_menu():
    if 'role' in session and session['role'] == 'Patient':
        return 'Welcome to the Patient menu!'
    flash('Unauthorized access.', 'error')
    return redirect(url_for('login'))

@app.route('/generic/menu')
def generic_menu():
    return 'Welcome to the Generic menu!'

@app.route('/doctor/review_appointments')
def review_appointments():
    doctor_id = session.get('doctor_id')
    connection = create_connection()
    # Assuming review_appointments function returns HTML content or a redirect
    return review_appointments(connection, doctor_id)

@app.route('/doctor/update_info', methods=['GET', 'POST'])
def update_doctor_info():
    doctor_id = session.get('doctor_id')
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        contact_number = request.form.get('contact_number')
        email = request.form.get('email')
        connection = create_connection()
        # Assuming update_doctor_info is your function that updates the database
        update_doctor_info(connection, doctor_id, first_name, last_name, contact_number, email)
        return redirect(url_for('doctor_menu'))
    return render_template('update_doctor_info.html')

@app.route('/doctor/view_scheduled')
def view_scheduled_patient_info():
    if 'user_id' not in session or 'role' not in session or session['role'] != 'Doctor':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('login'))

    doctor_id = session.get('user_id')
    connection = create_connection()

    cursor = connection.cursor(dictionary=True)
    try:
        query = """
        SELECT 
            Patients.PatientID, 
            Patients.FirstName, 
            Patients.LastName, 
            Patients.DateOfBirth, 
            Patients.Gender, 
            Patients.ContactNumber, 
            Patients.Address, 
            Patients.Email,
            Appointments.AppointmentDate
        FROM 
            Appointments
        JOIN 
            Patients ON Appointments.PatientID = Patients.PatientID
        WHERE 
            Appointments.DoctorID = %s AND Appointments.Status = 'Scheduled'
        ORDER BY 
            Appointments.AppointmentDate
        """
        cursor.execute(query, (doctor_id,))
        results = cursor.fetchall()
        return render_template('view_scheduled.html', appointments=results)
    except Error as e:
        flash(f"Error fetching patient information: {e}", 'error')
        return redirect(url_for('doctor_menu'))
    finally:
        cursor.close()





if __name__ == '__main__':
    app.run(debug=True)
