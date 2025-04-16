import customtkinter as ctk
from tkinter import ttk, messagebox
import mysql.connector
import sys
import os
import re
import hashlib

# ------------------- Database Connection -------------------
def connect_db():
    return mysql.connector.connect(
        host="141.209.241.57",
        user="kshat1m",
        password="mypass",  # Your actual database password
        database="BIS698W1700_GRP2"
    )

# Global variable to store current user info
current_user = {
    "user_id": None,
    "username": None,
    "first_name": None,
    "last_name": None,
    "role": None
}

# ------------------- User Authentication Functions -------------------
def get_user_info(username):
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute(
            "SELECT user_id, username, first_name, last_name, role FROM Users WHERE username = %s",
            (username,)
        )
        
        user = cursor.fetchone()
        if user:
            current_user["user_id"] = user["user_id"]
            current_user["username"] = user["username"]
            current_user["first_name"] = user["first_name"]
            current_user["last_name"] = user["last_name"]
            current_user["role"] = user["role"]
            
            # Check if user is admin
            if user["role"] != "admin":
                messagebox.showerror("Access Denied", "You don't have admin privileges.")
                return False
            
            return True
        
        return False
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# ------------------- Inventory Functions -------------------
def fetch_inventory():
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT product_id, name, price, stock FROM Products ORDER BY name")
        
        products = cursor.fetchall()
        return products
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def add_product(name, price, stock):
    if not name or not price or not stock:
        messagebox.showwarning("Input Error", "Please fill out all fields.")
        return False
    
    try:
        # Validate price and stock are numeric
        try:
            price_val = float(price)
            stock_val = int(stock)
            
            if price_val <= 0:
                messagebox.showwarning("Input Error", "Price must be greater than zero.")
                return False
            
            if stock_val < 0:
                messagebox.showwarning("Input Error", "Stock cannot be negative.")
                return False
                
        except ValueError:
            messagebox.showwarning("Input Error", "Price and Stock must be numeric values.")
            return False
        
        connection = connect_db()
        cursor = connection.cursor()
        
        # Check if product with same name already exists
        cursor.execute("SELECT product_id FROM Products WHERE name = %s", (name,))
        if cursor.fetchone():
            messagebox.showwarning("Input Error", f"Product '{name}' already exists.")
            return False
        
        # Insert new product
        cursor.execute(
            "INSERT INTO Products (name, price, stock) VALUES (%s, %s, %s)",
            (name, price_val, stock_val)
        )
        
        connection.commit()
        return True
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_product(product_id, name, price, stock):
    if not name or not price or not stock:
        messagebox.showwarning("Input Error", "Please fill out all fields.")
        return False
    
    try:
        # Validate price and stock are numeric
        try:
            price_val = float(price)
            stock_val = int(stock)
            
            if price_val <= 0:
                messagebox.showwarning("Input Error", "Price must be greater than zero.")
                return False
            
            if stock_val < 0:
                messagebox.showwarning("Input Error", "Stock cannot be negative.")
                return False
                
        except ValueError:
            messagebox.showwarning("Input Error", "Price and Stock must be numeric values.")
            return False
        
        connection = connect_db()
        cursor = connection.cursor()
        
        # Check if another product with same name exists
        cursor.execute("SELECT product_id FROM Products WHERE name = %s AND product_id != %s", 
                     (name, product_id))
        if cursor.fetchone():
            messagebox.showwarning("Input Error", f"Another product with name '{name}' already exists.")
            return False
        
        # Update product
        cursor.execute(
            "UPDATE Products SET name = %s, price = %s, stock = %s WHERE product_id = %s",
            (name, price_val, stock_val, product_id)
        )
        
        connection.commit()
        return True
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def delete_product(product_id):
    try:
        connection = connect_db()
        cursor = connection.cursor()
        
        # First check if product is referenced in any cart
        cursor.execute(
            "SELECT COUNT(*) FROM CartItems WHERE product_id = %s",
            (product_id,)
        )
        
        count = cursor.fetchone()[0]
        if count > 0:
            messagebox.showwarning(
                "Cannot Delete", 
                "This product is in active carts or orders. Consider marking it as out of stock instead."
            )
            return False
        
        # Delete the product
        cursor.execute(
            "DELETE FROM Products WHERE product_id = %s",
            (product_id,)
        )
        
        connection.commit()
        return True
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# ------------------- User Management Functions -------------------
def fetch_users():
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute(
            """
            SELECT user_id, first_name, last_name, username, role 
            FROM Users 
            ORDER BY role, first_name, last_name
            """
        )
        
        users = cursor.fetchall()
        return users
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def add_user(first_name, last_name, email, role, password="password123"):
    if not first_name or not last_name or not email or not role:
        messagebox.showwarning("Input Error", "Please fill out all fields.")
        return False
    
    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        messagebox.showwarning("Input Error", "Please enter a valid email address.")
        return False
    
    # Create username from email (part before @)
    username = email.split('@')[0]
    
    # Hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
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
            return False
        
        # Insert new user
        cursor.execute(
            """
            INSERT INTO Users (first_name, last_name, username, email, password, role) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (first_name, last_name, username, email, hashed_password, role)
        )
        
        connection.commit()
        return True
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_user(user_id, first_name, last_name, email, role):
    if not first_name or not last_name or not email or not role:
        messagebox.showwarning("Input Error", "Please fill out all fields.")
        return False
    
    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        messagebox.showwarning("Input Error", "Please enter a valid email address.")
        return False
    
    # Create username from email (part before @)
    username = email.split('@')[0]
    
    try:
        connection = connect_db()
        cursor = connection.cursor()
        
        # Check if email already exists for another user
        cursor.execute(
            "SELECT user_id FROM Users WHERE email = %s AND user_id != %s",
            (email, user_id)
        )
        
        if cursor.fetchone():
            messagebox.showwarning("Input Error", "A user with this email already exists.")
            return False
        
        # Update user
        cursor.execute(
            """
            UPDATE Users 
            SET first_name = %s, last_name = %s, username = %s, email = %s, role = %s 
            WHERE user_id = %s
            """,
            (first_name, last_name, username, email, role, user_id)
        )
        
        connection.commit()
        return True
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def delete_user(user_id):
    try:
        connection = connect_db()
        cursor = connection.cursor()
        
        # Check if user has orders or carts
        cursor.execute(
            """
            SELECT COUNT(*) FROM Orders WHERE user_id = %s
            UNION ALL
            SELECT COUNT(*) FROM Carts WHERE user_id = %s
            """,
            (user_id, user_id)
        )
        
        counts = cursor.fetchall()
        if counts[0][0] > 0 or counts[1][0] > 0:
            messagebox.showwarning(
                "Cannot Delete", 
                "This user has orders or carts. Consider deactivating their account instead."
            )
            return False
        
        # Delete the user
        cursor.execute(
            "DELETE FROM Users WHERE user_id = %s",
            (user_id,)
        )
        
        connection.commit()
        return True
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def reset_password(user_id, default_password="password123"):
    try:
        connection = connect_db()
        cursor = connection.cursor()
        
        # Hash the default password
        hashed_password = hashlib.sha256(default_password.encode()).hexdigest()
        
        # Update user's password
        cursor.execute(
            "UPDATE Users SET password = %s WHERE user_id = %s",
            (hashed_password, user_id)
        )
        
        connection.commit()
        return True
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Main Application Class
class AdminApp:
    def __init__(self, root, username):
        self.root = root
        self.root.title("SuperMarket - Admin Panel")
        self.root.geometry("1200x700")
        self.root.resizable(False, False)
        
        # Set current user
        self.user_logged_in = get_user_info(username)
        if not self.user_logged_in:
            messagebox.showerror("Authentication Error", "You need admin privileges to access this page.")
            self.root.destroy()
            # In a complete application, you would redirect to login here
            return
        
        # Variables for editing items
        self.editing_product_id = None
        self.editing_user_id = None
        
        # Setup UI
        self.setup_main_ui()
        
        # Default to inventory management on startup
        self.show_inventory_management()
    
    def setup_main_ui(self):
        # Main frame
        self.main_frame = ctk.CTkFrame(self.root, fg_color="#f3f4f6", corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)
        
        # Sidebar (Navigation Menu)
        self.sidebar = ctk.CTkFrame(self.main_frame, width=250, height=700, corner_radius=0, fg_color="#2563eb")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)  # Prevent the frame from shrinking
        
        # Sidebar Title
        title_label = ctk.CTkLabel(self.sidebar, text="Admin Panel", font=("Arial", 24, "bold"), text_color="white")
        title_label.pack(pady=(40, 30))
        
        # Sidebar Buttons
        menu_items = ["Manage Inventory", "Manage Users", "Generate Report", "Logout"]
        
        for item in menu_items:
            btn = ctk.CTkButton(self.sidebar, text=item, fg_color="transparent", 
                               text_color="white", font=("Arial", 16),
                               anchor="w", height=40,
                               corner_radius=0, hover_color="#1d4ed8",
                               command=lambda i=item: self.navigate_to(i))
            btn.pack(fill="x", pady=5, padx=10)
        
        # Content frame - will hold different content based on navigation
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="white", corner_radius=15)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    def clear_content_frame(self):
        # Destroy all widgets in the content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def navigate_to(self, destination):
        if destination == "Manage Inventory":
            self.show_inventory_management()
        elif destination == "Manage Users":
            self.show_user_management()
        elif destination == "Generate Report":
            self.show_report_generation()
        elif destination == "Logout":
            self.root.destroy()
            # In a complete application, you would redirect to login here
    
    # ===== INVENTORY MANAGEMENT =====
    def show_inventory_management(self):
        self.clear_content_frame()
        
        # Header
        header_label = ctk.CTkLabel(self.content_frame, text="Inventory Management",
                                   font=("Arial", 24, "bold"), text_color="#2563eb")
        header_label.pack(anchor="w", padx=30, pady=(30, 20))
        
        # Add New Item Section
        add_item_section = ctk.CTkFrame(self.content_frame, fg_color="white", corner_radius=10,
                                      border_width=1, border_color="#e5e7eb")
        add_item_section.pack(fill="x", padx=30, pady=10)
        
        add_item_label = ctk.CTkLabel(add_item_section, text="Add New Item",
                                    font=("Arial", 18, "bold"), text_color="black")
        add_item_label.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Item Name Entry
        self.item_name_entry = ctk.CTkEntry(add_item_section, placeholder_text="Item Name",
                                     width=400, height=40, corner_radius=5)
        self.item_name_entry.pack(fill="x", padx=20, pady=10)
        
        # Price Entry
        self.price_entry = ctk.CTkEntry(add_item_section, placeholder_text="Price ($)",
                                 width=400, height=40, corner_radius=5)
        self.price_entry.pack(fill="x", padx=20, pady=10)
        
        # Stock Entry
        self.stock_entry = ctk.CTkEntry(add_item_section, placeholder_text="Stock Quantity",
                                 width=400, height=40, corner_radius=5)
        self.stock_entry.pack(fill="x", padx=20, pady=10)
        
        # Add Item Button
        self.add_item_btn = ctk.CTkButton(add_item_section, text="Add Item",
                                   fg_color="#10b981", hover_color="#059669",
                                   font=("Arial", 14), height=40, width=120,
                                   command=self.handle_add_update_product)
        self.add_item_btn.pack(anchor="w", padx=20, pady=(10, 20))
        
        # Existing Inventory Section
        inventory_section = ctk.CTkFrame(self.content_frame, fg_color="white")
        inventory_section.pack(fill="both", expand=True, padx=30, pady=10)
        
        inventory_label = ctk.CTkLabel(inventory_section, text="Existing Inventory",
                                     font=("Arial", 18, "bold"), text_color="black")
        inventory_label.pack(anchor="w", pady=(10, 15))
        
        # Create a custom style for the treeview
        style = ttk.Style()
        style.configure("Treeview", 
                        background="white",
                        fieldbackground="white", 
                        rowheight=40)
        style.configure("Treeview.Heading", 
                        font=('Arial', 12, 'bold'),
                        background="#f8fafc", 
                        foreground="black")
        style.map('Treeview', background=[('selected', '#e5e7eb')])
        
        # Create a frame for the table
        table_frame = ctk.CTkFrame(inventory_section, fg_color="#f8fafc", corner_radius=10)
        table_frame.pack(fill="both", expand=True, pady=5)
        
        # Create columns
        columns = ("name", "price", "stock", "actions")
        
        # Create treeview
        self.inventory_table = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Define headings
        self.inventory_table.heading("name", text="Item Name")
        self.inventory_table.heading("price", text="Price")
        self.inventory_table.heading("stock", text="Stock")
        self.inventory_table.heading("actions", text="Actions")
        
        # Define column widths and alignment
        self.inventory_table.column("name", width=300, anchor="w")
        self.inventory_table.column("price", width=100, anchor="center")
        self.inventory_table.column("stock", width=100, anchor="center")
        self.inventory_table.column("actions", width=200, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.inventory_table.yview)
        self.inventory_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.inventory_table.pack(fill="both", expand=True)
        
        # Bind double-click event for editing
        self.inventory_table.bind("<Double-1>", self.edit_product)
        
        # Create buttons frame
        buttons_frame = ctk.CTkFrame(inventory_section, fg_color="white")
        buttons_frame.pack(fill="x", pady=10)
        
        # Edit and Delete buttons
        edit_btn = ctk.CTkButton(buttons_frame, text="Edit Selected", 
                                fg_color="#eab308", hover_color="#ca8a04",
                                font=("Arial", 14), height=40, width=150,
                                command=lambda: self.edit_product(None))
        edit_btn.pack(side="left", padx=10)
        
        delete_btn = ctk.CTkButton(buttons_frame, text="Delete Selected", 
                                  fg_color="#ef4444", hover_color="#dc2626",
                                  font=("Arial", 14), height=40, width=150,
                                  command=self.delete_selected_product)
        delete_btn.pack(side="left", padx=10)
        
        # Populate inventory table
        self.refresh_inventory_table()

    def refresh_inventory_table(self):
        # Clear existing items
        for item in self.inventory_table.get_children():
            self.inventory_table.delete(item)
        
        # Fetch and display products
        products = fetch_inventory()
        
        for product in products:
            product_id = product["product_id"]
            name = product["name"]
            price = f"${float(product['price']):.2f}"
            stock = product["stock"]
            
            self.inventory_table.insert("", "end", values=(name, price, stock, ""), tags=(str(product_id),))

    def clear_product_fields(self):
        self.item_name_entry.delete(0, 'end')
        self.item_name_entry.insert(0, "")
        
        self.price_entry.delete(0, 'end')
        self.price_entry.insert(0, "")
        
        self.stock_entry.delete(0, 'end')
        self.stock_entry.insert(0, "")
        
        # Reset state
        self.add_item_btn.configure(text="Add Item")
        self.editing_product_id = None

    def handle_add_update_product(self):
        name = self.item_name_entry.get()
        price = self.price_entry.get()
        stock = self.stock_entry.get()
        
        if self.editing_product_id:
            # Update existing product
            if update_product(self.editing_product_id, name, price, stock):
                messagebox.showinfo("Success", f"Product '{name}' updated successfully!")
                self.refresh_inventory_table()
                self.clear_product_fields()
        else:
            # Add new product
            if add_product(name, price, stock):
                messagebox.showinfo("Success", f"Product '{name}' added successfully!")
                self.refresh_inventory_table()
                self.clear_product_fields()

    def edit_product(self, event):
        selected_items = self.inventory_table.selection()
        if not selected_items:
            return
        
        item = selected_items[0]
        values = self.inventory_table.item(item, 'values')
        
        if not values:
            return
        
        # Get product ID from tag
        product_id = int(self.inventory_table.item(item, 'tags')[0])
        
        # Fill entry fields with selected product details
        self.item_name_entry.delete(0, 'end')
        self.item_name_entry.insert(0, values[0])  # Name
        
        self.price_entry.delete(0, 'end')
        self.price_entry.insert(0, values[1].replace('$', ''))  # Price without $ sign
        
        self.stock_entry.delete(0, 'end')
        self.stock_entry.insert(0, values[2])  # Stock
        
        # Change button text and store product ID
        self.add_item_btn.configure(text="Update Item")
        self.editing_product_id = product_id

    def delete_selected_product(self):
        selected_items = self.inventory_table.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Please select a product to delete.")
            return
        
        item = selected_items[0]
        values = self.inventory_table.item(item, 'values')
        
        if not values:
            return
        
        # Get product ID from tag
        product_id = int(self.inventory_table.item(item, 'tags')[0])
        product_name = values[0]
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{product_name}'?")
        if not confirm:
            return
        
        # Delete the product
        if delete_product(product_id):
            messagebox.showinfo("Success", f"Product '{product_name}' deleted successfully!")
            self.refresh_inventory_table()
            self.clear_product_fields()
    
    # ===== USER MANAGEMENT =====
    def show_user_management(self):
        self.clear_content_frame()
        
        # Header
        header_label = ctk.CTkLabel(self.content_frame, text="User Management",
                                   font=("Arial", 24, "bold"), text_color="black")
        header_label.pack(anchor="w", padx=30, pady=(30, 20))
        
        # Add New User Section
        add_user_section = ctk.CTkFrame(self.content_frame, fg_color="white", corner_radius=10,
                                      border_width=1, border_color="#e5e7eb")
        add_user_section.pack(fill="x", padx=30, pady=10)
        
        add_user_label = ctk.CTkLabel(add_user_section, text="Add New User",
                                    font=("Arial", 18, "bold"), text_color="black")
        add_user_label.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Full Name Entry
        self.name_entry = ctk.CTkEntry(add_user_section, placeholder_text="Full Name",
                                 width=400, height=40, corner_radius=5)
        self.name_entry.pack(fill="x", padx=20, pady=10)
        
        # Email Entry
        self.email_entry = ctk.CTkEntry(add_user_section, placeholder_text="Email",
                                 width=400, height=40, corner_radius=5)
        self.email_entry.pack(fill="x", padx=20, pady=10)
        
        # Role Dropdown
        self.role_combobox = ctk.CTkComboBox(add_user_section, values=["admin", "user", "customer"],
                                      width=400, height=40, corner_radius=5)
        self.role_combobox.pack(fill="x", padx=20, pady=10)
        self.role_combobox.set("User Role")  # Default text
        
        # Add User Button
        self.add_user_btn = ctk.CTkButton(add_user_section, text="Add User",
                                   fg_color="#10b981", hover_color="#059669",
                                   font=("Arial", 14), height=40, width=120,
                                   command=self.handle_add_update_user)
        self.add_user_btn.pack(anchor="w", padx=20, pady=(10, 20))
        
        # Existing Users Section
        users_section = ctk.CTkFrame(self.content_frame, fg_color="white")
        users_section.pack(fill="both", expand=True, padx=30, pady=10)
        
        users_label = ctk.CTkLabel(users_section, text="Existing Users",
                                 font=("Arial", 18, "bold"), text_color="black")
        users_label.pack(anchor="w", pady=(10, 15))
        
        # Create a custom style for the treeview
        style = ttk.Style()
        style.configure("Treeview", 
                        background="white",
                        fieldbackground="white", 
                        rowheight=40)
        style.configure("Treeview.Heading", 
                        font=('Arial', 12, 'bold'),
                        background="#f8fafc", 
                        foreground="black")
        style.map('Treeview', background=[('selected', '#e5e7eb')])
        
        # Create a frame for the table
        table_frame = ctk.CTkFrame(users_section, fg_color="#f8fafc", corner_radius=10)
        table_frame.pack(fill="both", expand=True, pady=5)
        
        # Create columns
        columns = ("name", "email", "role", "actions")
        
        # Create treeview
        self.users_table = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Define headings
        self.users_table.heading("name", text="Name")
        self.users_table.heading("email", text="Email")
        self.users_table.heading("role", text="Role")
        self.users_table.heading("actions", text="Actions")
        
        # Define column widths and alignment
        self.users_table.column("name", width=200, anchor="w")
        self.users_table.column("email", width=250, anchor="w")
        self.users_table.column("role", width=100, anchor="center")
        self.users_table.column("actions", width=200, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.users_table.yview)
        self.users_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.users_table.pack(fill="both", expand=True)
        
        # Bind double-click event for editing
        self.users_table.bind("<Double-1>", self.edit_user)
        
        # Create buttons frame
        buttons_frame = ctk.CTkFrame(users_section, fg_color="white")
        buttons_frame.pack(fill="x", pady=10)
        
        # Edit and Delete buttons
        edit_btn = ctk.CTkButton(buttons_frame, text="Edit Selected", 
                                fg_color="#eab308", hover_color="#ca8a04",
                                font=("Arial", 14), height=40, width=150,
                                command=lambda: self.edit_user(None))
        edit_btn.pack(side="left", padx=10)
        
        delete_btn = ctk.CTkButton(buttons_frame, text="Delete Selected", 
                                  fg_color="#ef4444", hover_color="#dc2626",
                                  font=("Arial", 14), height=40, width=150,
                                  command=self.delete_selected_user)
        delete_btn.pack(side="left", padx=10)
        
        # Reset Password button
        reset_pwd_btn = ctk.CTkButton(buttons_frame, text="Reset Password", 
                                    fg_color="#3b82f6", hover_color="#2563eb",
                                    font=("Arial", 14), height=40, width=150,
                                    command=self.reset_selected_password)
        reset_pwd_btn.pack(side="left", padx=10)
        
        # Populate users table
        self.refresh_users_table()
        
    def refresh_users_table(self):
        # Clear existing items
        for item in self.users_table.get_children():
            self.users_table.delete(item)
        
        # Fetch and display users
        users = fetch_users()
        
        for user in users:
            user_id = user["user_id"]
            full_name = f"{user['first_name']} {user['last_name']}"
            email = f"{user['username']}@example.com"  # Replace with actual email field if available
            role = user["role"]
            
            self.users_table.insert("", "end", values=(full_name, email, role, ""), tags=(str(user_id),))
    
    def clear_user_fields(self):
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, "")
        
        self.email_entry.delete(0, 'end')
        self.email_entry.insert(0, "")
        
        self.role_combobox.set("User Role")  # Clear combobox selection
        
        # Reset state
        self.add_user_btn.configure(text="Add User")
        self.editing_user_id = None
    
    def handle_add_update_user(self):
        # Get first name and last name from the full name
        full_name = self.name_entry.get().strip()
        if " " in full_name:
            first_name, last_name = full_name.split(" ", 1)
        else:
            first_name = full_name
            last_name = ""
        
        email = self.email_entry.get().strip()
        role = self.role_combobox.get()
        
        if self.editing_user_id:
            # Update existing user
            if update_user(self.editing_user_id, first_name, last_name, email, role):
                messagebox.showinfo("Success", f"User '{full_name}' updated successfully!")
                self.refresh_users_table()
                self.clear_user_fields()
        else:
            # Add new user
            if add_user(first_name, last_name, email, role):
                messagebox.showinfo("Success", f"User '{full_name}' added successfully!")
                self.refresh_users_table()
                self.clear_user_fields()
    
    def edit_user(self, event):
        selected_items = self.users_table.selection()
        if not selected_items:
            return
        
        item = selected_items[0]
        values = self.users_table.item(item, 'values')
        
        if not values:
            return
        
        # Get user ID from tag
        user_id = int(self.users_table.item(item, 'tags')[0])
        
        # Fill entry fields with selected user details
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, values[0])  # Full name
        
        self.email_entry.delete(0, 'end')
        self.email_entry.insert(0, values[1])  # Email
        
        self.role_combobox.set(values[2])  # Role
        
        # Change button text and store user ID
        self.add_user_btn.configure(text="Update User")
        self.editing_user_id = user_id
    
    def delete_selected_user(self):
        selected_items = self.users_table.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Please select a user to delete.")
            return
        
        item = selected_items[0]
        values = self.users_table.item(item, 'values')
        
        if not values:
            return
        
        # Get user ID from tag
        user_id = int(self.users_table.item(item, 'tags')[0])
        user_name = values[0]
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{user_name}'?")
        if not confirm:
            return
        
        # Delete the user
        if delete_user(user_id):
            messagebox.showinfo("Success", f"User '{user_name}' deleted successfully!")
            self.refresh_users_table()
            self.clear_user_fields()
    
    def reset_selected_password(self):
        selected_items = self.users_table.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Please select a user to reset their password.")
            return
        
        item = selected_items[0]
        values = self.users_table.item(item, 'values')
        
        if not values:
            return
        
        # Get user ID from tag
        user_id = int(self.users_table.item(item, 'tags')[0])
        user_name = values[0]
        
        # Confirm reset
        confirm = messagebox.askyesno("Confirm Reset", f"Are you sure you want to reset the password for '{user_name}'?")
        if not confirm:
            return
        
        # Reset the password
        if reset_password(user_id):
            messagebox.showinfo("Success", f"Password for '{user_name}' has been reset to the default!")
    
    # ===== REPORT GENERATION =====
    def show_report_generation(self):
        self.clear_content_frame()
        
        # Header
        header_label = ctk.CTkLabel(self.content_frame, text="Report Generation",
                                   font=("Arial", 24, "bold"), text_color="black")
        header_label.pack(anchor="w", padx=30, pady=(30, 20))
        
        # Report options frame
        report_frame = ctk.CTkFrame(self.content_frame, fg_color="white", corner_radius=10,
                                   border_width=1, border_color="#e5e7eb")
        report_frame.pack(fill="x", padx=30, pady=10)
        
        options_label = ctk.CTkLabel(report_frame, text="Report Options",
                                    font=("Arial", 18, "bold"), text_color="black")
        options_label.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Report type selector
        report_type_frame = ctk.CTkFrame(report_frame, fg_color="transparent")
        report_type_frame.pack(fill="x", padx=20, pady=10)
        
        report_type_label = ctk.CTkLabel(report_type_frame, text="Report Type:",
                                        font=("Arial", 14), text_color="black")
        report_type_label.pack(side="left", padx=(0, 10))
        
        self.report_type = ctk.CTkComboBox(report_type_frame, values=["Sales Report", "Inventory Report", "User Activity"],
                                     width=300, height=40, corner_radius=5)
        self.report_type.pack(side="left")
        self.report_type.set("Sales Report")
        
        # Date range
        date_frame = ctk.CTkFrame(report_frame, fg_color="transparent")
        date_frame.pack(fill="x", padx=20, pady=10)
        
        from_label = ctk.CTkLabel(date_frame, text="From:",
                                 font=("Arial", 14), text_color="black")
        from_label.pack(side="left", padx=(0, 10))
        
        self.from_date = ctk.CTkEntry(date_frame, placeholder_text="YYYY-MM-DD",
                                width=150, height=40, corner_radius=5)
        self.from_date.pack(side="left", padx=(0, 20))
        
        to_label = ctk.CTkLabel(date_frame, text="To:",
                               font=("Arial", 14), text_color="black")
        to_label.pack(side="left", padx=(0, 10))
        
        self.to_date = ctk.CTkEntry(date_frame, placeholder_text="YYYY-MM-DD",
                              width=150, height=40, corner_radius=5)
        self.to_date.pack(side="left")
        
        # Generate button
        generate_btn = ctk.CTkButton(report_frame, text="Generate Report",
                                    fg_color="#10b981", hover_color="#059669",
                                    font=("Arial", 14), height=40, width=150,
                                    command=self.generate_report)
        generate_btn.pack(anchor="w", padx=20, pady=(10, 20))
        
        # Preview area
        preview_frame = ctk.CTkFrame(self.content_frame, fg_color="white")
        preview_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        preview_label = ctk.CTkLabel(preview_frame, text="Report Preview",
                                    font=("Arial", 18, "bold"), text_color="black")
        preview_label.pack(anchor="w", pady=(10, 15))
        
        self.preview_text = ctk.CTkTextbox(preview_frame, fg_color="#f8fafc", corner_radius=5,
                                     width=800, height=300)
        self.preview_text.pack(fill="both", expand=True, pady=5)
        self.preview_text.insert("1.0", "Report preview will appear here...")
        
    def generate_report(self):
        report_type = self.report_type.get()
        from_date = self.from_date.get()
        to_date = self.to_date.get()
        
        # In a real application, you would generate an actual report
        # For demonstration purposes, we'll just show a sample report
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", f"Sample {report_type}\n")
        self.preview_text.insert("end", f"Period: {from_date} to {to_date}\n\n")
        self.preview_text.insert("end", "This is where the actual report data would appear.\n")
        self.preview_text.insert("end", "In a real application, you would query the database\n")
        self.preview_text.insert("end", "and generate a detailed report based on the selected parameters.\n\n")
        self.preview_text.insert("end", "You could also add options to export as PDF, CSV, etc.")
        
        messagebox.showinfo("Report Generated", f"{report_type} has been generated for preview.")


# ------------------- Main Entry Point -------------------
def main():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    
    # Check if username was provided from login
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        # For testing purposes - remove in production
        username = "admin123"  # Replace with an admin username in your database
    
    app = AdminApp(root, username)
    root.mainloop()

if __name__ == "__main__":
    main()