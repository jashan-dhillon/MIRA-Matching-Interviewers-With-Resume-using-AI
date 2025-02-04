from flask import Flask, request, jsonify, render_template
import mysql.connector

app = Flask(__name__)

# Database configuration
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'sqlpass@135',
    'database': 'mira_db'
}

# import mysql.connector

try:
    conn = mysql.connector.connect(**db_config)
    print("Connected successfully!")
except mysql.connector.Error as err:
    print(f"Error: {err}")


try:
    conn = mysql.connector.connect(**db_config)
    if conn.is_connected():
        print("Connected to the database!")
except mysql.connector.Error as err:
    print(f"Database connection error: {err}")


# Route for the Sign-Up form

@app.route('/')
def home():
    return render_template('signup.html')  # Removed the 'methods' parameter here

# Route to handle form submission
@app.route('/sign-up', methods=['POST'])
def sign_up():
    if request.method == 'POST':
    # Connect to the database
      conn = mysql.connector.connect(**db_config)
      cursor = conn.cursor()
      role = request.form.get('role')
      first_name = request.form.get('first_name')
      last_name = request.form.get('last_name')
      password = request.form.get('password')
      department = request.form.get('department')
    
    # Role-specific fields
      email = request.form.get('email') or None
      phone_number = request.form.get('phone_number') or None
      department = request.form.get('department') or None
      employee_id = request.form.get('employee_id') or None
      current_post = request.form.get('current_post') or None
      department_hr = request.form.get('department_hr') or None
      employee_id_hr = request.form.get('employee_id_hr') or None
      current_post_hr = request.form.get('current_post_hr') or None

    # Insert data into the database based on role
    if role == "applicant":
        query = "INSERT INTO applicants01 (first_name, last_name, password, email, phone_number) VALUES (%s, %s, %s, %s, %s)"

        # query = "INSERT INTO applicants (first_name, last_name,password, email, phone_number)) VALUES (%s,%s, %s, %s, %s)"
        cursor.execute(query, (first_name, last_name,password, email, phone_number))
    elif role == "expert":
        query = "INSERT INTO experts (first_name, last_name, password, department, employee_id, current_post) VALUES (%s,%s, %s, %s, %s, %s)"
        cursor.execute(query, (first_name, last_name, password,department, employee_id, current_post))
    elif role == "hr":
        query = "INSERT INTO hr (first_name, last_name, password, department, employee_id, current_post) VALUES (%s,%s, %s, %s, %s, %s)"
        cursor.execute(query, (first_name, last_name, password, department_hr, employee_id_hr, current_post_hr))
    
    # Commit the transaction and close the connection
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'User successfully registered!'}), 200

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
