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

# ------------------- Password Strength Check -------------------
def check_password_strength(password):
    # Initialize strength score
    score = 0
    
    # Check length
    if len(password) >= 8:
        score += 1
    
    # Check for uppercase letters
    if re.search(r'[A-Z]', password):
        score += 1
    
    # Check for lowercase letters
    if re.search(r'[a-z]', password):
        score += 1
    
    # Check for digits
    if re.search(r'\d', password):
        score += 1
    
    # Check for special characters
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    
    # Determine strength based on score
    if score <= 2:
        return "Weak", "#f87171"  # Red
    elif score <= 3:
        return "Moderate", "#fbbf24"  # Yellow
    elif score <= 4:
        return "Strong", "#34d399"  # Green
    else:
        return "Very Strong", "#2563eb"  # Blue

# ------------------- Password Change Callback -------------------
def on_password_change(*args):
    password = password_entry.get()
    if password:
        strength, color = check_password_strength(password)
        password_strength_label.configure(text=f"Password Strength: {strength}", text_color=color)
        password_strength_label.pack(anchor="w", pady=(5, 10))
    else:
        password_strength_label.pack_forget()

# ------------------- Toggle Password Visibility -------------------
def toggle_password_visibility():
    current_show_value = password_entry.cget("show")
    if current_show_value == "":  # Currently showing password
        password_entry.configure(show="*")
        password_toggle_btn.configure(text="👁️")  # Open eye when password is hidden
    else:  # Currently hiding password
        password_entry.configure(show="")
        password_toggle_btn.configure(text="👁️‍🗨️")  # Eye with speech bubble to indicate visible

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

# ------------------- Responsive Layout Functions -------------------
def adjust_layout(event=None):
    width = root.winfo_width()
    height = root.winfo_height()
    
    # Update main frame
    main_frame.place(relx=0.5, rely=0.5, anchor="center", 
                     relwidth=min(0.95, 1400/width) if width > 800 else 0.98, 
                     relheight=min(0.9, 900/height) if height > 600 else 0.98)
    
    # Adjust layout based on screen size
    if width < 1200:
        # Stack vertically on smaller screens
        left_frame.place(relx=0.5, rely=0, relwidth=1, relheight=0.5, anchor="n")
        right_frame.place(relx=0.5, rely=1, relwidth=1, relheight=0.5, anchor="s")
        
        # Adjust form container
        form_container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)
        
        # Adjust image size for vertical layout
        img.configure(size=(int(width*0.3), int(width*0.3)))
        
        # For very small screens, adjust font sizes and spacings
        if width < 900:
            title_label.configure(font=("Arial", 24, "bold"))
            subtitle_label.configure(font=("Arial", 12))
            login_header.configure(font=("Arial", 16, "bold"))
            login_instruction.configure(font=("Arial", 12))
            # Reduce vertical spacing
            title_label.pack(anchor="w", pady=(0, 3))
            subtitle_label.pack(anchor="w", pady=(0, 15))
            login_header.pack(anchor="w", pady=(0, 3))
            login_instruction.pack(anchor="w", pady=(0, 15))
        else:
            # Reset to original values for larger screens
            title_label.configure(font=("Arial", 28, "bold"))
            subtitle_label.configure(font=("Arial", 14))
            login_header.configure(font=("Arial", 18, "bold"))
            login_instruction.configure(font=("Arial", 14))
            # Reset spacing
            title_label.pack(anchor="w", pady=(0, 5))
            subtitle_label.pack(anchor="w", pady=(0, 30))
            login_header.pack(anchor="w", pady=(0, 5))
            login_instruction.pack(anchor="w", pady=(0, 30))
            
    else:
        # Side by side on larger screens
        left_frame.place(relx=0, rely=0, relwidth=0.5, relheight=1)
        right_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)
        
        # Adjust form container
        form_container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        # Adjust image size for horizontal layout
        img_size = min(int(width*0.2), 252)
        img.configure(size=(img_size, img_size))
        
    # Ensure that bottom elements (signup and forgot password) are visible
    # This needs to be done after the above layout adjustments
    
    # Get current form container dimensions
    form_width = form_container.winfo_width()
    form_height = form_container.winfo_height()
    
    # Calculate content height by summing up all widgets' heights and spacing
    # This is an approximation
    content_height = sum([w.winfo_reqheight() for w in form_container.winfo_children() if hasattr(w, 'winfo_reqheight')])
    
    # If content might overflow, adjust the layout to make it more compact
    if content_height > form_height * 0.9:  # If content takes more than 90% of available height
        # Make elements more compact
        login_btn.pack(fill="x", pady=(5, 10))  # Reduce padding around login button
        signup_frame.pack(fill="x", pady=(5, 0))  # Reduce padding above signup frame
        
        # Ensure forgot password is visible
        forgot_pwd_label.pack(anchor="w", pady=(3, 0))
    else:
        # Normal spacing
        login_btn.pack(fill="x", pady=(10, 20))
        signup_frame.pack(fill="x", pady=(10, 0))
        forgot_pwd_label.pack(anchor="w", pady=(5, 0))

# ---------------- Main Application Window ----------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("SuperMarket - Login")
root.geometry("1500x1000")  
# Allow window to be resizable
root.resizable(True, True)
root.minsize(800, 600)  # Set minimum window size

