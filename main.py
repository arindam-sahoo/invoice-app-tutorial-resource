import sqlite3
import tkinter as tk
from tkinter import messagebox

def create_database():
    conn = sqlite3.connect('invoice.db')
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            name TEXT,
            price REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            date TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoice_items (
            item_id INTEGER PRIMARY KEY,
            invoice_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY (invoice_id) REFERENCES invoices (invoice_id),
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
    ''')

    conn.commit()
    conn.close()

def is_number(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def add_customer(name, email):
    conn = sqlite3.connect('invoice.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO customers (name, email) VALUES (?, ?)', (name, email))

    conn.commit()
    conn.close()

def add_product(name, price):
    conn = sqlite3.connect('invoice.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO products (name, price) VALUES (?, ?)', (name, price))

    conn.commit()
    conn.close()

def create_invoice(customer_id, date, items):
    conn = sqlite3.connect('invoice.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO invoices (customer_id, date) VALUES (?, ?)', (customer_id, date))
    invoice_id = cursor.lastrowid

    for item in items:
        cursor.execute('INSERT INTO invoice_items (invoice_id, product_id, quantity) VALUES (?, ?, ?)',
                       (invoice_id, item['product_id'], item['quantity']))

    conn.commit()
    conn.close()

def generate_invoice_report(invoice_id):
    conn = sqlite3.connect('invoice.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT customers.name as customer_name, customers.email as customer_email,
               invoices.date as invoice_date,
               products.name as product_name, products.price as product_price,
               invoice_items.quantity
        FROM invoices
        JOIN customers ON invoices.customer_id = customers.customer_id
        JOIN invoice_items ON invoices.invoice_id = invoice_items.invoice_id
        JOIN products ON invoice_items.product_id = products.product_id
        WHERE invoices.invoice_id = ?
    ''', (invoice_id,))

    rows = cursor.fetchall()

    # Display the invoice report
    if rows:
        print(f"Invoice ID: {invoice_id}")
        print(f"Customer: {rows[0][0]} ({rows[0][1]})")
        print(f"Date: {rows[0][2]}")
        print("\nInvoice Items:")
        total_quantity = 0
        total_amount = 0
        for row in rows:
            product_name, product_price, quantity = row[3], row[4], row[5]
            amount = product_price * quantity
            total_quantity += quantity
            total_amount += amount
            print(f"{product_name} - Quantity: {quantity} - Price: ${product_price:.2f} - Amount: ${amount:.2f}")
        print(f"\nTotal Quantity:{total_quantity}")
        print("\nTotal Amount: ${:.2f}".format(total_amount))
    else:
        print(f"No invoice found with ID {invoice_id}")

    conn.close()

class InvoiceApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Invoice App")

        # Create the database and tables
        create_database()

        # Label and Entry for Customer
        tk.Label(master, text="Customer Name:").grid(row=0, column=0, padx=10, pady=10)
        self.customer_name_entry = tk.Entry(master)
        self.customer_name_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(master, text="Customer Email:").grid(row=1, column=0, padx=10, pady=10)
        self.customer_email_entry = tk.Entry(master)
        self.customer_email_entry.grid(row=1, column=1, padx=10, pady=10)

        # Button to add customer
        tk.Button(master, text="Add Customer", command=self.add_customer).grid(row=2, column=0, columnspan=2, pady=10)

        # Label and Entry for Product
        tk.Label(master, text="Product Name:").grid(row=3, column=0, padx=10, pady=10)
        self.product_name_entry = tk.Entry(master)
        self.product_name_entry.grid(row=3, column=1, padx=10, pady=10)

        tk.Label(master, text="Product Price:").grid(row=4, column=0, padx=10, pady=10)
        self.product_price_entry = tk.Entry(master)
        self.product_price_entry.grid(row=4, column=1, padx=10, pady=10)

        # Button to add product
        tk.Button(master, text="Add Product", command=self.add_product).grid(row=5, column=0, columnspan=2, pady=10)

        # Invoice creation section
        tk.Label(master, text="Invoice Date:").grid(row=6, column=0, padx=10, pady=10)
        self.invoice_date_entry = tk.Entry(master)
        self.invoice_date_entry.grid(row=6, column=1, padx=10, pady=10)

        tk.Label(master, text="Enter Items (Format: [{'product_id': 1, 'quantity': 2}, ...]):").grid(row=7, column=0, columnspan=2, pady=10)
        self.invoice_items_text = tk.Text(master, height=4, width=40)
        self.invoice_items_text.grid(row=8, column=0, columnspan=2, pady=10)

        # Button to create invoice
        tk.Button(master, text="Create Invoice", command=self.create_invoice).grid(row=9, column=0, columnspan=2, pady=10)

    def add_customer(self):
        name = self.customer_name_entry.get()
        email = self.customer_email_entry.get()

        if name and email:
            add_customer(name, email)
            messagebox.showinfo("Success", "Customer added successfully.")
        else:
            messagebox.showerror("Error", "Please enter both customer name and email.")

    def add_product(self):
        name = self.product_name_entry.get()
        price = self.product_price_entry.get()
        
        while not is_number(price) or float(price) < 0:
            messagebox.showerror("Error", "Please Enter a Positive Numeric Price.")
            return None

        if name and price:
            add_product(name, float(price))
            messagebox.showinfo("Success", "Product added successfully.")
        else:
            messagebox.showerror("Error", "Please enter both product name and price.")

    def create_invoice(self):
        customer_id = 1  # Replace with actual customer ID (you may fetch it from the database)
        date = self.invoice_date_entry.get()
        items_text = self.invoice_items_text.get("1.0", "end-1c")

        try:
            items = eval(items_text)  # Convert the string representation to a list
            create_invoice(customer_id, date, items)
            messagebox.showinfo("Success", "Invoice created successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Error creating invoice: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceApp(root)
    root.mainloop()