
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class InventoryManagement:
    def __init__(self, parent):
        self.parent = parent
        
        # Set default low stock threshold
        self.low_stock_threshold = 5
        
        # Create widgets
        self.create_widgets()
        self.load_inventory()
    
    def create_widgets(self):
        # Create frames
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        form_frame = ttk.LabelFrame(self.parent, text="Item Details")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        table_frame = ttk.LabelFrame(self.parent, text="Inventory Items")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel widgets
        ttk.Label(control_frame, text="Low Stock Threshold:").pack(side=tk.LEFT, padx=(0, 5))
        self.threshold_entry = ttk.Entry(control_frame, width=6)
        self.threshold_entry.pack(side=tk.LEFT, padx=5)
        self.threshold_entry.insert(0, str(self.low_stock_threshold))
        
        ttk.Button(control_frame, text="Set Threshold", command=self.set_threshold).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Check Low Stock", command=self.check_low_stock).pack(side=tk.LEFT, padx=5)
        
        # Form widgets
        # Row 1
        row1 = ttk.Frame(form_frame)
        row1.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row1, text="Item Name:").pack(side=tk.LEFT, padx=(0, 5))
        self.name_entry = ttk.Entry(row1, width=30)
        self.name_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="Quantity:").pack(side=tk.LEFT, padx=(10, 5))
        self.quantity_entry = ttk.Entry(row1, width=10)
        self.quantity_entry.pack(side=tk.LEFT, padx=5)
        
        # Row 2
        row2 = ttk.Frame(form_frame)
        row2.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row2, text="Purchase Price (TZS):").pack(side=tk.LEFT, padx=(0, 5))
        self.purchase_entry = ttk.Entry(row2, width=15)
        self.purchase_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2, text="Sale Price (TZS):").pack(side=tk.LEFT, padx=(10, 5))
        self.sale_entry = ttk.Entry(row2, width=15)
        self.sale_entry.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_button = ttk.Button(button_frame, text="Add Item", command=self.add_item)
        self.add_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.update_button = ttk.Button(button_frame, text="Update Selected", command=self.update_item, state=tk.DISABLED)
        self.update_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.delete_button = ttk.Button(button_frame, text="Delete Selected", command=self.delete_item, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.clear_button = ttk.Button(button_frame, text="Clear Form", command=self.clear_form)
        self.clear_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create Treeview
        columns = ("id", "item_name", "quantity", "purchase_price", "sale_price", "value", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        # Set column headings
        self.tree.heading("id", text="ID")
        self.tree.heading("item_name", text="Item Name")
        self.tree.heading("quantity", text="Quantity")
        self.tree.heading("purchase_price", text="Purchase Price (TZS)")
        self.tree.heading("sale_price", text="Sale Price (TZS)")
        self.tree.heading("value", text="Total Value (TZS)")
        self.tree.heading("status", text="Status")
        
        # Set column widths
        self.tree.column("id", width=40)
        self.tree.column("item_name", width=200)
        self.tree.column("quantity", width=80)
        self.tree.column("purchase_price", width=120)
        self.tree.column("sale_price", width=120)
        self.tree.column("value", width=120)
        self.tree.column("status", width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind select event
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Add some padding
        for child in form_frame.winfo_children():
            child.pack_configure(pady=3)
            
        # Configure tags for status colors
        self.tree.tag_configure('low_stock', background='#ffcccc')
        self.tree.tag_configure('ok_stock', background='white')
    
    def set_threshold(self):
        try:
            new_threshold = int(self.threshold_entry.get())
            if new_threshold < 0:
                messagebox.showwarning("Invalid Value", "Threshold must be a positive number.")
                return
                
            self.low_stock_threshold = new_threshold
            messagebox.showinfo("Threshold Set", f"Low stock threshold set to {self.low_stock_threshold} items.")
            self.load_inventory()  # Reload to update status colors
        except ValueError:
            messagebox.showwarning("Invalid Value", "Please enter a valid number.")
    
    def check_low_stock(self):
        low_stock_items = []
        
        for item_id in self.tree.get_children():
            values = self.tree.item(item_id, "values")
            quantity = int(values[2])
            if quantity <= self.low_stock_threshold:
                low_stock_items.append(f"{values[1]} (Qty: {quantity})")
        
        if low_stock_items:
            message = "The following items are low in stock:\n\n"
            message += "\n".join(low_stock_items)
            messagebox.showwarning("Low Stock Alert", message)
        else:
            messagebox.showinfo("Stock Status", "All items are above the low stock threshold.")
    
    def load_inventory(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Connect to the database
        conn = sqlite3.connect('easylogipro.db')
        cursor = conn.cursor()
        
        # Get all items
        cursor.execute("SELECT * FROM inventory ORDER BY item_name")
        items = cursor.fetchall()
        
        # Add items to treeview
        for item in items:
            item_id, name, quantity, purchase_price, sale_price = item
            
            # Calculate total value based on purchase price
            total_value = quantity * purchase_price
            
            purchase_formatted = f"{float(purchase_price):.2f}"
            sale_formatted = f"{float(sale_price):.2f}"
            value_formatted = f"{float(total_value):.2f}"
            
            # Determine status based on quantity
            status = "OK"
            tag = 'ok_stock'
            
            if quantity <= self.low_stock_threshold:
                status = "LOW"
                tag = 'low_stock'
                
            self.tree.insert("", tk.END, values=(item_id, name, quantity, purchase_formatted, 
                                             sale_formatted, value_formatted, status), tags=(tag,))
        
        conn.close()
    
    # ... keep existing code (clear_form, validate_form methods)
    
    def add_item(self):
        if not self.validate_form():
            return
        
        try:
            # Get values from form
            name = self.name_entry.get()
            quantity = int(self.quantity_entry.get())
            purchase_price = float(self.purchase_entry.get())
            sale_price = float(self.sale_entry.get())
            
            # Connect to database
            conn = sqlite3.connect('easylogipro.db')
            cursor = conn.cursor()
            
            # Check if item already exists
            cursor.execute("SELECT id FROM inventory WHERE item_name=?", (name,))
            existing = cursor.fetchone()
            
            if existing:
                messagebox.showerror("Error", f"An item with the name '{name}' already exists.")
                conn.close()
                return
            
            # Insert new item
            cursor.execute('''
            INSERT INTO inventory (item_name, quantity, purchase_price, sale_price)
            VALUES (?, ?, ?, ?)
            ''', (name, quantity, purchase_price, sale_price))
            
            conn.commit()
            conn.close()
            
            # Refresh inventory and clear form
            self.load_inventory()
            self.clear_form()
            messagebox.showinfo("Success", "Inventory item added successfully!")
            
            # Check if the item is below threshold and alert
            if quantity <= self.low_stock_threshold:
                messagebox.showwarning("Low Stock Alert", f"The item '{name}' has been added with a quantity of {quantity}, which is below or at the low stock threshold ({self.low_stock_threshold}).")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add inventory item: {str(e)}")
    
    # ... keep existing code (on_select method)
    
    def update_item(self):
        if not self.validate_form():
            return
        
        try:
            # Get selected item
            selected_item = self.tree.selection()[0]
            item_id = self.tree.item(selected_item, "values")[0]
            
            # Get updated values
            name = self.name_entry.get()
            quantity = int(self.quantity_entry.get())
            purchase_price = float(self.purchase_entry.get())
            sale_price = float(self.sale_entry.get())
            
            # Confirm update
            confirm = messagebox.askyesno("Confirm Update", "Are you sure you want to update this inventory item?")
            if not confirm:
                return
            
            # Connect to database
            conn = sqlite3.connect('easylogipro.db')
            cursor = conn.cursor()
            
            # Check if updated name conflicts with another item
            cursor.execute("SELECT id FROM inventory WHERE item_name=? AND id!=?", (name, item_id))
            existing = cursor.fetchone()
            
            if existing:
                messagebox.showerror("Error", f"Another item with the name '{name}' already exists.")
                conn.close()
                return
            
            # Update item
            cursor.execute('''
            UPDATE inventory
            SET item_name=?, quantity=?, purchase_price=?, sale_price=?
            WHERE id=?
            ''', (name, quantity, purchase_price, sale_price, item_id))
            
            conn.commit()
            conn.close()
            
            # Refresh inventory and clear form
            self.load_inventory()
            self.clear_form()
            messagebox.showinfo("Success", "Inventory item updated successfully!")
            
            # Check if the updated item is below threshold
            if quantity <= self.low_stock_threshold:
                messagebox.showwarning("Low Stock Alert", f"The item '{name}' has been updated with a quantity of {quantity}, which is below or at the low stock threshold ({self.low_stock_threshold}).")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update inventory item: {str(e)}")
    
    # ... keep existing code (delete_item method)