# ---------------- Main Frame ----------------
main_frame = ctk.CTkFrame(root, fg_color="white", corner_radius=10)
main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.9)

# ---------------- Left Side (Login Form) ----------------
left_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=0)
left_frame.place(relx=0, rely=0, relwidth=0.5, relheight=1)

# Create a form container for better alignment
form_container = ctk.CTkFrame(left_frame, fg_color="transparent")
form_container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)

# SuperMarket Title
title_label = ctk.CTkLabel(form_container, text="SuperMarket", 
                          font=("Arial", 28, "bold"), text_color="#2563eb")
title_label.pack(anchor="w", pady=(0, 5))

# Subtitle
subtitle_label = ctk.CTkLabel(form_container, text="Manage your shopping experience seamlessly.", 
                             font=("Arial", 14), text_color="gray")
subtitle_label.pack(anchor="w", pady=(0, 30))

# Login Details Header
login_header = ctk.CTkLabel(form_container, text="Enter your login details", 
                           font=("Arial", 18, "bold"), text_color="black")
login_header.pack(anchor="w", pady=(0, 5))

# Login Instruction
login_instruction = ctk.CTkLabel(form_container, text="Enter the registered credentials used while signing up", 
                               font=("Arial", 14), text_color="gray")
login_instruction.pack(anchor="w", pady=(0, 30))

# Username Label
username_label = ctk.CTkLabel(form_container, text="Username", font=("Arial", 14), text_color="gray")
username_label.pack(anchor="w", pady=(0, 5))

# Username Entry
username_entry = ctk.CTkEntry(form_container, font=("Arial", 14), height=40, 
                             border_color="#e5e7eb", border_width=1, corner_radius=5)
username_entry.pack(fill="x", pady=(0, 15))

# Password Label
password_label = ctk.CTkLabel(form_container, text="Password", font=("Arial", 14), text_color="gray")
password_label.pack(anchor="w", pady=(0, 5))

# Create a frame to hold password entry field and toggle button
password_frame = ctk.CTkFrame(form_container, fg_color="transparent")
password_frame.pack(fill="x", pady=(0, 5))

# Password Entry
password_entry = ctk.CTkEntry(password_frame, font=("Arial", 14), height=40, 
                             border_color="#e5e7eb", border_width=1, corner_radius=5, show="*")
password_entry.pack(side="left", fill="x", expand=True)

# Create password toggle button with eye emoji
password_toggle_btn = ctk.CTkButton(
    password_frame, 
    text="👁️",  # Open eye emoji (default state - password hidden)
    width=40,
    height=40,
    fg_color="transparent",
    hover_color="#e5e7eb",
    corner_radius=5,
    command=toggle_password_visibility
)
password_toggle_btn.pack(side="right", padx=(5, 0))

# Bind password entry to check strength on key release
password_entry.bind("<KeyRelease>", lambda e: on_password_change())

# Password Strength Label (hidden initially)
password_strength_label = ctk.CTkLabel(form_container, text="", font=("Arial", 12))
# This will be packed/unpacked dynamically based on password input

# Login Button
login_btn = ctk.CTkButton(form_container, text="Login", font=("Arial", 14, "bold"), 
                         fg_color="#2563eb", hover_color="#1d4ed8",
                         height=40, corner_radius=5, command=login_user)
login_btn.pack(fill="x", pady=(10, 20))

# Bottom options frame - contains both signup and forgot password
bottom_options_frame = ctk.CTkFrame(form_container, fg_color="transparent")
bottom_options_frame.pack(fill="x")

# Sign Up Text
signup_frame = ctk.CTkFrame(bottom_options_frame, fg_color="transparent")
signup_frame.pack(fill="x", pady=(5, 5))

signup_label = ctk.CTkLabel(signup_frame, text="Don't have an account?", 
                           font=("Arial", 14), text_color="gray")
signup_label.pack(side="left", padx=(0, 5))

signup_link = ctk.CTkLabel(signup_frame, text="Sign Up", 
                          font=("Arial", 14, "bold"), text_color="#2563eb", cursor="hand2")
signup_link.pack(side="left")
signup_link.bind("<Button-1>", lambda e: open_signup())

# Forgot Password
forgot_pwd_label = ctk.CTkLabel(bottom_options_frame, text="Forgot Password?", 
                             font=("Arial", 14), text_color="#2563eb", cursor="hand2")
forgot_pwd_label.pack(anchor="w", pady=(0, 5))
forgot_pwd_label.bind("<Button-1>", lambda e: open_forgot_password())

# ---------------- Right Side (Image) ----------------
right_frame = ctk.CTkFrame(main_frame, fg_color="#EBF3FF", corner_radius=0)
right_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)

# Create a centered frame for the image
image_container = ctk.CTkFrame(right_frame, fg_color="#EBF3FF", corner_radius=5)
image_container.place(relx=0.5, rely=0.5, anchor="center")

# Load and display the shopping cart image with transparency
image_path = "images/shopping.png"
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

# Add a scrollbar to the form container for very small screens
scrollable_frame = ctk.CTkScrollableFrame(left_frame, fg_color="transparent")
# This will only be used if the screen is too small for the content

# Bind configure event to adjust layout when window size changes
root.bind("<Configure>", adjust_layout)

# Initial layout adjustment
root.update_idletasks()
adjust_layout()

# ---------------- Run Application ----------------
root.mainloop()