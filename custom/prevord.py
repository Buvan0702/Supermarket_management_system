import customtkinter as ctk
from tkinter import messagebox
import mysql.connector
import subprocess
import os
import sys

# Set environment variables for Tkinter
os.environ['TCL_LIBRARY'] = r"C:\Users\buvan\AppData\Local\Programs\Python\Python39\tcl\tcl8.6"
os.environ['TK_LIBRARY'] = r"C:\Users\buvan\AppData\Local\Programs\Python\Python39\tcl\tk8.6"

# Global variable to store current user info
current_user = {
    "user_id": None,
    "username": None,
    "first_name": None,
    "last_name": None,
    "role": None
}

# ------------------- Database Connection -------------------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="new_password",  # Update with your MySQL password
        database="supermarket_management"
    )

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
            return True
        
        return False
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# ------------------- Order Functions -------------------
def fetch_user_orders():
    if not current_user["user_id"]:
        return []
    
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        
        # Get all orders for the current user with a simplified query
        cursor.execute("""
            SELECT order_id, order_date, total_amount, status 
            FROM Orders 
            WHERE user_id = %s 
            ORDER BY order_date DESC
        """, (current_user["user_id"],))
        
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error fetching orders: {err}")
        messagebox.showerror("Database Error", str(err))
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def fetch_order_details(order_id):
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        
        # First, get basic order information
        cursor.execute("""
            SELECT o.order_id, o.order_date, o.total_amount, o.status, c.cart_id
            FROM Orders o
            JOIN Carts c ON o.cart_id = c.cart_id
            WHERE o.order_id = %s
        """, (order_id,))
        
        order = cursor.fetchone()
        
        if not order:
            print(f"No order found with ID {order_id}")
            return None, []
        
        cart_id = order["cart_id"]
        print(f"Found order {order_id} with cart ID {cart_id}")
        
        # Now, get the items in this cart
        # Use a direct and simple query to avoid complex joins that might fail
        cursor.execute("""
            SELECT ci.quantity, p.name, p.price
            FROM CartItems ci
            JOIN Products p ON ci.product_id = p.product_id
            WHERE ci.cart_id = %s
        """, (cart_id,))
        
        items = cursor.fetchall()
        print(f"Found {len(items)} items in order {order_id}")
        
        return order, items
    except mysql.connector.Error as err:
        print(f"Error fetching order details: {err}")
        messagebox.showerror("Database Error", str(err))
        return None, []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# ------------------- Navigation Functions -------------------
def return_to_home():
    app.destroy()
    subprocess.run(["python", "home.py", current_user["username"]])

