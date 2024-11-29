from flask import Flask, render_template, send_from_directory, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
import mysql.connector
import os
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

# Define paths for custom templates and static files
template_path = os.path.join('Frontend', 'html', 'templates')
static_path = os.path.join('Frontend', 'static')

# Initialize Flask app
app = Flask(__name__, template_folder=template_path, static_folder=static_path)

# Secret key for session management
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

# Secure session cookie settings
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

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

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

# Login route
@app.route('/login', methods=['POST'])
def login():
    login_info = request.json
    email = login_info.get('email')
    password = login_info.get('password')

    if not all([email, password]):
        return jsonify({"error": "Email and password are required"}), 400

    db = get_db_connection()
    if db:
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user or not check_password_hash(user['password'], password):
                return jsonify({"error": "Invalid credentials"}), 401

            # Check if 'id' key exists
            if 'user_id' in user:
                session['user_id'] = user['user_id']
                session['email'] = user['email']
                session['first_name'] = user.get('first_name', 'Guest')  # Default if missing

                return jsonify({"message": "Login successful!"}), 200
            else:
                return jsonify({"error": "User data is incomplete"}), 500

        except mysql.connector.Error as e:
            return jsonify({"error": f"Database operation failed: {e}"}), 500
        finally:
            cursor.close()
            db.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/logout', methods=['GET'])
def logout_page():
    return render_template('logout.html')

# Logout route
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully!"}), 200

# Route to check if user is logged in
@app.route('/is_logged_in', methods=['GET'])
def is_logged_in():
    if 'user_id' in session:
        return jsonify({
            "message": "User is logged in",
            "user": {
                "id": session['user_id'],
                "email": session['email'],
                "first_name": session['first_name']
            }
        }), 200
    return jsonify({"message": "User is not logged in"}), 401



# Route to render the signup page
@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

# Route to handle signup form submission
@app.route('/signup', methods=['POST'])
def signup():
    try:
        # Parse JSON data from the request
        signup_info = request.json
        first_name = signup_info.get('first_name')
        last_name = signup_info.get('last_name')
        email = signup_info.get('email')
        password = signup_info.get('password')
        phone_number = signup_info.get('phone_number')

        # Validate inputs
        if not all([first_name, last_name, email, password, phone_number]):
            return jsonify({"error": "All fields are required"}), 400

        # Hash the password
        hashed_password = generate_password_hash(password)

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
                    (first_name, last_name, email, hashed_password, phone_number)
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
    app.run(host="0.0.0.0", port=5000, debug=True)
