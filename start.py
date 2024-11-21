from flask import Flask, render_template, send_from_directory, request, jsonify
from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()

# Define the path to the custom templates and static folders
template_path = os.path.join('Frontend', 'html', 'templates')
static_path = os.path.join('Frontend', 'static')

# Initialize the Flask app
app = Flask(__name__, template_folder=template_path, static_folder=static_path)

# Database configuration
db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_DATABASE')
}

# Function to get a database connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to database: {e}")
        return None

# Route to serve JS files from the Backend/js directory
@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('Backend/js', filename)

# Home route
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

# Route to render the signup page
@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

# Route to handle signup form submission
@app.route('/signup', methods=['POST'])
def signup():
    try:
        # Parse JSON data from the request
        signup_info = request.json  # Corrected variable name
        first_name = signup_info.get('first_name')
        last_name = signup_info.get('last_name')
        email = signup_info.get('email')
        password = signup_info.get('password')
        phone_number = signup_info.get('phone_number')


        # Validate inputs
        if not all([first_name, last_name, email, password, phone_number]):
            return jsonify({"error": "All fields are required"}), 400

        # Connect to the database
        db = get_db_connection()
        if db:
            cursor = db.cursor(dictionary=True)
            try:
                # Check if the user already exists
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                existing_user = cursor.fetchone()
                if existing_user:
                    return jsonify({"error": "User with this email already exists"}), 409


                # Insert new user into the database
                cursor.execute(
                    """
                    INSERT INTO users (first_name, last_name, email, password, phone_number)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (first_name, last_name, email, password, phone_number)
                )
                db.commit()

                return jsonify({"message": "User registered successfully"}), 201
            except mysql.connector.Error as e:
                return jsonify({"error": f"Database operation failed: {e}"}), 500
            finally:
                cursor.close()
                db.close()
        else:
            return jsonify({"error": "Database connection failed"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
