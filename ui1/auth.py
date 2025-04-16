"""
Authentication module for the Supermarket Management System
Handles login, signup, and admin access controls
"""

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import mysql.connector
import hashlib
import os
import subprocess
import sys

# Import from parent directory
sys.path.append('..')
from config import DB_CONFIG, UI_THEME, UI_COLOR_THEME
from utils import connect_db, hash_password, write_login_file

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperMarket - Login")
        self.root.geometry("1000x600")
        self.root.resizable(False, False)
        
        # Configure appearance
        ctk.set_appearance_mode(UI_THEME)
        ctk.set_default_color_theme(UI_COLOR_THEME)
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main Frame
        main_frame = ctk.CTkFrame(self.root, fg_color="white", corner_radius=10)
        main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.9)
        
        # Left Side (Login Form)
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
        self.username_entry = ctk.CTkEntry(form_container, font=("Arial", 14), height=40, 
                                     border_color="#e5e7eb", border_width=1, corner_radius=5)
        self.username_entry.pack(fill="x", pady=(0, 15))
        
        # Password Label
        password_label = ctk.CTkLabel(form_container, text="Password", font=("Arial", 14), text_color="gray")
        password_label.pack(anchor="w", pady=(0, 5))
        
        # Password Entry
        self.password_entry = ctk.CTkEntry(form_container, font=("Arial", 14), height=40, 
                                     border_color="#e5e7eb", border_width=1, corner_radius=5, show="*")
        self.password_entry.pack(fill="x", pady=(0, 20))
        
        # Login Button
        login_btn = ctk.CTkButton(form_container, text="Login", font=("Arial", 14, "bold"), 
                                 fg_color="#2563eb", hover_color="#1d4ed8",
                                 height=40, corner_radius=5, command=self.login_user)
        login_btn.pack(fill="x", pady=(10, 20))
        
        # Sign Up Text
        signup_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        signup_frame.pack(fill="x", pady=(10, 0))
        
        signup_label = ctk.CTkLabel(signup_frame, text="Don't have an account?", 
                                   font=("Arial", 14), text_color="gray")
        signup_label.pack(side="left", padx=(0, 5))
        
        signup_link = ctk.CTkLabel(signup_frame, text="Sign Up", 
                                  font=("Arial", 14, "bold"), text_color="#2563eb", cursor="hand2")
        signup_link.pack(side="left")
        signup_link.bind("<Button-1>", lambda e: self.open_signup())
        
        # Right Side (Image)
        right_frame = ctk.CTkFrame(main_frame, fg_color="#EBF3FF", corner_radius=0)
        right_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)
        
        # Create a centered frame for the image
        image_container = ctk.CTkFrame(right_frame, fg_color="#EBF3FF", corner_radius=5, width=252, height=252)
        image_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Load and display the shopping cart image with transparency
        image_path = "../static/images/shopping.png"
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
    
    def login_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Input Error", "All fields are required.")
            return
        
        hashed_password = hash_password(password)
        
        try:
            connection = connect_db()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT first_name, last_name, role FROM Users WHERE username = %s AND password = %s",
                (username, hashed_password)
            )
            user = cursor.fetchone()
            
            if user:
                first_name, last_name, role = user["first_name"], user["last_name"], user["role"]
                
                if role.lower() != "user" and not self.admin_allowed:
                    messagebox.showerror("Access Denied", "Only users can log in. Admin access is restricted.")
                    return
                
                messagebox.showinfo("Success", f"Welcome {first_name} {last_name} ({role})!")
                
                # Save user info for session
                write_login_file(username, role)
                
                # Close login window
                self.root.destroy()
                
                # Launch appropriate dashboard based on role
                if role == "admin" and self.admin_allowed:
                    subprocess.Popen(["python", "custom/admin_dashboard.py", username])
                else:
                    subprocess.Popen(["python", "custom/user_dashboard.py", username])
            else:
                messagebox.showerror("Error", "Invalid Username or Password")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    def open_signup(self):
        self.root.destroy()
        subprocess.run(["python", "custom/auth.py", "signup"])


class SignupWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperMarket - Sign Up")
        self.root.geometry("1000x600")
        self.root.resizable(False, False)
        
        # Configure appearance
        ctk.set_appearance_mode(UI_THEME)
        ctk.set_default_color_theme(UI_COLOR_THEME)
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main Frame
        main_frame = ctk.CTkFrame(self.root, fg_color="white", corner_radius=10)
        main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.9)
        
        # Left Side (Signup Form)
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
        first_name_label.place(relx=0.1, rely=0.44)
        
        # First Name Entry
        self.first_name_entry = ctk.CTkEntry(left_frame, font=("Arial", 14), height=40, width=300, 
                                      border_color="#e5e7eb", border_width=1, corner_radius=5)
        self.first_name_entry.place(relx=0.1, rely=0.48)
        
        # Last Name Label
        last_name_label = ctk.CTkLabel(left_frame, text="Last Name", font=("Arial", 14), text_color="gray")
        last_name_label.place(relx=0.1, rely=0.54)
        
        # Last Name Entry
        self.last_name_entry = ctk.CTkEntry(left_frame, font=("Arial", 14), height=40, width=300, 
                                     border_color="#e5e7eb", border_width=1, corner_radius=5)
        self.last_name_entry.place(relx=0.1, rely=0.58)
        
        # Email Label
        email_label = ctk.CTkLabel(left_frame, text="Email", font=("Arial", 14), text_color="gray")
        email_label.place(relx=0.1, rely=0.64)
        
        # Email Entry
        self.email_entry = ctk.CTkEntry(left_frame, font=("Arial", 14), height=40, width=300, 
                                  border_color="#e5e7eb", border_width=1, corner_radius=5)
        self.email_entry.place(relx=0.1, rely=0.68)
        
        # Password Label
        password_label = ctk.CTkLabel(left_frame, text="Password", font=("Arial", 14), text_color="gray")
        password_label.place(relx=0.1, rely=0.74)
        
        # Password Entry
        self.password_entry = ctk.CTkEntry(left_frame, font=("Arial", 14), height=40, width=300, 
                                     border_color="#e5e7eb", border_width=1, corner_radius=5, show="*")
        self.password_entry.place(relx=0.1, rely=0.78)
        
        # Sign Up Button
        signup_btn = ctk.CTkButton(left_frame, text="Sign Up", font=("Arial", 14, "bold"), 
                                  fg_color="#2563eb", hover_color="#1d4ed8",
                                  height=40, width=300, corner_radius=5, command=self.register_user)
        signup_btn.place(relx=0.1, rely=0.86)
        
        # Already have an account text
        login_label = ctk.CTkLabel(left_frame, text="Already have an account? Login", 
                                  font=("Arial", 14), text_color="#2563eb", cursor="hand2")
        login_label.place(relx=0.1, rely=0.92)
        login_label.bind("<Button-1>", lambda e: self.open_login())
        
        # Right Side (Image)
        right_frame = ctk.CTkFrame(main_frame, fg_color="#EBF3FF", corner_radius=0)
        right_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)
        
        # Create a centered frame for the image
        image_container = ctk.CTkFrame(right_frame, fg_color="#EBF3FF", corner_radius=5, width=252, height=252)
        image_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Load and display the shopping cart image with transparency
        image_path = "../static/images/shopping.png"
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
    
    def register_user(self):
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if not first_name or not last_name or not email or not password:
            messagebox.showwarning("Input Error", "All fields are required.")
            return
        
        # Create username from email (part before @)
        username = email.split('@')[0] if '@' in email else email
        
        hashed_password = hash_password(password)
        
        try:
            connection = connect_db()
            cursor = connection.cursor()
            
            # Check if username or email already exists
            cursor.execute(
                "SELECT user_id FROM Users WHERE username = %s OR email = %s",
                (username, email)
            )
            
            if cursor.fetchone():
                messagebox.showwarning("Input Error", "A user with this username or email already exists.")
                return
            
            # Insert new user
            cursor.execute(
                """
                INSERT INTO Users (first_name, last_name, username, email, password, role) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (first_name, last_name, username, email, hashed_password, "user")
            )
            
            connection.commit()
            messagebox.showinfo("Success", "User registered successfully!")
            
            # Clear the input fields
            self.first_name_entry.delete(0, ctk.END)
            self.last_name_entry.delete(0, ctk.END)
            self.email_entry.delete(0, ctk.END)
            self.password_entry.delete(0, ctk.END)
            
            # Return to login screen
            self.open_login()
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    def open_login(self):
        self.root.destroy()
        subprocess.run(["python", "custom/auth.py", "login"])


class AdminLoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperMarket - Admin Login")
        self.root.geometry("600x600")
        self.root.resizable(False, False)
        
        # Configure appearance
        ctk.set_appearance_mode(UI_THEME)
        ctk.set_default_color_theme(UI_COLOR_THEME)
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main Frame
        main_frame = ctk.CTkFrame(self.root, fg_color="white", corner_radius=10)
        main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)
        
        # Create form container for better alignment
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=50, pady=(20, 20))
        
        # Title
        title_label = ctk.CTkLabel(form_frame, text="Admin Login", 
                                  font=("Arial", 24, "bold"), 
                                  text_color="#2563eb")
        title_label.pack(pady=(10, 5))
        
        # Instructions
        instructions_label = ctk.CTkLabel(form_frame, 
                                        text="Please enter your admin credentials", 
                                        font=("Arial", 14), 
                                        text_color="gray")
        instructions_label.pack(pady=(0, 20))
        
        # Username Entry
        username_label = ctk.CTkLabel(form_frame, text="Username", 
                                     font=("Arial", 14), 
                                     text_color="black")
        username_label.pack(anchor="w")
        
        self.username_entry = ctk.CTkEntry(form_frame, width=400, height=40, corner_radius=5)
        self.username_entry.pack(fill="x", pady=(5, 15))
        
        # Password Entry
        password_label = ctk.CTkLabel(form_frame, text="Password", 
                                     font=("Arial", 14), 
                                     text_color="black")
        password_label.pack(anchor="w")
        
        self.password_entry = ctk.CTkEntry(form_frame, width=400, height=40, 
                                     corner_radius=5, show="*")
        self.password_entry.pack(fill="x", pady=(5, 20))
        
        # Login Button
        login_btn = ctk.CTkButton(form_frame, text="Login", 
                                 width=400, height=40, 
                                 fg_color="#2563eb", hover_color="#1d4ed8",
                                 font=("Arial", 16, "bold"), 
                                 command=self.login_admin)
        login_btn.pack(fill="x", pady=(5, 10))
        
        # Return to Main Button
        return_btn = ctk.CTkButton(form_frame, text="Return to Main Menu", 
                                  width=400, height=30, 
                                  fg_color="#64748b", hover_color="#475569",
                                  font=("Arial", 14), 
                                  command=self.return_to_main)
        return_btn.pack(fill="x", pady=(5, 10))
    
    def login_admin(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Input Error", "All fields are required.")
            return
        
        hashed_password = hash_password(password)
        
        try:
            connection = connect_db()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT user_id, first_name, last_name, role FROM Users WHERE username = %s AND password = %s",
                (username, hashed_password)
            )
            user = cursor.fetchone()
            
            if user:
                # Check if user has admin role
                if user["role"] != "admin":
                    messagebox.showerror("Access Denied", "You don't have admin privileges.")
                    return
                    
                # Admin login successful
                messagebox.showinfo("Success", f"Welcome Admin {user['first_name']} {user['last_name']}!")
                
                # Save login info for session
                write_login_file(username, "admin")
                
                # Close admin login window
                self.root.destroy()
                
                # Launch admin dashboard
                subprocess.run(["python", "custom/admin_dashboard.py", username])
            else:
                messagebox.showerror("Error", "Invalid Username or Password")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    def return_to_main(self):
        self.root.destroy()
        subprocess.run(["python", "../main.py"])


# Main function to run different auth windows based on arguments
def main():
    if len(sys.argv) < 2:
        print("Please specify an action: login, signup, or admin_login")
        return
    
    action = sys.argv[1]
    root = ctk.CTk()
    
    if action == "login":
        LoginWindow(root)
        # Pass whether admin login is allowed or not
        root.admin_allowed = False
    elif action == "signup":
        SignupWindow(root)
    elif action == "admin_login":
        AdminLoginWindow(root)
    else:
        print(f"Unknown action: {action}")
        root.destroy()
        return
    
    root.mainloop()

if __name__ == "__main__":
    main()