# ------------------- UI Functions -------------------
def display_order_details(order_id):
    # Clear existing content
    for widget in details_container.winfo_children():
        widget.destroy()
    
    # Fetch order details
    order, items = fetch_order_details(order_id)
    
    if not order:
        no_order_label = ctk.CTkLabel(details_container, text="Order not found or no items in this order",
                                    font=("Arial", 16), text_color="gray")
        no_order_label.pack(pady=20)
        return
    
    # Order header
    order_header = ctk.CTkFrame(details_container, fg_color="white", corner_radius=10)
    order_header.pack(fill="x", padx=20, pady=10)
    
    # Format the date
    order_date = order["order_date"].strftime("%Y-%m-%d %H:%M")
    
    # Order title
    order_title = ctk.CTkLabel(order_header, text=f"Order #{order['order_id']}",
                              font=("Arial", 18, "bold"), text_color="black")
    order_title.pack(anchor="w", padx=20, pady=(10, 5))
    
    # Order date
    date_label = ctk.CTkLabel(order_header, text=f"Date: {order_date}",
                            font=("Arial", 14), text_color="gray")
    date_label.pack(anchor="w", padx=20, pady=(0, 5))
    
    # Order status
    status_label = ctk.CTkLabel(order_header, text=f"Status: {order['status'].capitalize()}",
                              font=("Arial", 14), text_color="gray")
    status_label.pack(anchor="w", padx=20, pady=(0, 10))
    
    # Items container
    if not items:
        no_items_label = ctk.CTkLabel(details_container, text="No items found in this order",
                                    font=("Arial", 16), text_color="gray")
        no_items_label.pack(pady=20)
        return
    
    items_frame = ctk.CTkFrame(details_container, fg_color="white", corner_radius=10)
    items_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    # Items header
    items_header = ctk.CTkLabel(items_frame, text="Order Items",
                              font=("Arial", 16, "bold"), text_color="black")
    items_header.pack(anchor="w", padx=20, pady=(10, 5))
    
    # Table header
    header_frame = ctk.CTkFrame(items_frame, fg_color="#f3f4f6")
    header_frame.pack(fill="x", padx=20, pady=(5, 0))
    
    # Header columns
    ctk.CTkLabel(header_frame, text="Item", font=("Arial", 14, "bold"), text_color="black").pack(side="left", padx=20, pady=5)
    ctk.CTkLabel(header_frame, text="Price", font=("Arial", 14, "bold"), text_color="black").pack(side="left", expand=True, pady=5)
    ctk.CTkLabel(header_frame, text="Quantity", font=("Arial", 14, "bold"), text_color="black").pack(side="left", padx=20, pady=5)
    ctk.CTkLabel(header_frame, text="Subtotal", font=("Arial", 14, "bold"), text_color="black").pack(side="right", padx=20, pady=5)
    
    # Divider
    divider = ctk.CTkFrame(items_frame, height=1, fg_color="gray")
    divider.pack(fill="x", padx=20, pady=(0, 5))
    
    # Item rows
    for item in items:
        item_row = ctk.CTkFrame(items_frame, fg_color="white")
        item_row.pack(fill="x", padx=20, pady=2)
        
        price = float(item["price"])
        quantity = item["quantity"]
        subtotal = price * quantity
        
        ctk.CTkLabel(item_row, text=item["name"], font=("Arial", 14), text_color="black").pack(side="left", padx=20, pady=5)
        ctk.CTkLabel(item_row, text=f"${price:.2f}", font=("Arial", 14), text_color="black").pack(side="left", expand=True, pady=5)
        ctk.CTkLabel(item_row, text=str(quantity), font=("Arial", 14), text_color="black").pack(side="left", padx=20, pady=5)
        ctk.CTkLabel(item_row, text=f"${subtotal:.2f}", font=("Arial", 14), text_color="black").pack(side="right", padx=20, pady=5)
    
    # Bottom divider
    divider2 = ctk.CTkFrame(items_frame, height=1, fg_color="gray")
    divider2.pack(fill="x", padx=20, pady=(5, 5))
    
    # Total row
    total_row = ctk.CTkFrame(items_frame, fg_color="white")
    total_row.pack(fill="x", padx=20, pady=(5, 10))
    
    ctk.CTkLabel(total_row, text="Total:", font=("Arial", 16, "bold"), text_color="black").pack(side="left", padx=20)
    ctk.CTkLabel(total_row, text=f"${float(order['total_amount']):.2f}", font=("Arial", 16, "bold"), text_color="black").pack(side="right", padx=20)

def populate_orders_list():
    # Clear existing items
    for widget in orders_list.winfo_children():
        widget.destroy()
    
    # Fetch orders
    orders = fetch_user_orders()
    
    if not orders:
        no_orders_label = ctk.CTkLabel(orders_list, text="No orders found",
                                     font=("Arial", 14), text_color="gray")
        no_orders_label.pack(pady=20)
        return
    
    # Add each order to the list
    for order in orders:
        order_btn = ctk.CTkButton(
            orders_list,
            text=f"Order #{order['order_id']} - {order['order_date'].strftime('%Y-%m-%d')} - ${float(order['total_amount']):.2f}",
            fg_color="#f3f4f6" if order["status"] != "completed" else "#dcfce7",
            text_color="black",
            hover_color="#e5e7eb",
            height=40,
            anchor="w",
            command=lambda id=order['order_id']: display_order_details(id)
        )
        order_btn.pack(fill="x", padx=10, pady=5)
    
    # If order_id was passed as command-line argument, display it
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        display_order_details(int(sys.argv[1]))
    elif orders:
        # Display the first order by default
        display_order_details(orders[0]["order_id"])

