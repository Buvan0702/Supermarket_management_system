import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import mysql.connector
import hashlib
import os
import subprocess
import re

# ------------------- Database Connection -------------------
def connect_db():
    return mysql.connector.connect(
        host="141.209.241.57",
        user="kshat1m",
        password="mypass",  # Your actual database password
        database="BIS698W1700_GRP2"
    )

# ------------------- Password Hashing -------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ------------------- Password Strength Checker -------------------
def check_password_strength(password):
    """
    Check password strength and return (score, message)
    Score: 0-4 (0: very weak, 4: very strong)
    """
    if not password:
        return 0, "Password is required"
        
    score = 0
    feedback = []
    
    # Length check
    if len(password) < 8:
        feedback.append("Too short (min 8 characters)")
    else:
        score += 1
    
    # Complexity checks
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("Add uppercase letters")
        
    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append("Add lowercase letters")
        
    if re.search(r'[0-9]', password):
        score += 1
    else:
        feedback.append("Add numbers")
        
    if re.search(r'[^A-Za-z0-9]', password):
        score += 1
    else:
        feedback.append("Add special characters")
    
    # Determine message based on score
    if score == 0:
        return score, "Very weak password"
    elif score <= 2:
        return score, "Weak password: " + ", ".join(feedback[:2])
    elif score == 3:
        return score, "Moderate password"
    elif score == 4:
        return score, "Strong password"
    else:
        return score, "Very strong password"

# ------------------- Password Change Event -------------------
def on_password_change(event=None):
    password = password_entry.get()
    strength, message = check_password_strength(password)
    
    # Update strength label
    password_strength_label.configure(text=message)
    
    # Set color based on strength
    if strength == 0:
        password_strength_label.configure(text_color="red")
    elif strength <= 2:
        password_strength_label.configure(text_color="orange")
    elif strength == 3:
        password_strength_label.configure(text_color="blue")
    else:
        password_strength_label.configure(text_color="green")

# ------------------- Register User Function -------------------
def register_user():
    first_name = first_name_entry.get()
    last_name = last_name_entry.get()
    email = email_entry.get()
    password = password_entry.get()
    secret_key = secret_entry.get()

    if not first_name or not last_name or not email or not password or not secret_key:
        messagebox.showwarning("Input Error", "All fields are required.")
        return

    # Check password strength before registration
    strength, _ = check_password_strength(password)
    if strength <= 2:
        messagebox.showwarning("Weak Password", "Please choose a stronger password.")
        return
        
    # Validate email format
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        messagebox.showwarning("Invalid Email", "Please enter a valid email address.")
        return

    hashed_password = hash_password(password)

    try:
        connection = connect_db()
        cursor = connection.cursor()
        
        cursor.execute(
            "INSERT INTO Users (first_name, last_name, username, password, role, secret_key) VALUES (%s, %s, %s, %s, %s, %s)",
            (first_name, last_name, email, hashed_password, "user", secret_key)
        )
        
        connection.commit()
        messagebox.showinfo("Success", "User registered successfully!")
        
        # Clear the input fields
        first_name_entry.delete(0, ctk.END)
        last_name_entry.delete(0, ctk.END)
        email_entry.delete(0, ctk.END)
        password_entry.delete(0, ctk.END)
        secret_entry.delete(0, ctk.END)
        
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def open_login():
    root.destroy()  # Close signup window first
    subprocess.run(["python", "login.py"])  # Then run login.py

