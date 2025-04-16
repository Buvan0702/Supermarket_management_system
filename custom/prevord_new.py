import customtkinter as ctk
from tkinter import messagebox
import mysql.connector
import subprocess
import os
import sys
from datetime import datetime

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
        host="141.209.241.57",
        user="kshat1m",
        password="mypass",  # Update with your MySQL password
        database="BIS698W1700_GRP2"
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
def get_status_color(status):
    """Return appropriate color based on order status"""
    status = status.lower()
    if status == "completed":
        return "#10b981"  # Green
    elif status == "pending":
        return "#f59e0b"  # Amber
    elif status == "cancelled":
        return "#ef4444"  # Red
    else:
        return "#6b7280"  # Gray

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
    
    # Order header with improved design
    order_header = ctk.CTkFrame(details_container, fg_color="white", corner_radius=10)
    order_header.pack(fill="x", padx=20, pady=10)
    
    # Format the date
    order_date = order["order_date"].strftime("%B %d, %Y at %I:%M %p")
    
    # Order title and ID in a row
    title_row = ctk.CTkFrame(order_header, fg_color="transparent")
    title_row.pack(fill="x", padx=20, pady=(15, 5))
    
    order_title = ctk.CTkLabel(title_row, text=f"Order #{order['order_id']}",
                              font=("Arial", 20, "bold"), text_color="#1e40af")
    order_title.pack(side="left")
    
    # Status badge
    status_color = get_status_color(order["status"])
    status_badge = ctk.CTkFrame(title_row, fg_color=status_color, corner_radius=15, height=30)
    status_badge.pack(side="right", padx=5)
    
    status_text = ctk.CTkLabel(status_badge, text=order["status"].capitalize(),
                              font=("Arial", 12, "bold"), text_color="white")
    status_text.pack(padx=10, pady=5)
    
    # Order date with icon
    date_frame = ctk.CTkFrame(order_header, fg_color="transparent")
    date_frame.pack(fill="x", padx=20, pady=(0, 5))
    
    date_label = ctk.CTkLabel(date_frame, text=f"📅 {order_date}",
                            font=("Arial", 14), text_color="#4b5563")
    date_label.pack(anchor="w")
    
    # Total amount with icon
    total_frame = ctk.CTkFrame(order_header, fg_color="transparent")
    total_frame.pack(fill="x", padx=20, pady=(0, 15))
    
    total_label = ctk.CTkLabel(total_frame, text=f"💰 Total: ${float(order['total_amount']):.2f}",
                              font=("Arial", 16, "bold"), text_color="#1e40af")
    total_label.pack(anchor="w")
    
    # Divider
    divider = ctk.CTkFrame(order_header, height=1, fg_color="#e5e7eb")
    divider.pack(fill="x", padx=20, pady=(0, 15))
    
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
                              font=("Arial", 18, "bold"), text_color="#1e40af")
    items_header.pack(anchor="w", padx=20, pady=(15, 10))
    
    # Table header with improved design
    header_frame = ctk.CTkFrame(items_frame, fg_color="#f3f4f6", corner_radius=5)
    header_frame.pack(fill="x", padx=20, pady=(5, 0))
    
    # Header columns with better spacing
    ctk.CTkLabel(header_frame, text="Item", font=("Arial", 14, "bold"), text_color="#4b5563").pack(side="left", padx=20, pady=10)
    ctk.CTkLabel(header_frame, text="Price", font=("Arial", 14, "bold"), text_color="#4b5563").pack(side="left", expand=True, pady=10)
    ctk.CTkLabel(header_frame, text="Quantity", font=("Arial", 14, "bold"), text_color="#4b5563").pack(side="left", padx=20, pady=10)
    ctk.CTkLabel(header_frame, text="Subtotal", font=("Arial", 14, "bold"), text_color="#4b5563").pack(side="right", padx=20, pady=10)
    
    # Item rows with alternating colors
    for i, item in enumerate(items):
        # Alternate row colors
        row_color = "white" if i % 2 == 0 else "#f9fafb"
        
        item_row = ctk.CTkFrame(items_frame, fg_color=row_color)
        item_row.pack(fill="x", padx=20, pady=2)
        
        price = float(item["price"])
        quantity = item["quantity"]
        subtotal = price * quantity
        
        ctk.CTkLabel(item_row, text=item["name"], font=("Arial", 14), text_color="#1f2937").pack(side="left", padx=20, pady=10)
        ctk.CTkLabel(item_row, text=f"${price:.2f}", font=("Arial", 14), text_color="#4b5563").pack(side="left", expand=True, pady=10)
        ctk.CTkLabel(item_row, text=str(quantity), font=("Arial", 14), text_color="#4b5563").pack(side="left", padx=20, pady=10)
        ctk.CTkLabel(item_row, text=f"${subtotal:.2f}", font=("Arial", 14, "bold"), text_color="#1e40af").pack(side="right", padx=20, pady=10)
    
    # Summary section
    summary_frame = ctk.CTkFrame(items_frame, fg_color="#f3f4f6", corner_radius=5)
    summary_frame.pack(fill="x", padx=20, pady=(10, 15))
    
    # Subtotal
    subtotal_row = ctk.CTkFrame(summary_frame, fg_color="transparent")
    subtotal_row.pack(fill="x", padx=20, pady=5)
    
    ctk.CTkLabel(subtotal_row, text="Subtotal:", font=("Arial", 14), text_color="#4b5563").pack(side="left")
    ctk.CTkLabel(subtotal_row, text=f"${float(order['total_amount']):.2f}", font=("Arial", 14), text_color="#4b5563").pack(side="right")
    
    # Tax (estimated at 10%)
    tax = float(order['total_amount']) * 0.1
    tax_row = ctk.CTkFrame(summary_frame, fg_color="transparent")
    tax_row.pack(fill="x", padx=20, pady=5)
    
    ctk.CTkLabel(tax_row, text="Tax (10%):", font=("Arial", 14), text_color="#4b5563").pack(side="left")
    ctk.CTkLabel(tax_row, text=f"${tax:.2f}", font=("Arial", 14), text_color="#4b5563").pack(side="right")
    
    # Total with divider
    divider2 = ctk.CTkFrame(summary_frame, height=1, fg_color="#d1d5db")
    divider2.pack(fill="x", padx=20, pady=5)
    
    total_row = ctk.CTkFrame(summary_frame, fg_color="transparent")
    total_row.pack(fill="x", padx=20, pady=5)
    
    ctk.CTkLabel(total_row, text="Total:", font=("Arial", 16, "bold"), text_color="#1e40af").pack(side="left")
    ctk.CTkLabel(total_row, text=f"${float(order['total_amount']):.2f}", font=("Arial", 16, "bold"), text_color="#1e40af").pack(side="right")

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
    
    # Add each order to the list with improved design
    for order in orders:
        # Create a card for each order
        order_card = ctk.CTkFrame(orders_list, fg_color="white", corner_radius=10)
        order_card.pack(fill="x", padx=10, pady=5)
        
        # Order ID and date row
        header_row = ctk.CTkFrame(order_card, fg_color="transparent")
        header_row.pack(fill="x", padx=15, pady=(10, 5))
        
        order_id_label = ctk.CTkLabel(header_row, text=f"Order #{order['order_id']}", 
                                    font=("Arial", 16, "bold"), text_color="#1e40af")
        order_id_label.pack(side="left")
        
        # Status badge
        status_color = get_status_color(order["status"])
        status_badge = ctk.CTkFrame(header_row, fg_color=status_color, corner_radius=15, height=25)
        status_badge.pack(side="right", padx=5)
        
        status_text = ctk.CTkLabel(status_badge, text=order["status"].capitalize(),
                                  font=("Arial", 10, "bold"), text_color="white")
        status_text.pack(padx=8, pady=3)
        
        # Date row
        date_row = ctk.CTkFrame(order_card, fg_color="transparent")
        date_row.pack(fill="x", padx=15, pady=(0, 5))
        
        date_text = order["order_date"].strftime("%B %d, %Y")
        date_label = ctk.CTkLabel(date_row, text=f"📅 {date_text}", 
                                font=("Arial", 12), text_color="#4b5563")
        date_label.pack(side="left")
        
        # Total amount row
        total_row = ctk.CTkFrame(order_card, fg_color="transparent")
        total_row.pack(fill="x", padx=15, pady=(0, 10))
        
        total_text = f"💰 ${float(order['total_amount']):.2f}"
        total_label = ctk.CTkLabel(total_row, text=total_text, 
                                 font=("Arial", 14, "bold"), text_color="#1e40af")
        total_label.pack(side="left")
        
        # View details button
        view_btn = ctk.CTkButton(order_card, text="View Details", 
                               fg_color="#2563eb", hover_color="#1d4ed8", 
                               font=("Arial", 12), height=30, width=100,
                               command=lambda id=order['order_id']: display_order_details(id))
        view_btn.pack(side="right", padx=15, pady=(0, 10))
    
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
app.title("SuperMarket - Order History")
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
# Create a container for the entire app
app_container = ctk.CTkFrame(app, fg_color="#f3f4f6", corner_radius=0)
app_container.pack(fill="both", expand=True)

