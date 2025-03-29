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
        password="new_password",
        database="supermarket_management"
    )

# ------------------- Password Hashing -------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ------------------- Login Function -------------------
def login_user():
    username = email_entry.get()
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
            messagebox.showinfo("Success", f"Welcome {first_name} {last_name} ({role})!")
            root.destroy()  # Close the login window upon successful login
            # Here you can open another window or move to your main application
        else:
            messagebox.showerror("Error", "Invalid Username or Password")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# ------------------- Toggle Password Visibility -------------------
def toggle_password():
    if password_entry.cget("show") == "":
        password_entry.configure(show="*")
        toggle_btn.configure(text="🔒")
    else:
        password_entry.configure(show="")
        toggle_btn.configure(text="👁️")

# ---------------- Main Application Window ----------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("SuperMarket - Login")
root.geometry("800x500")  
root.resizable(False, False)

# ---------------- Main Frame ----------------
main_frame = ctk.CTkFrame(root, fg_color="white", corner_radius=10)
main_frame.place(relx=0.5, rely=0.5, anchor="center")

# ---------------- Left Side - Image ----------------
left_frame = ctk.CTkFrame(main_frame, fg_color="white", width=350, height=420, corner_radius=10)
left_frame.pack(side="left", fill="both", padx=10, pady=10)

# Load and display an image
image_path = "shopping.png"  # Replace with your image path
try:
    img = ctk.CTkImage(light_image=Image.open(image_path), size=(300, 300))
    image_label = ctk.CTkLabel(left_frame, image=img, text="")
    image_label.pack(pady=20)
except:
    ctk.CTkLabel(left_frame, text="🛒 SuperMarket", font=("Arial", 20, "bold"), text_color="#2563eb").pack(pady=80)

# ---------------- Right Side - Login Form ----------------
right_frame = ctk.CTkFrame(main_frame, fg_color="white", width=350, height=420, corner_radius=10)
right_frame.pack(side="right", fill="both", padx=10, pady=10)

ctk.CTkLabel(right_frame, text="Login to Your Account", font=("Arial", 18, "bold")).pack(pady=(20, 5))

# --- Username Entry --- 
ctk.CTkLabel(right_frame, text="Username", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
email_entry = ctk.CTkEntry(right_frame, font=("Arial", 12), height=35)
email_entry.pack(fill="x", pady=5)

# --- Password Entry with Toggle --- 
ctk.CTkLabel(right_frame, text="Password", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
password_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
password_frame.pack(fill="x", pady=5)

password_entry = ctk.CTkEntry(password_frame, font=("Arial", 12), height=35, show="*")
password_entry.pack(side="left", fill="x", expand=True)

toggle_btn = ctk.CTkButton(password_frame, text="🔒", width=30, height=30, fg_color="gray", command=toggle_password)
toggle_btn.pack(side="right", padx=5)

# --- Login Button --- 
login_btn = ctk.CTkButton(right_frame, text="Login", font=("Arial", 13, "bold"), fg_color="#2563eb",
                           height=40, corner_radius=5, command=login_user)
login_btn.pack(fill="x", pady=(15, 10))

# --- Signup Button --- 
signup_btn = ctk.CTkButton(right_frame, text="New User? Sign Up", font=("Arial", 12), fg_color="gray",
                            height=35, corner_radius=5)
signup_btn.pack(fill="x", pady=(5, 20))

# ---------------- Run Application ----------------
root.mainloop()
