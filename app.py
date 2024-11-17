import tkinter as tk
from tkinter import ttk, messagebox
import csv
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

class FinanceTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Tracker")
        self.root.geometry("900x700")

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

        tk.Label(input_frame, text="Date:").grid(row=0, column=6, padx=5)
        self.date_picker = DateEntry(input_frame, date_pattern="yyyy-mm-dd")
        self.date_picker.grid(row=0, column=7, padx=5)

        tk.Button(input_frame, text="Add Transaction", command=self.add_transaction).grid(row=0, column=8, padx=5)

        # Transaction Table
        self.tree = ttk.Treeview(self.root, columns=("Description", "Amount", "Category", "Date"), show="headings")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Date", text="Date")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # Budget and Summary
        summary_frame = tk.Frame(self.root)
        summary_frame.pack(pady=10)
        tk.Label(summary_frame, text="Monthly Budget:").pack(side=tk.LEFT, padx=5)
        self.budget_var = tk.StringVar()
        tk.Entry(summary_frame, textvariable=self.budget_var, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(summary_frame, text="Set Budget", command=self.set_budget).pack(side=tk.LEFT, padx=5)
        tk.Button(summary_frame, text="Visualize Spending", command=self.visualize_spending).pack(side=tk.LEFT, padx=5)
        tk.Button(summary_frame, text="Visualize Monthly Expenses", command=self.visualize_monthly_expenses).pack(side=tk.LEFT, padx=5)
        tk.Button(summary_frame, text="Download CSV", command=self.download_csv).pack(side=tk.LEFT, padx=5)

        # Visualization Area
        self.graph_area = tk.Frame(self.root)
        self.graph_area.pack(fill=tk.BOTH, expand=True)

    def add_transaction(self):
        if self.budget == 0:
            messagebox.showerror("Budget Not Set", "Please set your monthly budget before adding transactions.")
            return

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
        date = self.date_picker.get_date()

        if not desc or not category or category == "Select":
            messagebox.showerror("Invalid Input", "All fields are required.")
            return

        if sum(t["amount"] for t in self.transactions if t["date"].month == date.month) + amount > self.budget:
            messagebox.showwarning("Budget Exceeded", "This transaction exceeds your monthly budget.")

        self.transactions.append({"description": desc, "amount": amount, "category": category, "date": date})
        self.update_table()
        self.clear_inputs()

    def update_table(self):
        # Clear the table
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Populate with updated data
        for transaction in self.transactions:
            self.tree.insert(
                "", "end", values=(transaction["description"], transaction["amount"], transaction["category"], transaction["date"].strftime("%d-%m-%Y"))
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
        self.date_picker.set_date(datetime.now())

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
                writer.writerow(["Description", "Amount", "Category", "Date"])
                for transaction in self.transactions:
                    writer.writerow([transaction["description"], transaction["amount"], transaction["category"], transaction["date"].strftime("%d-%m-%Y")])

            messagebox.showinfo("Success", f"Transactions exported successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save CSV: {e}")

    def visualize_spending(self):
        # Same code for daily spending visualization
        pass

    def visualize_monthly_expenses(self):
    # Group transactions by month and category
        monthly_expenses = {}
        for transaction in self.transactions:
            month = transaction["date"].strftime("%B")
            category = transaction["category"]
            monthly_expenses.setdefault(month, {}).setdefault(category, 0)
            monthly_expenses[month][category] += transaction["amount"]

        # Prepare data for bar chart
        months = list(monthly_expenses.keys())
        categories = set(cat for data in monthly_expenses.values() for cat in data.keys())

        data = {cat: [monthly_expenses.get(month, {}).get(cat, 0) for month in months] for cat in categories}

        # Determine the maximum expense amount for color scaling
        max_expense = max(sum(values) for values in data.values())
        cmap = get_cmap("coolwarm")  # Use a color map for the gradient
        norm = Normalize(vmin=0, vmax=max_expense)

        # Plot the data with colors based on values
        fig, ax = plt.subplots(figsize=(10, 6))
        bar_positions = range(len(months))
        bar_width = 0.8 / len(categories)  # Adjust width to avoid overlap

        for idx, (category, values) in enumerate(data.items()):
            bar_colors = [cmap(norm(value)) for value in values]
            ax.bar(
                [pos + idx * bar_width for pos in bar_positions],
                values,
                bar_width,
                color=bar_colors,
                label=category,
                edgecolor="black",
            )

        # Add legend, labels, and title
        ax.set_title("Monthly Expenses by Category")
        ax.set_xticks([pos + bar_width * (len(categories) / 2) for pos in bar_positions])
        ax.set_xticklabels(months)
        ax.set_xlabel("Month")
        ax.set_ylabel("Amount")
        ax.legend()

        # Add color bar for scale reference
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        plt.colorbar(sm, ax=ax, label="Expense Amount")

        # Display the bar chart in Tkinter
        for widget in self.graph_area.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_area)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceTrackerApp(root)
    root.mainloop()