# ---------------- Top Navigation Bar ----------------
top_nav = ctk.CTkFrame(app_container, fg_color="#2563eb", corner_radius=0, height=60)
top_nav.pack(fill="x", side="top")
top_nav.pack_propagate(False)  # Prevent the frame from shrinking

# Logo and title in the top nav
logo_frame = ctk.CTkFrame(top_nav, fg_color="transparent")
logo_frame.pack(side="left", padx=20, pady=10)

logo_label = ctk.CTkLabel(logo_frame, text="SuperMarket", font=("Arial", 20, "bold"), text_color="white")
logo_label.pack(side="left")

# User info in top nav
if user_logged_in:
    user_info = f"{current_user['first_name']} {current_user['last_name']}"
    user_label = ctk.CTkLabel(top_nav, text=f"Welcome, {user_info}",
                            font=("Arial", 14), text_color="white")
    user_label.pack(side="left", padx=20, pady=10)

# Return to Home button in top nav
return_btn = ctk.CTkButton(top_nav, text="Return to Home",
                         fg_color="transparent", text_color="white",
                         font=("Arial", 14), height=30, width=120,
                         corner_radius=15, hover_color="#1d4ed8",
                         command=return_to_home)
return_btn.pack(side="right", padx=20, pady=10)

# ---------------- Main Content Area ----------------
main_content = ctk.CTkFrame(app_container, fg_color="#f3f4f6", corner_radius=0)
main_content.pack(fill="both", expand=True, padx=20, pady=20)