# ------------------- Responsive Layout Functions -------------------
def adjust_layout(event=None):
    """Adjust layout based on window size"""
    width = root.winfo_width()
    height = root.winfo_height()
    
    # Adjust main frame
    main_frame.place(relx=0.5, rely=0.5, anchor="center", 
                    relwidth=min(0.95, 1200/width) if width > 800 else 0.98, 
                    relheight=min(0.9, 900/height) if height > 700 else 0.98)
    
    # If window is narrow, stack the frames vertically
    if width < 1000:
        left_frame.place(relx=0, rely=0, relwidth=1, relheight=0.65)
        right_frame.place(relx=0, rely=0.65, relwidth=1, relheight=0.35)
        
        # Adjust form elements for narrower width
        form_width = min(300, width * 0.8)
        form_relx = 0.5
        form_rely_start = 0.12
        form_rely_step = 0.09
        anchor = "center"
        
        # Adjust image size
        img_scale = min(1.0, width/1000)
        if img:
            img.configure(size=(int(252 * img_scale), int(252 * img_scale)))
        
    else:
        # Side by side layout for wider windows
        left_frame.place(relx=0, rely=0, relwidth=0.5, relheight=1)
        right_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)
        
        form_width = min(300, (width * 0.5) * 0.8)
        form_relx = 0.1
        form_rely_start = 0.1
        form_rely_step = 0.06
        anchor = "w"
        
        # Reset image size
        if img:
            img.configure(size=(252, 252))
    
    # Adjust form elements
    title_label.place(relx=form_relx, rely=form_rely_start, anchor=anchor)
    subtitle_label.place(relx=form_relx, rely=form_rely_start + form_rely_step, anchor=anchor)
    account_header.place(relx=form_relx, rely=form_rely_start + form_rely_step * 3, anchor=anchor)
    signup_instruction.place(relx=form_relx, rely=form_rely_start + form_rely_step * 4, anchor=anchor)
    
    # Adjust all field positions based on the new layout
    field_rely = form_rely_start + form_rely_step * 5
    for field in [
        (first_name_label, first_name_entry),
        (last_name_label, last_name_entry),
        (email_label, email_entry),
        (secret_key_label, secret_entry),
        (password_label, password_entry)
    ]:
        label, entry = field
        label.place(relx=form_relx, rely=field_rely, anchor=anchor)
        entry.place(relx=form_relx, rely=field_rely + form_rely_step*0.6, anchor=anchor)
        entry.configure(width=form_width)
        field_rely += form_rely_step * 1.8
    
    # Place password strength label
    password_strength_label.place(relx=form_relx, rely=field_rely - form_rely_step, anchor=anchor)
    
    # Place buttons at the bottom
    signup_btn.place(relx=form_relx, rely=field_rely + form_rely_step*0.4, anchor=anchor)
    signup_btn.configure(width=form_width)
    login_label.place(relx=form_relx, rely=field_rely + form_rely_step*1.2, anchor=anchor)
    
    # Adjust image container
    if width < 1000:
        image_container.place(relx=0.5, rely=0.5, anchor="center")
    else:
        image_container.place(relx=0.5, rely=0.5, anchor="center")

# ---------------- Main Application Window ----------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("SuperMarket - Sign Up")
root.geometry("1500x1000")  # Starting size
root.minsize(700, 800)  # Minimum window size

# ---------------- Main Frame ----------------
main_frame = ctk.CTkFrame(root, fg_color="white", corner_radius=10)
main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.9)

# ---------------- Left Side (Signup Form) ----------------
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

# Create Account Header
account_header = ctk.CTkLabel(left_frame, text="Create your account", 
                           font=("Arial", 18, "bold"), text_color="black")
account_header.place(relx=0.1, rely=0.3)

# Signup Instruction
signup_instruction = ctk.CTkLabel(left_frame, text="Fill in the details below to sign up.", 
                               font=("Arial", 14), text_color="gray")
signup_instruction.place(relx=0.1, rely=0.37)

# First Name Label
first_name_label = ctk.CTkLabel(left_frame, text="First Name", font=("Arial", 14), text_color="gray")
first_name_label.place(relx=0.5, rely=0.30)

# First Name Entry
first_name_entry = ctk.CTkEntry(left_frame, font=("Arial", 14), height=40, width=300, 
                              border_color="#e5e7eb", border_width=1, corner_radius=5)
first_name_entry.place(relx=0.1, rely=0.48)

