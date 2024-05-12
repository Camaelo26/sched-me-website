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

def review_pending_appointments_content(connection, doctor_id):
    cursor = connection.cursor()
    try:
        query = """
        SELECT AppointmentID, Patients.FirstName, Patients.LastName, AppointmentDate, Status
        FROM Appointments
        JOIN Patients ON Appointments.PatientID = Patients.PatientID
        WHERE DoctorID = %s
        ORDER BY AppointmentDate
        """
        cursor.execute(query, (doctor_id,))
        results = cursor.fetchall()

        if results:
            appointments = []
            for appt in results:
                appointment = {
                    "ID": appt[0],
                    "Patient": f"{appt[1]} {appt[2]}",
                    "Date": appt[3].strftime('%Y-%m-%d %H:%M:%S'),
                    "Status": appt[4]
                }
                appointments.append(appointment)
            return render_template('review_pending_appointments.html', appointments=appointments)
        else:
            message = "No pending appointments found for this doctor."
            return render_template('review_pending_appointments.html', message=message)
    except Error as e:
        flash(f"Error fetching appointments: {e}", 'error')
        return redirect(url_for('doctor_menu'))
    finally:
        cursor.close()


@app.route('/doctor/review_pending_appointments', methods=['GET', 'POST'])
def review_pending_appointments():
    doctor_id = session.get('doctor_id')
    connection = create_connection()
    if request.method == 'POST':
        appointment_id = request.form.get('appointment_id')
        new_status = request.form.get('new_status')
        update_appointment_status(connection, appointment_id, new_status)
        flash(f"Appointment ID {appointment_id} has been updated to {new_status}.", 'success')
        return redirect(url_for('review_pending_appointments'))
    else:
        return review_pending_appointments_content(connection, doctor_id)
    


@app.route('/doctor/update_info', methods=['GET', 'POST'])
def update_doctor_info():
    if 'user_id' not in session or 'role' not in session or session['role'] != 'Doctor':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('login'))

    doctor_user_id = session.get('user_id')  # User ID of the logged-in doctor
    
    # Fetch the DoctorID associated with the logged-in user ID
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT DoctorID FROM doctors WHERE UserID = %s", (doctor_user_id,))
    doctor = cursor.fetchone()
    if doctor is None:
        flash('Doctor information not found.', 'error')
        return redirect(url_for('login'))
    doctor_id = doctor['DoctorID']

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        contact_number = request.form.get('contact_number')
        email = request.form.get('email')

        # Check if any information is provided for update
        if not any((first_name, last_name, contact_number, email)):
            flash('No changes submitted.', 'info')
            return redirect(url_for('update_doctor_info'))

        # Update the doctor information
        if update_doctor_inf(connection, doctor_id, first_name, last_name, contact_number, email):
            flash('Doctor information updated successfully.', 'success')
        else:
            flash('Failed to update doctor information.', 'error')
        return redirect(url_for('update_doctor_info'))

    return render_template('update_doctor_info.html')

@app.route('/doctor/view_scheduled')
def view_scheduled_patient_info():
    if 'user_id' not in session or 'role' not in session or session['role'] != 'Doctor':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    connection = create_connection()

    cursor = connection.cursor(dictionary=True)
    try:
        # Fetching the doctor's ID based on the user ID
        cursor.execute("SELECT DoctorID FROM doctors WHERE UserID = %s", (user_id,))
        doctor = cursor.fetchone()
        if doctor:
            doctor_id = doctor['DoctorID']
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
        else:
            flash("Doctor not found.", 'error')
            return redirect(url_for('doctor_menu'))
    except Error as e:
        flash(f"Error fetching patient information: {e}", 'error')
        return redirect(url_for('doctor_menu'))
    finally:
        cursor.close()





if __name__ == '__main__':
    app.run(debug=True)
