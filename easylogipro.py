
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os
from trip_management import TripManagement
from vehicle_maintenance import VehicleMaintenance
from driver_payment import DriverPayment
from inventory_management import InventoryManagement
from customer_ledger import CustomerLedger

class EasyLogiPro:
    def __init__(self, root):
        self.root = root
        self.root.title("EasyLogiPro - Logistics Management System")
        self.root.geometry("1000x600")
        self.root.minsize(800, 500)
        
        # Check if database exists, if not create it
        self.setup_database()
        
        # Create main menu
        self.create_menu()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initialize modules
        self.trip_tab = tk.Frame(self.notebook)
        self.maintenance_tab = tk.Frame(self.notebook)
        self.driver_tab = tk.Frame(self.notebook)
        self.inventory_tab = tk.Frame(self.notebook)
        self.customer_tab = tk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.trip_tab, text="Trip Management")
        self.notebook.add(self.maintenance_tab, text="Vehicle Maintenance")
        self.notebook.add(self.driver_tab, text="Driver Payments")
        self.notebook.add(self.inventory_tab, text="Inventory")
        self.notebook.add(self.customer_tab, text="Customer Ledger")
        
        # Load modules
        self.trip_management = TripManagement(self.trip_tab)
        self.vehicle_maintenance = VehicleMaintenance(self.maintenance_tab)
        self.driver_payment = DriverPayment(self.driver_tab)
        self.inventory_management = InventoryManagement(self.inventory_tab)
        self.customer_ledger = CustomerLedger(self.customer_tab)
        
        # Status bar
        self.status_bar = ttk.Label(root, text="EasyLogiPro - Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Backup Database", command=self.backup_database)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def setup_database(self):
        """Create the database and tables if they don't exist"""
        conn = sqlite3.connect('easylogipro.db')
        cursor = conn.cursor()
        
        # Create trips table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            client_name TEXT NOT NULL,
            cargo_type TEXT NOT NULL,
            route TEXT NOT NULL,
            trip_income REAL NOT NULL,
            fuel_expenses REAL NOT NULL,
            driver_name TEXT NOT NULL
        )
        ''')
        
        # Create maintenance table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS maintenance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_plate_number TEXT NOT NULL,
            service_date TEXT NOT NULL,
            description TEXT NOT NULL,
            cost REAL NOT NULL
        )
        ''')
        
        # Create inventory table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            purchase_price REAL NOT NULL,
            sale_price REAL NOT NULL
        )
        ''')
        
        # Create customer_transactions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            date TEXT NOT NULL,
            amount_owed REAL NOT NULL,
            amount_paid REAL NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def backup_database(self):
        """Create a backup of the database"""
        import shutil
        from datetime import datetime
        
        # Create backups directory if it doesn't exist
        if not os.path.exists('backups'):
            os.makedirs('backups')
        
        backup_path = f"backups/easylogipro_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        try:
            shutil.copy2('easylogipro.db', backup_path)
            messagebox.showinfo("Backup Successful", f"Database backed up to {backup_path}")
        except Exception as e:
            messagebox.showerror("Backup Failed", f"Error creating backup: {str(e)}")
    
    def show_about(self):
        about_text = "EasyLogiPro v1.0\n\nA logistics management application for small trucking businesses."
        messagebox.showinfo("About EasyLogiPro", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = EasyLogiPro(root)
    root.mainloop()
