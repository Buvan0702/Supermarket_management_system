import customtkinter as ctk
from tkinter import messagebox
import mysql.connector
import hashlib
import subprocess
from PIL import Image

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

# ------------------- Verify Secret Key and Reset Password -------------------
def verify_and_reset_password():
    email = email_entry.get()
    secret_key = secret_key_entry.get()
    new_password = new_password_entry.get()
    confirm_password = confirm_password_entry.get()

    if not email or not secret_key or not new_password or not confirm_password:
        messagebox.showwarning("Input Error", "All fields are required.")
        return

    if new_password != confirm_password:
        messagebox.showwarning("Input Error", "New passwords do not match.")
        return

    try:
        connection = connect_db()
        cursor = connection.cursor()
        
        # Verify email and secret key
        cursor.execute(
            "SELECT user_id FROM Users WHERE username = %s AND secret_key = %s",
            (email, secret_key)
        )
        
        user = cursor.fetchone()
        
        if user:
            # Update password
            hashed_password = hash_password(new_password)
            cursor.execute(
                "UPDATE Users SET password = %s WHERE username = %s",
                (hashed_password, email)
            )
            
            connection.commit()
            messagebox.showinfo("Success", "Password has been reset successfully!")
            
            # Clear the input fields
            email_entry.delete(0, ctk.END)
            secret_key_entry.delete(0, ctk.END)
            new_password_entry.delete(0, ctk.END)
            confirm_password_entry.delete(0, ctk.END)
            
            # Return to login page
            root.destroy()
            subprocess.run(["python", "custom/login.py"])
        else:
            messagebox.showerror("Error", "Invalid email or secret key.")
            
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def open_login():
    root.destroy()
    subprocess.run(["python", "custom/login.py"])

# ---------------- Main Application Window ----------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("SuperMarket - Forgot Password")
root.geometry("1500x1000")
root.resizable(False, False)

# ---------------- Main Frame ----------------
main_frame = ctk.CTkFrame(root, fg_color="white", corner_radius=10)
main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.9)

# ---------------- Left Side (Form) ----------------
left_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=0)
left_frame.place(relx=0, rely=0, relwidth=0.5, relheight=1)

# SuperMarket Title
title_label = ctk.CTkLabel(left_frame, text="SuperMarket", 
                          font=("Arial", 28, "bold"), text_color="#2563eb")
title_label.place(relx=0.1, rely=0.1)

# Subtitle
subtitle_label = ctk.CTkLabel(left_frame, text="Reset your password\nusing your secret key.", 
                             font=("Arial", 14), text_color="gray")
subtitle_label.place(relx=0.1, rely=0.17)

# Reset Password Header
reset_header = ctk.CTkLabel(left_frame, text="Reset Password", 
                           font=("Arial", 18, "bold"), text_color="black")
reset_header.place(relx=0.1, rely=0.3)

# Reset Password Instruction
reset_instruction = ctk.CTkLabel(left_frame, text="Enter your email and secret key to reset your password.", 
                               font=("Arial", 14), text_color="gray")
reset_instruction.place(relx=0.1, rely=0.37)

# Email Label
email_label = ctk.CTkLabel(left_frame, text="Email", font=("Arial", 14), text_color="gray")
email_label.place(relx=0.1, rely=0.44)

# Email Entry
email_entry = ctk.CTkEntry(left_frame, font=("Arial", 14), height=40, width=300, 
                          border_color="#e5e7eb", border_width=1, corner_radius=5)
email_entry.place(relx=0.1, rely=0.48)

# Secret Key Label
secret_key_label = ctk.CTkLabel(left_frame, text="Secret Key", font=("Arial", 14), text_color="gray")
secret_key_label.place(relx=0.1, rely=0.54)

# Secret Key Entry
secret_key_entry = ctk.CTkEntry(left_frame, font=("Arial", 14), height=40, width=300, 
                               border_color="#e5e7eb", border_width=1, corner_radius=5)
secret_key_entry.place(relx=0.1, rely=0.58)

# New Password Label
new_password_label = ctk.CTkLabel(left_frame, text="New Password", font=("Arial", 14), text_color="gray")
new_password_label.place(relx=0.1, rely=0.64)

# New Password Entry
new_password_entry = ctk.CTkEntry(left_frame, font=("Arial", 14), height=40, width=300, 
                                 border_color="#e5e7eb", border_width=1, corner_radius=5, show="*")
new_password_entry.place(relx=0.1, rely=0.68)

# Confirm Password Label
confirm_password_label = ctk.CTkLabel(left_frame, text="Confirm Password", font=("Arial", 14), text_color="gray")
confirm_password_label.place(relx=0.1, rely=0.74)

# Confirm Password Entry
confirm_password_entry = ctk.CTkEntry(left_frame, font=("Arial", 14), height=40, width=300, 
                                     border_color="#e5e7eb", border_width=1, corner_radius=5, show="*")
confirm_password_entry.place(relx=0.1, rely=0.78)

# Reset Password Button
reset_btn = ctk.CTkButton(left_frame, text="Reset Password", font=("Arial", 14, "bold"), 
                         fg_color="#2563eb", hover_color="#1d4ed8",
                         height=40, width=300, corner_radius=5, command=verify_and_reset_password)
reset_btn.place(relx=0.1, rely=0.86)

# Back to Login text
login_label = ctk.CTkLabel(left_frame, text="Back to Login", 
                          font=("Arial", 14), text_color="#2563eb", cursor="hand2")
login_label.place(relx=0.1, rely=0.92)
login_label.bind("<Button-1>", lambda e: open_login())

# ---------------- Right Side (Image) ----------------
right_frame = ctk.CTkFrame(main_frame, fg_color="#EBF3FF", corner_radius=0)
right_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)

# Create a centered frame for the image
image_container = ctk.CTkFrame(right_frame, fg_color="#EBF3FF", corner_radius=5, width=252, height=252)
image_container.place(relx=0.5, rely=0.5, anchor="center")

# Load and display the shopping cart image
image_path = "./images/shopping.png"
try:
    img = ctk.CTkImage(light_image=Image.open(image_path), 
                       dark_image=Image.open(image_path),
                       size=(252, 252))
    
    image_label = ctk.CTkLabel(image_container, image=img, text="", bg_color="transparent")
    image_label.pack(fill="both", expand=True)
    
except Exception as e:
    print(f"Error loading image: {e}")
    error_label = ctk.CTkLabel(image_container, text="🛒", font=("Arial", 72), text_color="#2563eb")
    error_label.pack(pady=50)

# ---------------- Run Application ----------------
root.mainloop()
