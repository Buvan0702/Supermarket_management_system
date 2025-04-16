import os

# Set environment variables for Tkinter
os.environ['TCL_LIBRARY'] = r"C:\Users\buvan\AppData\Local\Programs\Python\Python39\tcl\tcl8.6"
os.environ['TK_LIBRARY'] = r"C:\Users\buvan\AppData\Local\Programs\Python\Python39\tcl\tk8.6"

# ------------------- Database Configuration -------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "new_password",  # Update with your MySQL password
}

DB_NAME = "supermarket_management"

# Required images
REQUIRED_IMAGES = ["apple.png", "banana.png", "broccoli.png", "shopping.png"]

# File paths
CURRENT_USER_FILE = "current_user.txt"

# Version
APP_VERSION = "1.0"

# Application title
APP_TITLE = "SuperMarket Management System"