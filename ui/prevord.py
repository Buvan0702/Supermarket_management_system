import customtkinter as ctk
from tkinter import ttk, Canvas

# ---------------- Initialize Application ----------------
ctk.set_appearance_mode("light")  # Options: "dark", "light", "system"
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("SuperMarket - Previous Orders")
app.geometry("900x500")
app.resizable(False, False)

# ---------------- Sidebar (Blue Navigation Menu) ----------------
sidebar = ctk.CTkFrame(app, width=180, height=500, fg_color="#2563eb", corner_radius=0)
sidebar.pack(side="left", fill="y")

# Sidebar Title
title_label = ctk.CTkLabel(sidebar, text="SuperMarket", font=("Arial", 16, "bold"), text_color="white")
title_label.pack(pady=20)

# Sidebar Buttons
menu_items = ["Home", "Cart", "Previous Orders", "Logout"]

def menu_click(item):
    ctk.CTkMessagebox(title="Navigation", message=f"You clicked: {item}")

for item in menu_items:
    btn = ctk.CTkButton(sidebar, text=item, fg_color="transparent", text_color="white",
                        hover_color="#1d4ed8", corner_radius=5,
                        command=lambda i=item: menu_click(i))
    btn.pack(fill="x", pady=5, padx=10)

# ---------------- Main Content ----------------
main_frame = ctk.CTkFrame(app, fg_color="#f2f2f2")
main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

# Header
header_label = ctk.CTkLabel(main_frame, text="Previous Orders", font=("Arial", 18, "bold"), text_color="#2563eb")
header_label.pack(anchor="w", pady=5)

# ---------------- Scrollable Orders Section ----------------
orders_frame_container = ctk.CTkFrame(main_frame, fg_color="#f2f2f2")
orders_frame_container.pack(fill="both", expand=True, pady=10)

canvas = Canvas(orders_frame_container, bg="#f2f2f2", highlightthickness=0)
scrollbar = ctk.CTkScrollbar(orders_frame_container, command=canvas.yview)
scrollable_frame = ctk.CTkFrame(canvas, fg_color="#f2f2f2")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Enable mouse scrolling
def on_mouse_wheel(event):
    canvas.yview_scroll(-1 * (event.delta // 120), "units")

canvas.bind_all("<MouseWheel>", on_mouse_wheel)

# ---------------- Orders Data ----------------
orders = [
    {"order_no": "Order #1", "items": [("Apples", "$2.00"), ("Bananas", "$1.50"), ("Broccoli", "$1.80")], "total": "$5.30"},
    {"order_no": "Order #2", "items": [("Bread", "$2.50"), ("Milk", "$3.00"), ("Eggs", "$2.00")], "total": "$7.50"},
    {"order_no": "Order #3", "items": [("Chicken", "$8.00"), ("Rice", "$2.00"), ("Broccoli", "$1.80")], "total": "$11.80"},
    {"order_no": "Order #4", "items": [("Carrots", "$1.00"), ("Spinach", "$2.50"), ("Avocado", "$3.00")], "total": "$6.50"},
    {"order_no": "Order #5", "items": [("Milk", "$3.00"), ("Cheese", "$4.00"), ("Yogurt", "$2.50")], "total": "$9.50"}
]

# ---------------- Creating Order Boxes ----------------
for order in orders:
    order_frame = ctk.CTkFrame(scrollable_frame, fg_color="white", border_width=1, corner_radius=5)
    order_frame.pack(fill="x", pady=10, padx=5, ipadx=5, ipady=5)

    # Order Title
    ctk.CTkLabel(order_frame, text=order["order_no"], font=("Arial", 13, "bold"), text_color="black").pack(anchor="w", padx=10)

    # Order Items
    for item, price in order["items"]:
        item_row = ctk.CTkFrame(order_frame, fg_color="white")
        item_row.pack(fill="x", padx=10, pady=2)

        ctk.CTkLabel(item_row, text=f"{item}  -  ", font=("Arial", 11), text_color="black").pack(side="left")
        ctk.CTkLabel(item_row, text=price, font=("Arial", 11), text_color="black").pack(side="right")

    # Total Row
    total_row = ctk.CTkFrame(order_frame, fg_color="white")
    total_row.pack(fill="x", padx=10, pady=8)

    ctk.CTkLabel(total_row, text="Total:", font=("Arial", 11, "bold"), text_color="black").pack(side="left")
    ctk.CTkLabel(total_row, text=order["total"], font=("Arial", 11, "bold"), text_color="black").pack(side="right")

# ---------------- Run Application ----------------
app.mainloop()