# ------------------- Initialize Application ----------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("SuperMarket - Previous Orders")
app.geometry("1200x700")
app.resizable(False, False)

# Set current user from command-line args or file
if len(sys.argv) > 2:
    username_from_args = sys.argv[2]
    user_logged_in = get_user_info(username_from_args)
else:
    # Try to read from file
    if os.path.exists("current_user.txt"):
        with open("current_user.txt", "r") as f:
            lines = f.readlines()
            if len(lines) >= 1:
                username_from_file = lines[0].strip()
                user_logged_in = get_user_info(username_from_file)
            else:
                user_logged_in = False
    else:
        user_logged_in = False

if not user_logged_in:
    messagebox.showerror("Authentication Error", "User not found. Please login again.")
    app.destroy()
    subprocess.run(["python", "login.py"])
    exit()

# ---------------- Main Content ----------------
main_frame = ctk.CTkFrame(app, fg_color="#f3f4f6", corner_radius=0)
main_frame.pack(fill="both", expand=True)

# ---------------- Sidebar (Navigation Menu) ----------------
sidebar = ctk.CTkFrame(app, width=200, height=700, corner_radius=0, fg_color="#2563eb")
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)  # Prevent the frame from shrinking

# Sidebar Title
title_label = ctk.CTkLabel(sidebar, text="SuperMarket", font=("Arial", 24, "bold"), text_color="white")
title_label.pack(pady=(40, 30))

# User info in sidebar
if user_logged_in:
    user_info = f"{current_user['first_name']} {current_user['last_name']}"
    user_label = ctk.CTkLabel(sidebar, text=f"Welcome, {user_info}",
                            font=("Arial", 14), text_color="white")
    user_label.pack(pady=(0, 20))

# Return to Home button
return_btn = ctk.CTkButton(sidebar, text="Return to Home",
                         fg_color="transparent", text_color="white",
                         font=("Arial", 16), anchor="w", height=40,
                         corner_radius=0, hover_color="#1d4ed8",
                         command=return_to_home)
return_btn.pack(fill="x", pady=5, padx=10)

# ---------------- Content Frame ----------------
content_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=15)
content_frame.pack(fill="both", expand=True, padx=20, pady=20)

# Header
header_label = ctk.CTkLabel(content_frame, text="Order History",
                          font=("Arial", 24, "bold"), text_color="#2563eb")
header_label.pack(anchor="w", padx=30, pady=(30, 20))

# Split view for orders - left panel for list, right panel for details
split_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
split_frame.pack(fill="both", expand=True, padx=20, pady=10)

# Orders list panel (left)
orders_panel = ctk.CTkFrame(split_frame, fg_color="white", corner_radius=10, width=300)
orders_panel.pack(side="left", fill="y", padx=(0, 10))
orders_panel.pack_propagate(False)  # Don't shrink

orders_title = ctk.CTkLabel(orders_panel, text="Your Orders",
                          font=("Arial", 18, "bold"), text_color="black")
orders_title.pack(anchor="w", padx=20, pady=(20, 10))

# Scrollable list of orders
orders_list = ctk.CTkScrollableFrame(orders_panel, fg_color="transparent")
orders_list.pack(fill="both", expand=True, padx=10, pady=10)

# Order details panel (right)
details_panel = ctk.CTkFrame(split_frame, fg_color="white", corner_radius=10)
details_panel.pack(side="right", fill="both", expand=True)

details_title = ctk.CTkLabel(details_panel, text="Order Details",
                           font=("Arial", 18, "bold"), text_color="black")
details_title.pack(anchor="w", padx=20, pady=(20, 10))

details_container = ctk.CTkScrollableFrame(details_panel, fg_color="transparent")
details_container.pack(fill="both", expand=True, padx=10, pady=10)

# Populate the orders list
populate_orders_list()

# ---------------- Run Application ----------------
app.mainloop()