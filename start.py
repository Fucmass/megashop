from flask import Flask, render_template, send_from_directory, request, jsonify, session, redirect, url_for
from functools import wraps
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


@app.route('/styles/<path:filename>')
def serve_styles(filename):
    return send_from_directory('frontend/static/css', filename)

# Route to serve JS files from the Backend/js directory
@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('Backend/js', filename)

# Custom authentication decorator
def is_authenticated(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/') # Redirect to login page
        return f(*args, **kwargs)
    return decorated_function

from functools import wraps
from flask import session, redirect
import mysql.connector

def is_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Ensure the database connection is established properly
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)  # Assuming `db` is a valid MySQL connection object
            user_id = session.get('user_id')  # Use `get` to avoid KeyError
            
            if not user_id:
                return redirect('/')  # Redirect if no user is logged in
            
            # Query to check user role
            cursor.execute("SELECT role FROM users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()  # Fetch one record
            
            # Check if the user is an admin
            if not user or user.get('role') != 'admin':
                return redirect('/')  # Redirect to the home page if not an admin
            
        except mysql.connector.Error as e:
            print(f"Database query failed: {e}")
            return redirect('/')  # Handle database errors gracefully
        finally:
            cursor.close()  # Ensure cursor is always closed

        # Call the wrapped function if the user is an admin
        return f(*args, **kwargs)
    
    return decorated_function


# Home route
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shop')
def shop():
    db = get_db_connection()
    if db:
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT product_id, brand, product_name, price, stock FROM products")
            products = cursor.fetchall()  # Fetch all products as a list of dictionaries
        except mysql.connector.Error as e:
            print(f"Database query failed: {e}")
            products = []
        finally:
            cursor.close()
            db.close()
    else:
        products = []

    return render_template('shop.html', products=products)

@app.route('/products/<int:product_id>')
def load_product(product_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)  # Use dictionary=True for row as dict
        cursor.execute('SELECT * FROM products WHERE product_id = %s', (product_id,))
        products = cursor.fetchone()
        cursor.close()
    finally:
        conn.close()

    if products is None:
        return jsonify({"error": "Product Not Found"}), 404

    # Pass the item data to the HTML template
    return render_template('products.html', products=products)

@app.route('/profile')
@is_authenticated
def profile():
    # Get the user role from the database based on session['user_id']
    user_id = session.get('user_id')
    db = get_db_connection()
    if db:
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT role FROM users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()
            if user:
                role = user['role']
            else:
                role = None
        except mysql.connector.Error as e:
            print(f"Database query failed: {e}")
            role = None
        finally:
            cursor.close()
            db.close()
    else:
        role = None

    return render_template('profile.html', role=role)

@app.route('/add_product')
@is_admin
def addProdDisplay():
    return render_template('add_product.html')

@app.route('/add_product', methods=['POST'])
def add_product():
    try:
        # Parse JSON data from the request
        product_info = request.json
        brand = product_info.get('brand')
        product_name = product_info.get('product_name')
        price = product_info.get('price')
        stock = product_info.get('stock')
        image = product_info.get('image')

        # Validate inputs
        if not all([brand, product_name, price, stock, image]):
            return jsonify({"error": "All fields are required"}), 400

        # Connect to the database
        db = get_db_connection()
        if db:
            cursor = db.cursor(dictionary=True)
            try:
                # Check if the product already exists
                cursor.execute("SELECT * FROM products WHERE product_name = %s", (product_name,))
                existing_user = cursor.fetchone()
                if existing_user:
                    return jsonify({"error": "User with this email already exists"}), 409

                # Insert new product into the database
                cursor.execute(
                    """
                    INSERT INTO products (brand, product_name, price, stock, image)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (brand, product_name, price, stock, image)
                )
                db.commit()

                return jsonify({"message": "product added successfully"}), 201
            except mysql.connector.Error as e:
                return jsonify({"error": f"Database operation failed: {e}"}), 500
            finally:
                cursor.close()
                db.close()
        else:
            return jsonify({"error": "Database connection failed"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

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
@is_authenticated
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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
