import tkinter as tk
from tkinter import ttk, messagebox
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime


class FinanceTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Tracker")
        self.root.geometry("800x600")

        # Initialize data structures
        self.transactions = []
        self.budget = 0

        # Set up UI components
        self.setup_ui()

    def setup_ui(self):
        # Title Label
        title_label = tk.Label(self.root, text="Personal Finance Tracker", font=("Arial", 18, "bold"), fg="Grey")
        title_label.pack(pady=10)

        # Input Frame
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Description:").grid(row=0, column=0, padx=5)
        self.desc_entry = tk.Entry(input_frame, width=20)
        self.desc_entry.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Amount:").grid(row=0, column=2, padx=5)
        self.amount_entry = tk.Entry(input_frame, width=10)
        self.amount_entry.grid(row=0, column=3, padx=5)

        tk.Label(input_frame, text="Category:").grid(row=0, column=4, padx=5)
        self.category_var = tk.StringVar(value="Select")
        self.category_menu = ttk.Combobox(
            input_frame, textvariable=self.category_var, values=["Food", "Rent", "Entertainment", "Grocery", "Others"]
        )
        self.category_menu.grid(row=0, column=5, padx=5)

        tk.Label(input_frame, text="Month:").grid(row=0, column=6, padx=5)
        self.month_var = tk.StringVar(value=datetime.now().strftime("%B"))  # Default to current month
        self.month_menu = ttk.Combobox(
            input_frame,
            textvariable=self.month_var,
            values=[
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December",
            ],
        )
        self.month_menu.grid(row=0, column=7, padx=5)

        tk.Button(input_frame, text="Add Transaction", command=self.add_transaction).grid(row=0, column=8, padx=5)

        # Transaction Table
        self.tree = ttk.Treeview(self.root, columns=("Description", "Amount", "Category", "Month"), show="headings")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Month", text="Month")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # Budget and Summary
        summary_frame = tk.Frame(self.root)
        summary_frame.pack(pady=10)
        tk.Label(summary_frame, text="Monthly Budget:").pack(side=tk.LEFT, padx=5)
        self.budget_var = tk.StringVar()
        tk.Entry(summary_frame, textvariable=self.budget_var, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(summary_frame, text="Set Budget", command=self.set_budget).pack(side=tk.LEFT, padx=5)
        tk.Button(summary_frame, text="Visualize Spending", command=self.visualize_spending).pack(side=tk.LEFT, padx=5)
        tk.Button(summary_frame, text="Download CSV", command=self.download_csv).pack(side=tk.LEFT, padx=5)

        # Visualization Area
        self.graph_area = tk.Frame(self.root)
        self.graph_area.pack(fill=tk.BOTH, expand=True)

    def add_transaction(self):
        desc = self.desc_entry.get().strip()
        amount = self.amount_entry.get().strip()

        if not desc:
            messagebox.showerror("Invalid Input", "Description cannot be empty.")
            return

        if not amount:
            messagebox.showerror("Invalid Input", "Amount cannot be empty.")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Invalid Input", "Amount must be a number.")
            return

        category = self.category_var.get()
        month = self.month_var.get()

        if not desc or not category or category == "Select" or month == "Select":
            messagebox.showerror("Invalid Input", "All fields are required.")
            return

        if sum(t["amount"] for t in self.transactions if t["month"] == month) + amount > self.budget:
            messagebox.showwarning("Budget Exceeded", "This transaction exceeds your monthly budget.")

        self.transactions.append({"description": desc, "amount": amount, "category": category, "month": month})
        self.update_table()
        self.clear_inputs()

    def update_table(self):
        # Clear the table
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Populate with updated data
        for transaction in self.transactions:
            self.tree.insert(
                "", "end", values=(transaction["description"], transaction["amount"], transaction["category"], transaction["month"])
            )

    def set_budget(self):
        try:
            self.budget = float(self.budget_var.get())
            messagebox.showinfo("Budget Set", f"Your monthly budget is set to {self.budget}.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Budget must be a number.")

    def clear_inputs(self):
        self.desc_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.category_var.set("Select")
        self.month_var.set(datetime.now().strftime("%B"))

    def download_csv(self):
        if not self.transactions:
            messagebox.showinfo("No Data", "No transactions to export.")
            return

        file_path = tk.filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save CSV File",
        )
        if not file_path:
            return

        try:
            with open(file_path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Description", "Amount", "Category", "Month"])
                for transaction in self.transactions:
                    writer.writerow([transaction["description"], transaction["amount"], transaction["category"], transaction["month"]])

            messagebox.showinfo("Success", f"Transactions exported successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save CSV: {e}")

    def visualize_spending(self):
        selected_month = self.month_var.get()

        # Filter transactions by the selected month
        month_transactions = [t for t in self.transactions if t["month"] == selected_month]

        if not month_transactions:
            messagebox.showinfo("No Data", f"No transactions found for {selected_month}.")
            return

        # Group expenses by category
        categories = {}
        total_expense = 0  # To calculate total expense
        for transaction in month_transactions:
            categories[transaction["category"]] = categories.get(transaction["category"], 0) + transaction["amount"]
            total_expense += transaction["amount"]

        # Create a pie chart
        fig, ax = plt.subplots()
        ax.pie(categories.values(), labels=categories.keys(), autopct="%1.1f%%", startangle=90)
        ax.axis("equal")  # Equal aspect ratio ensures that the pie is drawn as a circle

        # Display the pie chart in Tkinter
        for widget in self.graph_area.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_area)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()

        # Display total expense for the month
        total_label = tk.Label(self.graph_area, text=f"Total Expense for {selected_month}: {total_expense:.2f}", font=("Arial", 12, "bold"))
        total_label.pack(pady=10)



if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceTrackerApp(root)
    root.mainloop()
