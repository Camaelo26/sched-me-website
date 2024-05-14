from mysql.connector import Error
from executequery import execute_query
from connection import create_connection

def add_department(connection, department_name):
    query = "INSERT INTO Departments (DepartmentName) VALUES (%s)"
    execute_query(connection, query, (department_name,))


def list_doctors_by_department(connection, department_name):
    cursor = connection.cursor()
    try:
        query = query = "SELECT id, first_name, last_name FROM doctors WHERE department = %s"
        cursor.execute(query, (department_name,))
        results = cursor.fetchall()
        print(f"Results before return: {results}")  # Add this debug line to check the results
        if results:
            print(f"Doctors fetched for department {department_name}: {results}")
        else:
            print(f"No doctors found for department {department_name}.")
        return results  # Ensure to return the results
    except Error as e:
        print(f"Error fetching doctors: {e}")
        return []
    finally:
        cursor.close()

def remove_department(connection, department_id):
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM Departments WHERE DepartmentID = %s", (department_id,))
        connection.commit()
        print("Department removed successfully.")
    except Error as e:
        print(f"Error removing department: {e}")
    finally:
        cursor.close()

def list_doctors_by_department(connection, department_name):

    cursor = connection.cursor()
    try:
        query = """
        SELECT Doctors.DoctorID, Doctors.FirstName, Doctors.LastName 
        FROM Doctors
        JOIN Departments ON Doctors.DepartmentID = Departments.DepartmentID
        WHERE Departments.DepartmentName = %s
        """
        cursor.execute(query, (department_name,))
        results = cursor.fetchall()

        if results:
            print(f"Doctors in the {department_name} Department:")
            for doctor in results:
                print(f"ID: {doctor[0]}, Name: {doctor[1]} {doctor[2]}")
        else:
            print(f"No doctors found in the {department_name} Department.")
    except Error as e:
        print(f"Error fetching doctors: {e}")
    finally:
        cursor.close()

def get_doctors_by_department(department_name):
    connection = create_connection()
    cursor = connection.cursor()
    query = """
    SELECT d.DoctorID, d.FirstName, d.LastName 
    FROM doctors d
    JOIN departments dept ON d.DepartmentID = dept.DepartmentID
    WHERE dept.DepartmentName = %s
    """
    cursor.execute(query, (department_name,))
    doctors = cursor.fetchall()
    cursor.close()
    connection.close()
    return doctors
