"""
Navigation frame for the Supermarket Admin Interface
"""

import customtkinter as ctk
import subprocess
import os

class AdminNavigationFrame:
    def __init__(self, parent, user_info, navigate_callback):
        """
        Create a navigation sidebar for the admin interface
        
        Parameters:
        - parent: The parent widget
        - user_info: Dictionary with user information
        - navigate_callback: Function to call when a navigation option is selected
        """
        self.parent = parent
        self.user_info = user_info
        self.navigate_callback = navigate_callback
        
        # Create the sidebar frame
        self.sidebar = ctk.CTkFrame(parent, width=250, height=700, corner_radius=0, fg_color="#2563eb")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)  # Prevent the frame from shrinking
        
        # Create the sidebar content
        self._create_sidebar_content()
    
    def _create_sidebar_content(self):
        """Create the content of the sidebar"""
        # Sidebar Title
        title_label = ctk.CTkLabel(self.sidebar, text="Admin Panel", 
                                 font=("Arial", 24, "bold"), text_color="white")
        title_label.pack(pady=(40, 30))
        
        # Admin info display
        if self.user_info.get("first_name") and self.user_info.get("last_name"):
            admin_info = f"{self.user_info['first_name']} {self.user_info['last_name']}"
            admin_label = ctk.CTkLabel(self.sidebar, text=f"Admin: {admin_info}", 
                                     font=("Arial", 14), text_color="white")
            admin_label.pack(pady=(0, 20))
        
        # Sidebar Buttons
        menu_items = ["Manage Inventory", "Manage Users", "Generate Report", "Logout"]
        
        for item in menu_items:
            btn = ctk.CTkButton(self.sidebar, text=item, fg_color="transparent", 
                               text_color="white", font=("Arial", 16),
                               anchor="w", height=40,
                               corner_radius=0, hover_color="#1d4ed8",
                               command=lambda i=item: self.navigate_callback(i))
            btn.pack(fill="x", pady=5, padx=10)
    
    def highlight_option(self, option):
        """
        Highlight the selected navigation option
        
        Parameters:
        - option: The navigation option to highlight
        """
        # For a more advanced implementation, each button would need to be 
        # stored as an instance variable to modify its appearance
        pass