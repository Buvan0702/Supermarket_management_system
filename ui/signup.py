import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import mysql.connector
import hashlib
import os
os.environ['TCL_LIBRARY'] = r"C:\Users\buvan\AppData\Local\Programs\Python\Python39\tcl\tcl8.6"
os.environ['TK_LIBRARY'] = r"C:\Users\buvan\AppData\Local\Programs\Python\Python39\tcl\tk8.6"

# ------------------- Database Connection -------------------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="new_password",  # Replace with your MySQL password
        database="supermarket_management"
    )

# ------------------- Password Hashing -------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ------------------- Register User Function -------------------
def register_user():
    first_name = first_name_entry.get()
    last_name = last_name_entry.get()
    username = username_entry.get()
    email = email_entry.get()
    password = password_entry.get()

    if not first_name or not last_name or not username or not email or not password:
        messagebox.showwarning("Input Error", "All fields are required.")
        return

    hashed_password = hash_password(password)

    try:
        connection = connect_db()
        cursor = connection.cursor()
        
        cursor.execute(
            "INSERT INTO Users (first_name, last_name, username, password, role) VALUES (%s, %s, %s, %s, %s)",
            (first_name, last_name, username, hashed_password, "user")
        )
        
        connection.commit()
        messagebox.showinfo("Success", "User registered successfully!")
        
        # Clear the input fields
        first_name_entry.delete(0, ctk.END)
        last_name_entry.delete(0, ctk.END)
        username_entry.delete(0, ctk.END)
        email_entry.delete(0, ctk.END)
        password_entry.delete(0, ctk.END)
        
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# ---------------- Main Application Window ----------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("SuperMarket - Sign Up")
root.geometry("800x500")
root.resizable(False, False)

# ---------------- Main Frame ----------------
main_frame = ctk.CTkFrame(root, fg_color="white", corner_radius=10)
main_frame.place(relx=0.5, rely=0.5, anchor="center")

# ---------------- Left Side - Image ----------------
left_frame = ctk.CTkFrame(main_frame, fg_color="white", width=350, height=420, corner_radius=10)
left_frame.pack(side="left", fill="both", padx=10, pady=10)

# Load and display an image
image_path = "signup.png"  # Replace with your image file path
try:
    img = ctk.CTkImage(light_image=Image.open(image_path), size=(300, 300))
    image_label = ctk.CTkLabel(left_frame, image=img, text="")
    image_label.pack(pady=20)
except:
    ctk.CTkLabel(left_frame, text="🛍 Sign Up Now!", font=("Arial", 20, "bold"), text_color="#2563eb").pack(pady=80)

# ---------------- Right Side - Signup Form ----------------
right_frame = ctk.CTkFrame(main_frame, fg_color="white", width=350, height=420, corner_radius=10)
right_frame.pack(side="right", fill="both", padx=10, pady=10)

ctk.CTkLabel(right_frame, text="Create an Account", font=("Arial", 18, "bold")).pack(pady=(20, 5))

# --- First Name Entry ---
ctk.CTkLabel(right_frame, text="First Name", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
first_name_entry = ctk.CTkEntry(right_frame, font=("Arial", 12), height=35)
first_name_entry.pack(fill="x", pady=5)

# --- Last Name Entry ---
ctk.CTkLabel(right_frame, text="Last Name", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
last_name_entry = ctk.CTkEntry(right_frame, font=("Arial", 12), height=35)
last_name_entry.pack(fill="x", pady=5)

# --- Username Entry ---
ctk.CTkLabel(right_frame, text="Username", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
username_entry = ctk.CTkEntry(right_frame, font=("Arial", 12), height=35)
username_entry.pack(fill="x", pady=5)

# --- Email Entry ---
ctk.CTkLabel(right_frame, text="Email", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
email_entry = ctk.CTkEntry(right_frame, font=("Arial", 12), height=35)
email_entry.pack(fill="x", pady=5)

# --- Password Entry with Toggle ---
ctk.CTkLabel(right_frame, text="Password", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
password_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
password_frame.pack(fill="x", pady=5)

password_entry = ctk.CTkEntry(password_frame, font=("Arial", 12), height=35, show="*")
password_entry.pack(side="left", fill="x", expand=True)

toggle_btn = ctk.CTkButton(password_frame, text="🔒", width=30, height=30, fg_color="gray")
toggle_btn.pack(side="right", padx=5)

# --- Register Button ---
register_btn = ctk.CTkButton(right_frame, text="Sign Up", font=("Arial", 13, "bold"), fg_color="#2563eb",
                              height=40, corner_radius=5, command=register_user)
register_btn.pack(fill="x", pady=(15, 10))

# ---------------- Run Application ----------------
root.mainloop()
