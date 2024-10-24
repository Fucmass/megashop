from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_mysqldb import MySQL
import os
from config import Config  # Import your database config

# Define the path to the custom templates folder
template_path = os.path.join('Frontend', 'html', 'templates')
print(f"Template folder path: {template_path}")  # Debugging: Check the path

# Define the path to the static folder inside Frontend
static_path = os.path.join('Frontend', 'static')

# Initialize the Flask app with both the template and static folder paths
app = Flask(__name__, template_folder=template_path, static_folder=static_path)
app.config.from_object(Config)  # Load the DB config

# Initialize MySQL connection
mysql = MySQL(app)

# Route to serve JS files from the Backend/js directory
@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('Backend/js', filename)

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Route to add a user to the database
@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')
    phone_number = data.get('phone_number')

    # Basic validation
    if not all([first_name, last_name, email, password]):
        return jsonify({"error": "Missing required fields"}), 400

    # SQL query to insert user into the database
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            INSERT INTO users (first_name, last_name, password, email, phone_number) 
            VALUES (%s, %s, %s, %s, %s)
        """, (first_name, last_name, password, email, phone_number))
        mysql.connection.commit()
        return jsonify({"message": "User added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()

# Route to get all users from the database
@app.route('/users', methods=['GET'])
def get_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.close()

    return jsonify(users)

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change port if needed
