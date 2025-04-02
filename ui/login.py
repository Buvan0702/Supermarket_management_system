import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import mysql.connector
import hashlib
import os
import subprocess

os.environ['TCL_LIBRARY'] = r"C:\Users\buvan\AppData\Local\Programs\Python\Python39\tcl\tcl8.6"
os.environ['TK_LIBRARY'] = r"C:\Users\buvan\AppData\Local\Programs\Python\Python39\tcl\tk8.6"

# ------------------- Database Connection -------------------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="new_password",
        database="supermarket_management"
    )

# ------------------- Password Hashing -------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ------------------- Login Function -------------------
def login_user():
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showwarning("Input Error", "All fields are required.")
        return

    hashed_password = hash_password(password)

    try:
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT first_name, last_name, role FROM Users WHERE username = %s AND password = %s",
            (username, hashed_password)
        )
        user = cursor.fetchone()

        if user:
            first_name, last_name, role = user
            
            if role.lower() != "user":
                messagebox.showerror("Access Denied", "Only users can log in. Admin access is restricted.")
                return
            
            messagebox.showinfo("Success", f"Welcome {first_name} {last_name} ({role})!")

            # Launch home.py with username
            subprocess.Popen(["python", "home.py", username])
            root.destroy()
        else:
            messagebox.showerror("Error", "Invalid Username or Password")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def open_signup():
    root.destroy()
    subprocess.run(["python", "signup.py"])

# ------------------- Open Forgot Password Window -------------------
def open_forgot_password():
    subprocess.run(["python", "forgot_password.py"])

# ---------------- Main Application Window ----------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("SuperMarket - Login")
root.geometry("1000x600")  
root.resizable(False, False)

# ---------------- Main Frame ----------------
main_frame = ctk.CTkFrame(root, fg_color="white", corner_radius=10)
main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.9)

# ---------------- Left Side (Login Form) ----------------
left_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=0)
left_frame.place(relx=0, rely=0, relwidth=0.5, relheight=1)

# SuperMarket Title
title_label = ctk.CTkLabel(left_frame, text="SuperMarket", 
                          font=("Arial", 28, "bold"), text_color="#2563eb")
title_label.place(relx=0.1, rely=0.1)

# Subtitle
subtitle_label = ctk.CTkLabel(left_frame, text="Manage your shopping experience\nseamlessly.", 
                             font=("Arial", 14), text_color="gray")
subtitle_label.place(relx=0.1, rely=0.17)

# Login Details Header
login_header = ctk.CTkLabel(left_frame, text="Enter your login details", 
                           font=("Arial", 18, "bold"), text_color="black")
login_header.place(relx=0.1, rely=0.3)

# Login Instruction
login_instruction = ctk.CTkLabel(left_frame, text="Enter the registered credentials used\nwhile signing up", 
                               font=("Arial", 14), text_color="gray")
login_instruction.place(relx=0.1, rely=0.37)

# Username Label
username_label = ctk.CTkLabel(left_frame, text="Username", font=("Arial", 14), text_color="gray")
username_label.place(relx=0.1, rely=0.48)

# Username Entry
username_entry = ctk.CTkEntry(left_frame, font=("Arial", 14), height=40, width=350, 
                             border_color="#e5e7eb", border_width=1, corner_radius=5)
username_entry.place(relx=0.1, rely=0.53)

# Password Label
password_label = ctk.CTkLabel(left_frame, text="Password", font=("Arial", 14), text_color="gray")
password_label.place(relx=0.1, rely=0.61)

# Password Entry
password_entry = ctk.CTkEntry(left_frame, font=("Arial", 14), height=40, width=350, 
                             border_color="#e5e7eb", border_width=1, corner_radius=5, show="*")
password_entry.place(relx=0.1, rely=0.66)

# Login Button
login_btn = ctk.CTkButton(left_frame, text="Login", font=("Arial", 14, "bold"), 
                         fg_color="#2563eb", hover_color="#1d4ed8",
                         height=40, width=350, corner_radius=5, command=login_user)
login_btn.place(relx=0.1, rely=0.76)

# Sign Up Text
signup_label = ctk.CTkLabel(left_frame, text="Already have an account? Sign Up", 
                           font=("Arial", 14), text_color="#2563eb", cursor="hand2")
signup_label.place(relx=0.1, rely=0.84)
signup_label.bind("<Button-1>", lambda e: open_signup())

# Forgot Password
forgot_pwd_label = ctk.CTkLabel(left_frame, text="Forgot Password?", 
                              font=("Arial", 14), text_color="#2563eb", cursor="hand2")
forgot_pwd_label.place(relx=0.1, rely=0.89)
forgot_pwd_label.bind("<Button-1>", lambda e: open_forgot_password())

# ---------------- Right Side (Image) ----------------
right_frame = ctk.CTkFrame(main_frame, fg_color="#EBF3FF", corner_radius=0)
right_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)

# Create a centered frame for the image
image_container = ctk.CTkFrame(right_frame, fg_color="#EBF3FF", corner_radius=5, width=252, height=252)
image_container.place(relx=0.5, rely=0.5, anchor="center")

# Load and display the shopping cart image
image_path = "shopping.png"
try:
    img = ctk.CTkImage(light_image=Image.open(image_path), size=(252, 252))
    image_label = ctk.CTkLabel(image_container, image=img, text="")
    image_label.pack(fill="both", expand=True)
    
    # Size indicators (optional)
    size_label = ctk.CTkLabel(right_frame, text="252 × 252", font=("Arial", 10), text_color="gray")
    size_label.place(relx=0.5, rely=0.73, anchor="center")
    
except Exception as e:
    print(f"Error loading image: {e}")
    error_label = ctk.CTkLabel(image_container, text="🛒", font=("Arial", 72), text_color="#2563eb")
    error_label.pack(pady=50)

# ---------------- Run Application ----------------
root.mainloop()
