from mysql.connector import Error
from executequery import execute_query
from connection import create_connection
from flask import flash, render_template , redirect,url_for

def cancel_appointment(connection, appointment_id):
    query = "UPDATE Appointments SET Status = 'Cancelled' WHERE AppointmentID = %s"
    execute_query(connection, query, (appointment_id,))


def request_appointment(patient_id, doctor_id, appointment_date):
    connection = create_connection()
    cursor = connection.cursor()
    query = """
    INSERT INTO appointments (PatientID, DoctorID, AppointmentDate, Status)
    VALUES (%s, %s, %s, 'Pending')
    """
    cursor.execute(query, (patient_id, doctor_id, appointment_date))
    connection.commit()
    cursor.close()
    connection.close()


def view_my_appointments(connection, patient_id):
    cursor = connection.cursor()
    try:
        query = """
        SELECT 
            Appointments.AppointmentID, 
            Doctors.FirstName AS DoctorFirstName, 
            Doctors.LastName AS DoctorLastName, 
            Departments.DepartmentName,
            Appointments.AppointmentDate,
            Appointments.Status
        FROM 
            Appointments
        JOIN Doctors ON Appointments.DoctorID = Doctors.DoctorID
        JOIN Departments ON Doctors.DepartmentID = Departments.DepartmentID
        WHERE 
            Appointments.PatientID = %s
        ORDER BY 
            Appointments.AppointmentDate DESC
        """
        cursor.execute(query, (patient_id,))
        results = cursor.fetchall()

        if results:
            #print("\nYour Appointments:")
            for appointment in results:
                print(f"ID: {appointment[0]}, Doctor: {appointment[1]} {appointment[2]}, Department: {appointment[3]}, Date: {appointment[4]}, Status: {appointment[5]}")
            return results  # Ensure to return results
        else:
            #print("You have no appointments scheduled.")
            return []  # Return an empty list if no results
    except Error as e:
        #print(f"Error fetching appointments: {e}")
        return []
    finally:
        cursor.close()

def change_appointment_time(connection, patient_id, appointment_id, new_date):
    cursor = connection.cursor()
    try:
        # Check if the appointment is pending and belongs to the patient
        cursor.execute("SELECT Status FROM Appointments WHERE AppointmentID = %s AND PatientID = %s", (appointment_id, patient_id))
        result = cursor.fetchone()
        if result and result[0] == 'Pending':
            query = "UPDATE Appointments SET AppointmentDate = %s, Status = 'Pending' WHERE AppointmentID = %s"
            cursor.execute(query, (new_date, appointment_id))
            connection.commit()
            print("Appointment time changed successfully.")
            flash('Appointment time changed successfully.')
        else:
            print("Only pending appointments can be changed.")
            flash('Only pending appointments can be changed.')
    except Error as e:
        print(f"Error updating appointment: {e}")
    finally:
        cursor.close()

def get_all_appointments(connection, patient_id):
    cursor = connection.cursor()
    query = """
    SELECT a.AppointmentID, d.FirstName, d.LastName, dept.DepartmentName, a.AppointmentDate, a.Status
    FROM appointments a
    JOIN doctors d ON a.DoctorID = d.DoctorID
    JOIN departments dept ON d.DepartmentID = dept.DepartmentID
    WHERE a.PatientID = %s
    """
    cursor.execute(query, (patient_id,))
    appointments = cursor.fetchall()
    cursor.close()
    return appointments

def cancel_appointment_by_patient(connection, patient_id, appointment_id):
    cursor = connection.cursor()
    check_query = """
    SELECT Status FROM appointments 
    WHERE AppointmentID = %s AND PatientID = %s
    """
    cursor.execute(check_query, (appointment_id, patient_id))
    result = cursor.fetchone()
    if result and result[0] in ['Scheduled', 'Pending']:
        update_query = """
        UPDATE appointments
        SET Status = 'Cancelled'
        WHERE AppointmentID = %s AND PatientID = %s
        """
        cursor.execute(update_query, (appointment_id, patient_id))
        connection.commit()
        flash('Appointment cancelled successfully.')
    else:
        flash('Only scheduled or pending appointments can be cancelled.')
    cursor.close()


def get_pending_appointments(connection, patient_id):
    cursor = connection.cursor()
    query = """
    SELECT a.AppointmentID, d.FirstName, d.LastName, dept.DepartmentName, a.AppointmentDate
    FROM appointments a
    JOIN doctors d ON a.DoctorID = d.DoctorID
    JOIN departments dept ON d.DepartmentID = dept.DepartmentID
    WHERE a.PatientID = %s AND a.Status = 'Pending'
    """
    cursor.execute(query, (patient_id,))
    appointments = cursor.fetchall()
    cursor.close()
    return appointments


def request_new_appointment_time(connection, patient_id, appointment_id, new_date):
    cursor = connection.cursor()
    check_query = """
    SELECT Status FROM appointments 
    WHERE AppointmentID = %s AND PatientID = %s
    """
    cursor.execute(check_query, (appointment_id, patient_id))
    result = cursor.fetchone()
    if result and result[0] == 'Scheduled':
        update_query = """
        UPDATE appointments
        SET AppointmentDate = %s, Status = 'Pending'
        WHERE AppointmentID = %s AND PatientID = %s
        """
        cursor.execute(update_query, (new_date, appointment_id, patient_id))
        connection.commit()
        flash('New appointment time requested successfully.')
    else:
        flash('Only scheduled appointments can have a new time requested.')
    cursor.close()

def get_scheduled_appointments(connection, patient_id):
    cursor = connection.cursor()
    query = """
    SELECT a.AppointmentID, d.FirstName, d.LastName, dept.DepartmentName, a.AppointmentDate
    FROM appointments a
    JOIN doctors d ON a.DoctorID = d.DoctorID
    JOIN departments dept ON d.DepartmentID = dept.DepartmentID
    WHERE a.PatientID = %s AND a.Status = 'Scheduled'
    """
    cursor.execute(query, (patient_id,))
    appointments = cursor.fetchall()
    cursor.close()
    return appointments

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