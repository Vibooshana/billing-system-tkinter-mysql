import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from datetime import date

# ---------------- DATABASE CONNECTION ----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="25@Viboo",
    database="billing_system"
)
cursor = db.cursor()

# ---------------- LOGIN ----------------
def login():
    u = user.get()
    p = pwd.get()

    cursor.execute("SELECT password FROM users WHERE username=%s", (u,))
    r = cursor.fetchone()

    if r:
        if r[0] == p:
            lf.pack_forget()
            menu()
        else:
            messagebox.showerror("Error", "Wrong Password")
    else:
        messagebox.showerror("Error", "User does not exist")

# ---------------- MENU ----------------
def menu():
    global mf
    mf = tk.Frame(root, bg="#f0f8ff")
    mf.pack(fill="both", expand=True)

    tk.Label(mf, text="Billing System", bg="#f0f8ff",
             font=("Arial", 18, "bold")).pack(pady=15)

    btn = {"width": 20, "bg": "#a0d2eb", "font": ("Arial", 12)}

    tk.Button(mf, text="View Products", command=view_products, **btn).pack(pady=5)
    tk.Button(mf, text="Update Product", command=update_product, **btn).pack(pady=5)
    tk.Button(mf, text="Delete Product", command=delete_product, **btn).pack(pady=5)
    tk.Button(mf, text="Create Bill", command=create_bill, **btn).pack(pady=5)

# ---------------- VIEW PRODUCTS ----------------
def view_products():
    mf.pack_forget()
    global vf
    vf = tk.Frame(root, bg="#ffffff")
    vf.pack(fill="both", expand=True)

    tree = ttk.Treeview(vf, columns=("ID","Name","Price","Stock","Category"), show="headings")
    for col in ("ID","Name","Price","Stock","Category"):
        tree.heading(col, text=col)
    tree.pack(pady=10)

    cursor.execute("SELECT * FROM Product")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

    tk.Button(vf, text="Back", command=lambda:[vf.pack_forget(),menu()]).pack()

# ---------------- UPDATE PRODUCT ----------------
def update_product():
    mf.pack_forget()
    global uf
    uf = tk.Frame(root)
    uf.pack()

    tk.Label(uf, text="Product ID").pack()
    pid = tk.Entry(uf)
    pid.pack()

    tk.Label(uf, text="New Price").pack()
    price = tk.Entry(uf)
    price.pack()

    tk.Label(uf, text="New Stock").pack()
    stock = tk.Entry(uf)
    stock.pack()

    def update():
        try:
            cursor.execute("UPDATE Product SET price=%s, stock=%s WHERE product_id=%s",
                           (int(price.get()), int(stock.get()), int(pid.get())))
            db.commit()
            messagebox.showinfo("Success", "Updated Successfully")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(uf, text="Update", command=update).pack(pady=5)
    tk.Button(uf, text="Back", command=lambda:[uf.pack_forget(),menu()]).pack()

# ---------------- DELETE PRODUCT ----------------
def delete_product():
    mf.pack_forget()
    global df
    df = tk.Frame(root)
    df.pack()

    tk.Label(df, text="Product ID").pack()
    pid = tk.Entry(df)
    pid.pack()

    def delete():
        try:
            cursor.execute("DELETE FROM Product WHERE product_id=%s", (int(pid.get()),))
            db.commit()
            messagebox.showinfo("Deleted", "Product Deleted")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(df, text="Delete", command=delete).pack(pady=5)
    tk.Button(df, text="Back", command=lambda:[df.pack_forget(),menu()]).pack()

# ---------------- CREATE BILL ----------------
def create_bill():
    mf.pack_forget()
    global bf
    bf = tk.Frame(root, bg="#fefefe")
    bf.pack(fill="both", expand=True)

    tk.Label(bf, text="Customer Name").pack()
    cname = tk.Entry(bf)
    cname.pack()

    tk.Label(bf, text="Select Product").pack()

    cursor.execute("SELECT product_id,name,price,stock FROM Product")
    products = cursor.fetchall()
    product_dict = {f"{n} (₹{p})": (pid,p,s) for pid,n,p,s in products}

    selected = tk.StringVar()
    combo = ttk.Combobox(bf, textvariable=selected)
    combo['values'] = list(product_dict.keys())
    combo.pack()

    tk.Label(bf, text="Quantity").pack()
    qty = tk.Entry(bf)
    qty.pack()

    bill_area = tk.Text(bf, height=15, width=50, bg="#e6f2ff")
    bill_area.pack()

    items = []

    def add_item():
        try:
            name = selected.get()
            pid, price, stock = product_dict[name]
            q = int(qty.get())

            existing = sum(i[2] for i in items if i[0]==pid)
            if q + existing > stock:
                messagebox.showerror("Error","Stock exceeded")
                return

            sub = price*q
            items.append((pid,name,q,price,sub))
            show_bill()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_bill():
        bill_area.delete("1.0", tk.END)
        total = 0

        bill_area.insert(tk.END,"------ RECEIPT ------\n")
        bill_area.insert(tk.END,f"Date: {date.today()}\n")
        bill_area.insert(tk.END,f"Customer: {cname.get()}\n\n")

        for _,n,q,p,s in items:
            bill_area.insert(tk.END,f"{n[:10]}  {q} x {p} = {s}\n")
            total += s

        bill_area.insert(tk.END,"\nTotal: ₹"+str(total))

    def save_bill():
        try:
            total = sum(i[4] for i in items)

            cursor.execute(
                "INSERT INTO Bill(date,total_amount,customer_name) VALUES(%s,%s,%s)",
                (date.today(), total, cname.get())
            )
            bid = cursor.lastrowid

            for pid,_,q,_,s in items:
                cursor.execute(
                    "INSERT INTO Bill_Items(bill_id,product_id,quantity,subtotal) VALUES(%s,%s,%s,%s)",
                    (bid,pid,q,s)
                )
                cursor.execute(
                    "UPDATE Product SET stock=stock-%s WHERE product_id=%s",
                    (q,pid)
                )

            db.commit()
            messagebox.showinfo("Success", f"Bill Saved ID: {bid}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(bf, text="Add Item", command=add_item).pack(pady=2)
    tk.Button(bf, text="Save Bill", command=save_bill).pack(pady=2)
    tk.Button(bf, text="Back", command=lambda:[bf.pack_forget(),menu()]).pack(pady=2)

# ---------------- MAIN ----------------
root = tk.Tk()
root.title("Billing System")
root.geometry("600x600")

lf = tk.Frame(root)
lf.pack()

tk.Label(lf, text="Username").pack()
user = tk.Entry(lf)
user.pack()

tk.Label(lf, text="Password").pack()
pwd = tk.Entry(lf, show="*")
pwd.pack()

tk.Button(lf, text="Login", command=login).pack()

root.mainloop()
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="25@Viboo",
        database="billing_system"
    )
    print("✅ Connected successfully")
except Exception as e:
    print("❌ Connection failed:", e)