# Content Frame
content_frame = ctk.CTkFrame(main_content, fg_color="white", corner_radius=15)
content_frame.pack(fill="both", expand=True)

# Header with improved design
header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
header_frame.pack(fill="x", padx=30, pady=(30, 20))

header_label = ctk.CTkLabel(header_frame, text="Order History",
                          font=("Arial", 24, "bold"), text_color="#1e40af")
header_label.pack(side="left")

# Add a subtitle
subtitle_label = ctk.CTkLabel(header_frame, text="View and manage your past orders",
                            font=("Arial", 14), text_color="#6b7280")
subtitle_label.pack(side="left", padx=(10, 0), pady=(5, 0))

# Split view for orders - left panel for list, right panel for details
split_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
split_frame.pack(fill="both", expand=True, padx=20, pady=10)

# Orders list panel (left)
orders_panel = ctk.CTkFrame(split_frame, fg_color="white", corner_radius=10, width=350)
orders_panel.pack(side="left", fill="y", padx=(0, 10))
orders_panel.pack_propagate(False)  # Don't shrink

orders_title = ctk.CTkLabel(orders_panel, text="Your Orders",
                          font=("Arial", 18, "bold"), text_color="#1e40af")
orders_title.pack(anchor="w", padx=20, pady=(20, 10))

# Scrollable list of orders
orders_list = ctk.CTkScrollableFrame(orders_panel, fg_color="transparent")
orders_list.pack(fill="both", expand=True, padx=10, pady=10)

# Order details panel (right)
details_panel = ctk.CTkFrame(split_frame, fg_color="white", corner_radius=10)
details_panel.pack(side="right", fill="both", expand=True)

details_title = ctk.CTkLabel(details_panel, text="Order Details",
                           font=("Arial", 18, "bold"), text_color="#1e40af")
details_title.pack(anchor="w", padx=20, pady=(20, 10))

details_container = ctk.CTkScrollableFrame(details_panel, fg_color="transparent")
details_container.pack(fill="both", expand=True, padx=10, pady=10)

# Populate the orders list
populate_orders_list()

# ---------------- Run Application ----------------
app.mainloop() 