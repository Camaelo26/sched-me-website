from flask import Flask, request, render_template, redirect, url_for, flash, session
from mysql.connector import Error
from register import register_user,verify_password
from connection import create_connection
from update import update_doctor_inf,update_appointment_status,update_patient_info
from appointment import get_pending_appointments,cancel_appointment_by_patient,change_appointment_time,request_appointment,request_new_appointment_time,view_my_appointments,get_scheduled_appointments,get_all_appointments, review_pending_appointments_content
from department import get_doctors_by_department
import logging

app = Flask(__name__)
app.secret_key = 'Camelo123' 
logging.basicConfig(level=logging.DEBUG)


@app.route('/')
def home():
    return render_template('index.html')

#####
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


#####

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
            cursor.execute("SELECT UserID, PasswordHash, Role FROM users WHERE Username = %s", (username,))
            result = cursor.fetchone()
            if result:
                user_id, stored_password, role = result
                if verify_password(stored_password, password):
                    session['user_id'] = user_id
                    session['role'] = role
                    if role == 'Doctor':
                        cursor.execute("SELECT DoctorID FROM doctors WHERE UserID = %s", (user_id,))
                        doctor_result = cursor.fetchone()
                        if doctor_result:
                            session['doctor_id'] = doctor_result[0]
                            return redirect('/doctor/menu', code=302)
                        else:
                            flash('Doctor information not found.', 'error')
                    elif role == 'Patient':
                        cursor.execute("SELECT PatientID FROM patients WHERE UserID = %s", (user_id,))
                        patient_result = cursor.fetchone()
                        if patient_result:
                            session['patient_id'] = patient_result[0]
                            return redirect(url_for('patient_menu'))
                        else:
                            flash('Patient information not found.', 'error')
                    else:
                        flash('Unknown user role.', 'error')
                else:
                    flash('Invalid username or password', 'error')
            else:
                flash('Invalid username or password', 'error')
        except Exception as e:
            flash(str(e), 'error')
        finally:
            if connection.is_connected():
                connection.close()
    return render_template('login.html')
#####


@app.route('/doctor/menu')
def doctor_menu():
    if 'role' in session and session['role'] == 'Doctor':
        return render_template('doctor_menu.html')
    else:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('login'))

##########PATIENT##########

@app.route('/patient/menu')
def patient_menu():
    if 'role' in session and session['role'] == 'Patient':
        return render_template('patient_menu.html')
    else:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('login'))
    



@app.route('/view_appointments')
def view_appointments_route():
    patient_id = session.get('patient_id')
    if not patient_id:
        flash('No patient ID found in session.', 'error')
        return redirect(url_for('login'))

    appointments = view_my_appointments(create_connection(), patient_id)
    #print(f"Appointments passed to template for patient ID {patient_id}: {appointments}")

    return render_template('view_appointments.html', appointments=appointments)


@app.route('/update_info', methods=['GET', 'POST'])
def update_info_route():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['dob']
        gender = request.form['gender']
        contact_number = request.form['contact_number']
        address = request.form['address']
        email = request.form['email']
        update_patient_info(create_connection(), session['patient_id'], first_name, last_name, dob, gender, contact_number, address, email)
        return redirect(url_for('patient_menu'))
    return render_template('update_info.html')

@app.route('/change_appointment', methods=['GET', 'POST'])
def change_appointment_route():
    connection = create_connection()
    if request.method == 'POST':
        appointment_id = request.form['appointment_id']
        new_date = request.form['new_date']
        change_appointment_time(connection, session['patient_id'], appointment_id, new_date)
        return redirect(url_for('change_appointment_route'))
    
    pending_appointments = get_pending_appointments(connection, session['patient_id'])
    connection.close()
    return render_template('change_appointment.html', pending_appointments=pending_appointments)



@app.route('/request_appointment', methods=['GET', 'POST'])
def request_appointment_route():
    if request.method == 'POST':
        department_name = request.form.get('department_name')
        doctor_id = request.form.get('doctor_id')
        desired_date = request.form.get('desired_date')

        if department_name and not doctor_id:
            doctors = get_doctors_by_department(department_name)
            return render_template('request_appointment.html', department_name=department_name, doctors=doctors)

        if doctor_id and desired_date:
            patient_id = session.get('patient_id')  # Assuming the patient_id is stored in the session
            request_appointment(patient_id, doctor_id, desired_date)
            message = 'Appointment requested successfully!'
            return render_template('request_appointment.html', message=message)

    return render_template('request_appointment.html')



@app.route('/cancel_appointment', methods=['GET', 'POST'])
def cancel_appointment_route():
    connection = create_connection()
    if request.method == 'POST':
        appointment_id = request.form['appointment_id']
        cancel_appointment_by_patient(connection, session['patient_id'], appointment_id)
        return redirect(url_for('cancel_appointment_route'))
    
    appointments = get_all_appointments(connection, session['patient_id'])
    connection.close()
    return render_template('cancel_appointment.html', appointments=appointments)

@app.route('/request_new_time_route', methods=['GET', 'POST'])
def request_new_time_route():
    connection = create_connection()
    if request.method == 'POST':
        appointment_id = request.form['appointment_id']
        new_date = request.form['new_date']
        request_new_appointment_time(connection, session['patient_id'], appointment_id, new_date)
        return redirect(url_for('request_new_time_route'))
    
    scheduled_appointments = get_scheduled_appointments(connection, session['patient_id'])
    connection.close()
    return render_template('request_new_time.html', scheduled_appointments=scheduled_appointments)

########PATIENT MENU END##########

@app.route('/generic/menu')
def generic_menu():
    return 'Welcome to the Generic menu!'


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

        print("First Name:", first_name)
        print("Last Name:", last_name)
        print("Contact Number:", contact_number)


        if first_name != '' or last_name != '' or contact_number != '':
            print("Updating doctor information...")
            # Update the doctor information
            if update_doctor_inf(connection, doctor_id, first_name, last_name, contact_number,email):
                flash('Doctor information updated successfully.', 'success')
            else:
                flash('Failed to update doctor information.', 'error')
        else:
            flash('No changes submitted.', 'info')
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
