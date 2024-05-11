import hashlib
from flask import Flask
#from executequery import execute_query
import os
import mysql.connector

app = Flask(__name__)

def verify_password(stored_password, provided_password):
    salt = stored_password[:32]
    stored_key = stored_password[32:]
    new_key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    return stored_key == new_key

def hash_password(password):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt + key

def register_user(connection, form_data):
    cursor = connection.cursor()
    try:
        # Begin transaction
        connection.start_transaction()

        # Filter out empty duplicates by taking the first non-empty value for each key
        cleaned_data = {}
        for key in form_data:
            if form_data.getlist(key):  # Get list of all values for each key
                cleaned_data[key] = next((item for item in form_data.getlist(key) if item.strip()), '')

        # Extract cleaned form data
        username = cleaned_data['username']
        password = cleaned_data['password']
        role = cleaned_data['role']
        first_name = cleaned_data['first_name']
        last_name = cleaned_data['last_name']
        email = cleaned_data['email'].strip()

        # Validate email is not empty for doctors
        if role.lower() == 'doctor' and not email:
            app.logger.error("Email is required for doctors and cannot be empty.")
            return False

        # Insert user into 'users' table
        user_query = "INSERT INTO users (Username, PasswordHash, Role) VALUES (%s, %s, %s)"
        cursor.execute(user_query, (username, password, role))
        user_id = cursor.lastrowid

        # Insert specific role information
        if role.lower() == 'patient':
            patient_query = """
            INSERT INTO patients (UserID, FirstName, LastName, DateOfBirth, Gender, ContactNumber, Address, Email) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(patient_query, (user_id, first_name, last_name,
                                           cleaned_data.get('dob', '0000-00-00'),
                                           cleaned_data.get('gender', 'Male'),
                                           cleaned_data.get('contact_number', ''),
                                           cleaned_data.get('address', ''), email))

        elif role.lower() == 'doctor':
            doctor_query = """
            INSERT INTO doctors (UserID, FirstName, LastName, DepartmentID, ContactNumber, Email) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(doctor_query, (user_id, first_name, last_name,
                                          cleaned_data.get('department_id', ''),
                                          cleaned_data.get('contact_number', ''), email))

        # Commit transaction
        connection.commit()
        app.logger.info("User registered successfully")
        return True
    except mysql.connector.Error as e:
        # Roll back transaction
        connection.rollback()
        app.logger.error(f"SQL Error: {e}")
        return False
    finally:
        cursor.close()


def collect_additional_info(role, request):
    if role.lower() == 'patient':
        return (
            request.form.get('dob', '0000-00-00'),
            request.form.get('gender', 'Male'),
            request.form.get('contact_number', ''),
            request.form.get('address', ''),
            request.form.get('email', '')
        )
    elif role.lower() == 'doctor':
        return (
            request.form.get('department_id', ''),
            request.form.get('contact_number', ''),
            request.form.get('email', '')
        )