# Last Name Label
last_name_label = ctk.CTkLabel(left_frame, text="Last Name", font=("Arial", 14), text_color="gray")
last_name_label.place(relx=0.1, rely=0.54)

# Last Name Entry
last_name_entry = ctk.CTkEntry(left_frame, font=("Arial", 14), height=40, width=300, 
                             border_color="#e5e7eb", border_width=1, corner_radius=5)
last_name_entry.place(relx=0.1, rely=0.58)

# Email Label
email_label = ctk.CTkLabel(left_frame, text="Email", font=("Arial", 14), text_color="gray")
email_label.place(relx=0.1, rely=0.64)

# Email Entry
email_entry = ctk.CTkEntry(left_frame, font=("Arial", 14), height=40, width=300, 
                          border_color="#e5e7eb", border_width=1, corner_radius=5)
email_entry.place(relx=0.1, rely=0.68)

# Secret Key Label
secret_key_label = ctk.CTkLabel(left_frame, text="Secret Key", font=("Arial", 14), text_color="gray")
secret_key_label.place(relx=0.1, rely=0.74)

# Secret Key Entry
secret_entry = ctk.CTkEntry(left_frame, font=("Arial", 14), height=40, width=300, 
                          border_color="#e5e7eb", border_width=1, corner_radius=5)
secret_entry.place(relx=0.1, rely=0.78)

# Password Label
password_label = ctk.CTkLabel(left_frame, text="Password", font=("Arial", 14), text_color="gray")
password_label.place(relx=0.1, rely=0.84)

# Password Entry
password_entry = ctk.CTkEntry(left_frame, font=("Arial", 14), height=40, width=300, 
                             border_color="#e5e7eb", border_width=1, corner_radius=5, show="*")
password_entry.place(relx=0.1, rely=0.88)
password_entry.bind("<KeyRelease>", on_password_change)

# Password Strength Label
password_strength_label = ctk.CTkLabel(left_frame, text="", font=("Arial", 12), text_color="gray")
password_strength_label.place(relx=0.1, rely=0.92)

# Sign Up Button
signup_btn = ctk.CTkButton(left_frame, text="Sign Up", font=("Arial", 14, "bold"), 
                          fg_color="#2563eb", hover_color="#1d4ed8",
                          height=40, width=300, corner_radius=5, command=register_user)
signup_btn.place(relx=0.1, rely=0.94)

# Already have an account text
login_label = ctk.CTkLabel(left_frame, text="Already have an account? Login", 
                          font=("Arial", 14), text_color="#2563eb", cursor="hand2")
login_label.place(relx=0.1, rely=0.98)
login_label.bind("<Button-1>", lambda e: open_login())

# ---------------- Right Side (Image) ----------------
right_frame = ctk.CTkFrame(main_frame, fg_color="#EBF3FF", corner_radius=0)
right_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)

# Create a centered frame for the image
image_container = ctk.CTkFrame(right_frame, fg_color="#EBF3FF", corner_radius=5, width=252, height=252)
image_container.place(relx=0.5, rely=0.5, anchor="center")

# Load and display the shopping cart image with transparency
image_path = "./images/shopping.png"
img = None
try:
    # Create the CTkImage with transparency support
    img = ctk.CTkImage(light_image=Image.open(image_path), 
                       dark_image=Image.open(image_path),
                       size=(252, 252))
    
    # Create a label with transparent background
    image_label = ctk.CTkLabel(image_container, image=img, text="", bg_color="transparent")
    image_label.pack(fill="both", expand=True)
    
except Exception as e:
    print(f"Error loading image: {e}")
    error_label = ctk.CTkLabel(image_container, text="🛒", font=("Arial", 72), text_color="#2563eb")
    error_label.pack(pady=50)

# Bind resize event to adjust layout
root.bind("<Configure>", adjust_layout)

# Initial layout adjustment
root.update_idletasks()
adjust_layout()

# ---------------- Run Application ----------------
root.mainloop()