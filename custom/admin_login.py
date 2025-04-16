import customtkinter as ctk
from tkinter import messagebox
import mysql.connector
import hashlib
import subprocess
import sys
import os

os.environ['TCL_LIBRARY'] = r"C:\Users\buvan\AppData\Local\Programs\Python\Python39\tcl\tcl8.6"
os.environ['TK_LIBRARY'] = r"C:\Users\buvan\AppData\Local\Programs\Python\Python39\tcl\tk8.6"

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="new_password",  # Your actual database password
        database="supermarket_management"
    )

def validate_login(username, password):
    # Hash the entered password for comparison
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute(
            "SELECT user_id, role FROM Users WHERE username = %s AND password = %s",
            (username, hashed_password)
        )
        
        user = cursor.fetchone()
        
        return user
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def handle_login():
    username = username_entry.get()
    password = password_entry.get()
    
    if not username or not password:
        messagebox.showwarning("Login Error", "Please enter both username and password.")
        return
    
    user = validate_login(username, password)
    
    if user:
        app.destroy()
        
        # Launch the appropriate interface based on user role
        if user["role"] == "admin":
            # Launch the unified admin interface
            subprocess.run(["python", "admin.py", username])
        else:
            # For non-admin users, launch the appropriate interface
            subprocess.run(["python", "main.py", username])
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

# Initialize the application
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("SuperMarket - Login")
app.geometry("400x500")
app.resizable(False, False)

# Center the window
window_width = 400
window_height = 500
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

position_top = int(screen_height / 2 - window_height / 2)
position_right = int(screen_width / 2 - window_width / 2)

app.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

# Main frame
main_frame = ctk.CTkFrame(app, fg_color="white", corner_radius=15)
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

# Logo or title
title_label = ctk.CTkLabel(main_frame, text="SuperMarket", 
                          font=("Arial", 30, "bold"), text_color="#2563eb")
title_label.pack(pady=(50, 10))

subtitle_label = ctk.CTkLabel(main_frame, text="Welcome back!", 
                             font=("Arial", 14), text_color="black")
subtitle_label.pack(pady=(0, 40))

# Username
username_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
username_frame.pack(fill="x", padx=30, pady=10)

username_label = ctk.CTkLabel(username_frame, text="Username", 
                             font=("Arial", 14), text_color="#4b5563")
username_label.pack(anchor="w")

username_entry = ctk.CTkEntry(username_frame, height=40, corner_radius=5,
                             placeholder_text="Enter your username")
username_entry.pack(fill="x", pady=(5, 0))

# Password
password_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
password_frame.pack(fill="x", padx=30, pady=10)

password_label = ctk.CTkLabel(password_frame, text="Password", 
                             font=("Arial", 14), text_color="#4b5563")
password_label.pack(anchor="w")

password_entry = ctk.CTkEntry(password_frame, height=40, corner_radius=5,
                             placeholder_text="Enter your password", show="•")
password_entry.pack(fill="x", pady=(5, 0))

# Login button
login_btn = ctk.CTkButton(main_frame, text="Login", 
                         font=("Arial", 14, "bold"), 
                         fg_color="#2563eb", hover_color="#1d4ed8",
                         height=45, corner_radius=5,
                         command=handle_login)
login_btn.pack(fill="x", padx=30, pady=(30, 10))

# Register link
register_label = ctk.CTkLabel(main_frame, text="Don't have an account? Register here", 
                             font=("Arial", 12), text_color="#2563eb", cursor="hand2")
register_label.pack(pady=(5, 0))

app.mainloop()