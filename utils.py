import mysql.connector
from tkinter import messagebox
import os
import shutil
import hashlib
import sys
from config import DB_CONFIG, DB_NAME, REQUIRED_IMAGES, CURRENT_USER_FILE

# ------------------- Database Functions -------------------
def connect_db(database=None):
    """Connect to MySQL with or without specifying a database"""
    config = DB_CONFIG.copy()
    if database:
        config["database"] = database
    
    try:
        return mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            return None  # Database doesn't exist
        elif err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            messagebox.showerror("Database Error", 
                               "Access denied. Please check your MySQL username and password.")
            return None
        else:
            messagebox.showerror("Database Error", str(err))
            return None

def setup_database():
    """Create and set up the database with all required tables"""
    # First connect without specifying database
    conn = connect_db()
    if not conn:
        messagebox.showerror("Database Error", "Failed to connect to MySQL server")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        print(f"Creating database: {DB_NAME}")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")
        
        print("Creating Users table")
        # Create Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL,
            email VARCHAR(100),
            secret_key VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        print("Creating Products table")
        # Create Products table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Products (
            product_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            stock INT NOT NULL DEFAULT 0,
            image_path VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        print("Creating Carts table")
        # Create Carts table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Carts (
            cart_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) NOT NULL DEFAULT 'active',
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
        """)
        
        print("Creating CartItems table")
        # Create CartItems table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS CartItems (
            cart_item_id INT AUTO_INCREMENT PRIMARY KEY,
            cart_id INT NOT NULL,
            product_id INT NOT NULL,
            quantity INT NOT NULL DEFAULT 1,
            FOREIGN KEY (cart_id) REFERENCES Carts(cart_id),
            FOREIGN KEY (product_id) REFERENCES Products(product_id)
        )
        """)
        
        print("Creating Orders table")
        # Create Orders table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Orders (
            order_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            cart_id INT NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_amount DECIMAL(10, 2) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES Users(user_id),
            FOREIGN KEY (cart_id) REFERENCES Carts(cart_id)
        )
        """)
        
        conn.commit()
        print("Database tables created successfully")
        
        # Create default users and products
        create_default_user()
        create_default_products()
        
        return True
        
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")
        messagebox.showerror("Database Setup Error", str(err))
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def create_default_user():
    """Create a default admin user if no users exist"""
    try:
        conn = connect_db(DB_NAME)
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Check if users already exist
        cursor.execute("SELECT COUNT(*) FROM Users")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("Creating default users")
            # Create an admin user
            hashed_password = hashlib.sha256("admin123".encode()).hexdigest()
            cursor.execute("""
            INSERT INTO Users (first_name, last_name, username, email, password, role)
            VALUES ('Admin', 'User', 'admin123', 'admin@supermarket.com', %s, 'admin')
            """, (hashed_password,))
            
            # Create a regular user
            hashed_password = hashlib.sha256("user123".encode()).hexdigest()
            cursor.execute("""
            INSERT INTO Users (first_name, last_name, username, email, password, role)
            VALUES ('John', 'Doe', 'user1', 'user1@example.com', %s, 'user')
            """, (hashed_password,))
            
            conn.commit()
            print("Default users created successfully")
            return True
        
        print("Users already exist, skipping default user creation")
        return True
    
    except mysql.connector.Error as err:
        print(f"Error creating default users: {err}")
        messagebox.showerror("Database Error", str(err))
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def create_default_products():
    """Create default products if no products exist"""
    try:
        conn = connect_db(DB_NAME)
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Check if products already exist
        cursor.execute("SELECT COUNT(*) FROM Products")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("Creating default products")
            # Insert some default products
            products = [
                ("Fresh Apples", 2.00, 50, "custom/images/apple.png"),
                ("Organic Bananas", 1.50, 30, "custom/images/banana.png"),
                ("Fresh Broccoli", 1.80, 25, "custom/images/broccoli.png"),
                ("Whole Wheat Bread", 2.50, 20, None),
                ("Almond Milk", 3.00, 15, None),
                ("Eggs", 2.00, 40, None),
                ("Chicken Breast", 8.00, 10, None),
                ("Brown Rice", 2.00, 35, None)
            ]
            
            for product in products:
                cursor.execute("""
                INSERT INTO Products (name, price, stock, image_path)
                VALUES (%s, %s, %s, %s)
                """, product)
            
            conn.commit()
            print("Default products created successfully")
            return True
        
        print("Products already exist, skipping default product creation")
        return True
    
    except mysql.connector.Error as err:
        print(f"Error creating default products: {err}")
        messagebox.showerror("Database Error", str(err))
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# ------------------- File Operations -------------------
def check_image_files():
    """Check if required image files exist, copy from backup if needed"""
    # Check if images folder exists, create if not
    if not os.path.exists("custom/images"):
        os.makedirs("custom/images")
    
    # Check each required image
    for image in REQUIRED_IMAGES:
        if not os.path.exists(image):
            # Look for image in images folder
            if os.path.exists(os.path.join("images", image)):
                # Copy from images folder to current directory
                shutil.copy(os.path.join("images", image), image)
            else:
                print(f"Warning: Image file {image} not found")

def write_login_file(username, role="user"):
    """Write login info to a temporary file for other scripts to use"""
    try:
        with open(CURRENT_USER_FILE, "w") as f:
            f.write(f"{username}\n{role}")
        return True
    except Exception as e:
        print(f"Error writing login file: {e}")
        return False

def read_login_file():
    """Read login info from temporary file"""
    try:
        if os.path.exists(CURRENT_USER_FILE):
            with open(CURRENT_USER_FILE, "r") as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    return lines[0].strip(), lines[1].strip()
        return None, None
    except Exception as e:
        print(f"Error reading login file: {e}")
        return None, None

def check_database_connection():
    """Check database connection and setup"""
    print("Checking database connection...")
    conn = connect_db()
    if conn:
        conn.close()
        print("Connected to MySQL successfully")
        return True
    else:
        print("Failed to connect to MySQL")
        return False
        
def initialize_system():
    """Initialize the system - database, files, etc."""
    # Check database connection
    if not check_database_connection():
        print("Failed to connect to MySQL, exiting")
        return False
    
    # Setup database and tables
    print("Setting up database...")
    if not setup_database():
        print("Failed to setup database, exiting")
        messagebox.showerror("Database Error", "Failed to setup database tables")
        return False
    
    # Check required image files
    print("Checking image files...")
    check_image_files()
    
    return True