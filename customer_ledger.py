
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkcalendar import DateEntry

class CustomerLedger:
    def __init__(self, parent):
        self.parent = parent
        
        # Create a notebook for transactions and balances tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.transactions_tab = ttk.Frame(self.notebook)
        self.balances_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.transactions_tab, text="Transactions")
        self.notebook.add(self.balances_tab, text="Customer Balances")
        
        # Initialize both tabs
        self.setup_transactions_tab()
        self.setup_balances_tab()
        
        # Initial data load
        self.load_transactions()
        self.load_balances()
    
    def setup_transactions_tab(self):
        # Create frames
        form_frame = ttk.LabelFrame(self.transactions_tab, text="Transaction Details")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        table_frame = ttk.LabelFrame(self.transactions_tab, text="Transaction Records")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Form widgets
        # Row 1
        row1 = ttk.Frame(form_frame)
        row1.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row1, text="Customer Name:").pack(side=tk.LEFT, padx=(0, 5))
        self.customer_entry = ttk.Entry(row1, width=25)
        self.customer_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="Date:").pack(side=tk.LEFT, padx=(10, 5))
        self.date_entry = DateEntry(row1, width=12, background='darkblue',
                                  foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.pack(side=tk.LEFT, padx=5)
        
        # Row 2
        row2 = ttk.Frame(form_frame)
        row2.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row2, text="Amount Owed ($):").pack(side=tk.LEFT, padx=(0, 5))
        self.owed_entry = ttk.Entry(row2, width=15)
        self.owed_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2, text="Amount Paid ($):").pack(side=tk.LEFT, padx=(10, 5))
        self.paid_entry = ttk.Entry(row2, width=15)
        self.paid_entry.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_button = ttk.Button(button_frame, text="Add Transaction", command=self.add_transaction)
        self.add_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.update_button = ttk.Button(button_frame, text="Update Selected", command=self.update_transaction, state=tk.DISABLED)
        self.update_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.delete_button = ttk.Button(button_frame, text="Delete Selected", command=self.delete_transaction, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.clear_button = ttk.Button(button_frame, text="Clear Form", command=self.clear_form)
        self.clear_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create Treeview for transactions
        columns = ("id", "customer_name", "date", "amount_owed", "amount_paid", "balance")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        # Set column headings
        self.tree.heading("id", text="ID")
        self.tree.heading("customer_name", text="Customer Name")
        self.tree.heading("date", text="Date")
        self.tree.heading("amount_owed", text="Amount Owed ($)")
        self.tree.heading("amount_paid", text="Amount Paid ($)")
        self.tree.heading("balance", text="Balance ($)")
        
        # Set column widths
        self.tree.column("id", width=40)
        self.tree.column("customer_name", width=150)
        self.tree.column("date", width=100)
        self.tree.column("amount_owed", width=120)
        self.tree.column("amount_paid", width=120)
        self.tree.column("balance", width=120)
        
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
    
    def setup_balances_tab(self):
        # Create frame for balances
        control_frame = ttk.Frame(self.balances_tab)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.refresh_btn = ttk.Button(control_frame, text="Refresh Balances", command=self.load_balances)
        self.refresh_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        table_frame = ttk.LabelFrame(self.balances_tab, text="Customer Balances")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create Treeview for balances
        columns = ("customer_name", "balance")
        self.balance_tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        # Set column headings
        self.balance_tree.heading("customer_name", text="Customer Name")
        self.balance_tree.heading("balance", text="Outstanding Balance ($)")
        
        # Set column widths
        self.balance_tree.column("customer_name", width=200)
        self.balance_tree.column("balance", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.balance_tree.yview)
        self.balance_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.balance_tree.pack(fill=tk.BOTH, expand=True)
    
    def load_transactions(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Connect to the database
        conn = sqlite3.connect('easylogipro.db')
        cursor = conn.cursor()
        
        # Get all transactions ordered by date
        cursor.execute("SELECT * FROM customer_transactions ORDER BY date DESC")
        transactions = cursor.fetchall()
        
        # Add transactions to treeview
        for transaction in transactions:
            t_id, customer_name, date, amount_owed, amount_paid = transaction
            
            # Calculate balance for this transaction
            balance = amount_owed - amount_paid
            
            owed_formatted = f"{float(amount_owed):.2f}"
            paid_formatted = f"{float(amount_paid):.2f}"
            balance_formatted = f"{float(balance):.2f}"
            
            self.tree.insert("", tk.END, values=(t_id, customer_name, date, owed_formatted, 
                                               paid_formatted, balance_formatted))
        
        conn.close()
    
    def load_balances(self):
        # Clear existing items
        for item in self.balance_tree.get_children():
            self.balance_tree.delete(item)
        
        try:
            # Connect to the database
            conn = sqlite3.connect('easylogipro.db')
            cursor = conn.cursor()
            
            # Get customer balances
            cursor.execute('''
            SELECT 
                customer_name,
                SUM(amount_owed) - SUM(amount_paid) as balance
            FROM customer_transactions
            GROUP BY customer_name
            ORDER BY balance DESC
            ''')
            
            balances = cursor.fetchall()
            
            # Add balances to treeview
            for balance in balances:
                customer_name, amount = balance
                
                # Only show customers with non-zero balance
                if amount != 0:
                    amount_formatted = f"{float(amount):.2f}"
                    
                    # Use red for positive balances (money owed)
                    tag = 'positive' if amount > 0 else 'negative'
                    
                    self.balance_tree.insert("", tk.END, values=(customer_name, amount_formatted), tags=(tag,))
            
            # Configure tags
            self.balance_tree.tag_configure('positive', foreground='red')
            self.balance_tree.tag_configure('negative', foreground='green')
            
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customer balances: {str(e)}")
    
    def clear_form(self):
        self.customer_entry.delete(0, tk.END)
        self.date_entry.set_date(None)
        self.owed_entry.delete(0, tk.END)
        self.paid_entry.delete(0, tk.END)
        self.update_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.add_button.config(state=tk.NORMAL)
        self.tree.selection_remove(self.tree.selection())
    
    def validate_form(self):
        try:
            # Check if fields are empty
            if not self.customer_entry.get() or not self.date_entry.get() or \
               not self.owed_entry.get() or not self.paid_entry.get():
                messagebox.showerror("Validation Error", "All fields are required!")
                return False
            
            # Check if amounts are valid numbers
            try:
                float(self.owed_entry.get())
                float(self.paid_entry.get())
            except ValueError:
                messagebox.showerror("Validation Error", "Amounts must be valid numbers!")
                return False
            
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Validation error: {str(e)}")
            return False
    
    def add_transaction(self):
        if not self.validate_form():
            return
        
        try:
            # Get values from form
            customer_name = self.customer_entry.get()
            date = self.date_entry.get()
            amount_owed = float(self.owed_entry.get())
            amount_paid = float(self.paid_entry.get())
            
            # Connect to database
            conn = sqlite3.connect('easylogipro.db')
            cursor = conn.cursor()
            
            # Insert new transaction
            cursor.execute('''
            INSERT INTO customer_transactions (customer_name, date, amount_owed, amount_paid)
            VALUES (?, ?, ?, ?)
            ''', (customer_name, date, amount_owed, amount_paid))
            
            conn.commit()
            conn.close()
            
            # Refresh transactions and balances
            self.load_transactions()
            self.load_balances()
            self.clear_form()
            messagebox.showinfo("Success", "Transaction added successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add transaction: {str(e)}")
    
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
            self.customer_entry.insert(0, values[1])  # Customer
            self.date_entry.set_date(values[2])  # Date
            self.owed_entry.insert(0, values[3])  # Amount owed
            self.paid_entry.insert(0, values[4])  # Amount paid
            
            # Enable update and delete buttons, disable add button
            self.update_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
            self.add_button.config(state=tk.DISABLED)
            
        except IndexError:
            pass  # No selection
    
    def update_transaction(self):
        if not self.validate_form():
            return
        
        try:
            # Get selected item
            selected_item = self.tree.selection()[0]
            transaction_id = self.tree.item(selected_item, "values")[0]
            
            # Get updated values
            customer_name = self.customer_entry.get()
            date = self.date_entry.get()
            amount_owed = float(self.owed_entry.get())
            amount_paid = float(self.paid_entry.get())
            
            # Confirm update
            confirm = messagebox.askyesno("Confirm Update", "Are you sure you want to update this transaction?")
            if not confirm:
                return
            
            # Connect to database
            conn = sqlite3.connect('easylogipro.db')
            cursor = conn.cursor()
            
            # Update transaction
            cursor.execute('''
            UPDATE customer_transactions
            SET customer_name=?, date=?, amount_owed=?, amount_paid=?
            WHERE id=?
            ''', (customer_name, date, amount_owed, amount_paid, transaction_id))
            
            conn.commit()
            conn.close()
            
            # Refresh transactions and balances
            self.load_transactions()
            self.load_balances()
            self.clear_form()
            messagebox.showinfo("Success", "Transaction updated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update transaction: {str(e)}")
    
    def delete_transaction(self):
        try:
            # Get selected item
            selected_item = self.tree.selection()[0]
            transaction_id = self.tree.item(selected_item, "values")[0]
            
            # Confirm deletion
            confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this transaction?")
            if not confirm:
                return
            
            # Connect to database
            conn = sqlite3.connect('easylogipro.db')
            cursor = conn.cursor()
            
            # Delete transaction
            cursor.execute("DELETE FROM customer_transactions WHERE id=?", (transaction_id,))
            
            conn.commit()
            conn.close()
            
            # Refresh transactions and balances
            self.load_transactions()
            self.load_balances()
            self.clear_form()
            messagebox.showinfo("Success", "Transaction deleted successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete transaction: {str(e)}")
