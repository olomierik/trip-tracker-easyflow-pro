
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class InventoryManagement:
    def __init__(self, parent):
        self.parent = parent
        
        # Create widgets
        self.create_widgets()
        self.load_inventory()
    
    def create_widgets(self):
        # Create frames
        form_frame = ttk.LabelFrame(self.parent, text="Item Details")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        table_frame = ttk.LabelFrame(self.parent, text="Inventory Items")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
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
        
        ttk.Label(row2, text="Purchase Price ($):").pack(side=tk.LEFT, padx=(0, 5))
        self.purchase_entry = ttk.Entry(row2, width=15)
        self.purchase_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2, text="Sale Price ($):").pack(side=tk.LEFT, padx=(10, 5))
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
        columns = ("id", "item_name", "quantity", "purchase_price", "sale_price", "value")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        # Set column headings
        self.tree.heading("id", text="ID")
        self.tree.heading("item_name", text="Item Name")
        self.tree.heading("quantity", text="Quantity")
        self.tree.heading("purchase_price", text="Purchase Price ($)")
        self.tree.heading("sale_price", text="Sale Price ($)")
        self.tree.heading("value", text="Total Value ($)")
        
        # Set column widths
        self.tree.column("id", width=40)
        self.tree.column("item_name", width=200)
        self.tree.column("quantity", width=80)
        self.tree.column("purchase_price", width=120)
        self.tree.column("sale_price", width=120)
        self.tree.column("value", width=120)
        
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
            
            self.tree.insert("", tk.END, values=(item_id, name, quantity, purchase_formatted, 
                                             sale_formatted, value_formatted))
        
        conn.close()
    
    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.purchase_entry.delete(0, tk.END)
        self.sale_entry.delete(0, tk.END)
        self.update_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.add_button.config(state=tk.NORMAL)
        self.tree.selection_remove(self.tree.selection())
    
    def validate_form(self):
        try:
            # Check if fields are empty
            if not self.name_entry.get() or not self.quantity_entry.get() or \
               not self.purchase_entry.get() or not self.sale_entry.get():
                messagebox.showerror("Validation Error", "All fields are required!")
                return False
            
            # Check if quantity is a valid integer
            try:
                int(self.quantity_entry.get())
            except ValueError:
                messagebox.showerror("Validation Error", "Quantity must be a valid integer!")
                return False
                
            # Check if prices are valid numbers
            try:
                float(self.purchase_entry.get())
                float(self.sale_entry.get())
            except ValueError:
                messagebox.showerror("Validation Error", "Prices must be valid numbers!")
                return False
                
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Validation error: {str(e)}")
            return False
    
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
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add inventory item: {str(e)}")
    
    def on_select(self, event):
        try:
            # Get selected item
            selected_item = self.tree.selection()[0]
            values = self.tree.item(selected_item, "values")
            
            if not values:
                return
            
            # Clear form first
            self.clear_form()
            
            # Set values in form
            self.name_entry.insert(0, values[1])  # Name
            self.quantity_entry.insert(0, values[2])  # Quantity
            self.purchase_entry.insert(0, values[3])  # Purchase price
            self.sale_entry.insert(0, values[4])  # Sale price
            
            # Enable update and delete buttons, disable add button
            self.update_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
            self.add_button.config(state=tk.DISABLED)
            
        except IndexError:
            pass  # No selection
    
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
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update inventory item: {str(e)}")
    
    def delete_item(self):
        try:
            # Get selected item
            selected_item = self.tree.selection()[0]
            item_id = self.tree.item(selected_item, "values")[0]
            name = self.tree.item(selected_item, "values")[1]
            
            # Confirm deletion
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{name}'?")
            if not confirm:
                return
            
            # Connect to database
            conn = sqlite3.connect('easylogipro.db')
            cursor = conn.cursor()
            
            # Delete item
            cursor.execute("DELETE FROM inventory WHERE id=?", (item_id,))
            
            conn.commit()
            conn.close()
            
            # Refresh inventory and clear form
            self.load_inventory()
            self.clear_form()
            messagebox.showinfo("Success", "Inventory item deleted successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete inventory item: {str(e)}")
