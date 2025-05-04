
import tkinter as tk
from tkinter import messagebox
import pyodbc
import datetime


# Database Setup
def connect_to_db():
    # Connect to SQL Server. 
    try:
        conn = pyodbc.connect(
            'Driver={ODBC Driver 17 for SQL Server};'
            'Server=Lumine\SQLEXPRESS,1433;'
            'Database=ParkingLot;'  
            'UID=Demo_User;'
            'PWD=demo!123'  
        )
        return conn
    except Exception as e:
        messagebox.showerror("Database Error", f"Could not connect to the database.\n{e}")
        return None

# Get the current car count from the Car table
def fetch_car_count(conn):
    if not conn:
        return 0
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Car")
    count = cursor.fetchone()
    return count[0] if count else 0

# Get the current cycle count from the Cycle table
def fetch_cycle_count(conn):
    if not conn:
        return 0
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Cycle")
    count = cursor.fetchone()
    return count[0] if count else 0

# Insert values for the Car table in the program
def insert_car(conn, make, model, color):
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Car (Make, Model, Color) VALUES (?, ?, ?)", (make, model, color))
    conn.commit()

# Insert values for the Cycle table in the program
def insert_cycle(conn, make, model, color):
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Cycle (Make, Model, Color) VALUES (?, ?, ?)", (make, model, color))
    conn.commit()
 
# Insert values for a new fine into the Fines table 
def insert_fine_record(conn, make, model, amount):
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Fines (Make, Model, FineAmount) VALUES (?, ?, ?)",
        (make, model, amount)
    )
    conn.commit()

# Main Application Class
class ParkingLotSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Parking Lot System")
        self.attributes("-fullscreen", True)  # Launch in full-screen
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))  # Press Esc to exit full-screen

        # Database connection
        self.conn = connect_to_db()

        # Maximum spots
        self.max_car_spots = 1000
        self.max_cycle_spots = 200

        # Payment mode flag: "purchase" or "gate"
        self.payment_mode = "purchase"

        # Spot simulation flag
        self.no_spots_mode = False

        # Container for frames
        container = tk.Frame(self, bg="white")
        container.pack(side="top", fill="both", expand=True)

        self.frames = {}
        for F in (MainMenuFrame,
                  VehicleTypeFrame,
                  CarInfoFrame,
                  PaymentMethodFrame,
                  CardPaymentFrame,
                  CashPaymentFrame,
                  PinEntryFrame,
                  NoSpotsFrame,
                  SecurityDashboardFrame):
            frame_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[frame_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show main menu at startup
        self.show_frame("MainMenuFrame")

        # Time/date label in top-right
        self.time_label = tk.Label(self, text="", font=("Helvetica", 12), bg="white")
        self.time_label.pack(side="top", anchor="ne", padx=10, pady=5)
        self.update_time_label()

    def update_time_label(self):
        now = datetime.datetime.now()
        date_str = now.strftime("Date: %m/%d/%y  Time: %I:%M %p")
        self.time_label.config(text=date_str)
        self.after(1000, self.update_time_label)

    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        if frame_name == "VehicleTypeFrame":
            frame.update_availability_labels()
        frame.tkraise()

    def simulate_no_spots(self):
        self.no_spots_mode = not self.no_spots_mode
        if self.no_spots_mode:
            messagebox.showinfo("No Spots Mode", "Now simulating no spots available.")
        else:
            messagebox.showinfo("No Spots Mode", "Spots simulation reset to normal.")

    def get_car_spots_available(self):
        if self.no_spots_mode:
            return 0
        current = fetch_car_count(self.conn)
        return self.max_car_spots - current

    def get_cycle_spots_available(self):
        if self.no_spots_mode:
            return 0
        current = fetch_cycle_count(self.conn)
        return self.max_cycle_spots - current

# Main Menu
class MainMenuFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller

        title = tk.Label(self, text="Welcome!", font=("Helvetica", 36, "bold"), bg="white")
        title.pack(pady=40)

        btn_style = {"font": ("Helvetica", 24), "width": 20, "bg": "#4CAF50", "fg": "white", "bd": 3, "relief": "raised"}

        purchase_button = tk.Button(self, text="Purchase a Ticket", **btn_style,
                                    command=self.purchase_ticket)
        purchase_button.pack(pady=10)

        gate_button = tk.Button(self, text="Pay at Gate", **btn_style,
                                command=self.pay_at_gate)
        gate_button.pack(pady=10)

        pin_button = tk.Button(self, text="Enter a PIN Number", **btn_style,
                               command=lambda: controller.show_frame("PinEntryFrame"))
        pin_button.pack(pady=10)

        avail_button = tk.Button(self, text="Check Availability", **btn_style,
                                 command=self.check_availability)
        avail_button.pack(pady=10)

        simulate_button = tk.Button(self, text="Toggle No-Spots Simulation", **btn_style,
                                    command=controller.simulate_no_spots)
        simulate_button.pack(pady=10)
        
        security_button = tk.Button(
            self,
            text="Security Dashboard",
            font=("Helvetica", 24),
            width=20,
            bg="#795548",
            fg="white",
            bd=3,
            relief="raised",
            command=lambda: controller.show_frame("SecurityDashboardFrame")
        )
        security_button.pack(pady=10)

    def purchase_ticket(self):
        self.controller.payment_mode = "purchase"
        self.controller.show_frame("VehicleTypeFrame")

    def pay_at_gate(self):
        self.controller.payment_mode = "gate"
        self.controller.show_frame("VehicleTypeFrame")

    def check_availability(self):
        car = self.controller.get_car_spots_available()
        cycle = self.controller.get_cycle_spots_available()
        messagebox.showinfo("Availability", f"Car Spots Available: {car}\nCycle Spots Available: {cycle}")

# Vehicle Type Selection
class VehicleTypeFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller

        label = tk.Label(self, text="Select Your Vehicle Type", font=("Helvetica", 32, "bold"), bg="white")
        label.pack(pady=40)

        btn_style = {"font": ("Helvetica", 24), "width": 25, "bd": 3, "relief": "raised"}

        self.car_button = tk.Button(self, text="Sedan, SUV, Van", **btn_style,
                                    command=self.handle_car_selection, bg="#2196F3", fg="white")
        self.car_button.pack(pady=10)

        self.cycle_button = tk.Button(self, text="Motorcycle, Bicycle", **btn_style,
                                      command=self.handle_cycle_selection, bg="#9C27B0", fg="white")
        self.cycle_button.pack(pady=10)

        emergency_button = tk.Button(self, text="Emergency Vehicle", **btn_style,
                                     command=self.handle_emergency, bg="#f44336", fg="white")
        emergency_button.pack(pady=10)

        back_button = tk.Button(self, text="Back to Menu", **btn_style,
                                command=lambda: controller.show_frame("MainMenuFrame"))
        back_button.pack(pady=10)

    def update_availability_labels(self):
        car_spots = self.controller.get_car_spots_available()
        cycle_spots = self.controller.get_cycle_spots_available()
        self.car_button.config(text=f"Sedan, SUV, Van\n{car_spots} spots available")
        self.cycle_button.config(text=f"Motorcycle, Bicycle\n{cycle_spots} spots available")

    def handle_car_selection(self):
        if self.controller.get_car_spots_available() <= 0:
            self.controller.show_frame("NoSpotsFrame")
        else:
            self.controller.frames["CarInfoFrame"].vehicle_type = "Car"
            self.controller.show_frame("CarInfoFrame")

    def handle_cycle_selection(self):
        if self.controller.get_cycle_spots_available() <= 0:
            self.controller.show_frame("NoSpotsFrame")
        else:
            self.controller.frames["CarInfoFrame"].vehicle_type = "Cycle"
            self.controller.show_frame("CarInfoFrame")

    def handle_emergency(self):
        messagebox.showinfo("Emergency Vehicle", "Please proceed to the emergency location.")

# Enter Vehicle Details
class CarInfoFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        self.vehicle_type = None  # "Car" or "Cycle"

        label = tk.Label(self, text="Enter Vehicle Details", font=("Helvetica", 32, "bold"), bg="white")
        label.pack(pady=40)

        field_style = {"font": ("Helvetica", 24), "bg": "white"}
        entry_style = {"font": ("Helvetica", 24)}

        tk.Label(self, text="Make:", **field_style).pack(pady=5)
        self.make_entry = tk.Entry(self, **entry_style)
        self.make_entry.pack(pady=5)

        tk.Label(self, text="Model:", **field_style).pack(pady=5)
        self.model_entry = tk.Entry(self, **entry_style)
        self.model_entry.pack(pady=5)

        tk.Label(self, text="Color:", **field_style).pack(pady=5)
        self.color_entry = tk.Entry(self, **entry_style)
        self.color_entry.pack(pady=5)

        btn_style = {"font": ("Helvetica", 24), "width": 15, "bd": 3, "relief": "raised", "bg": "#009688", "fg": "white"}
        next_button = tk.Button(self, text="Next", **btn_style, command=self.submit_info)
        next_button.pack(pady=20)

        back_button = tk.Button(self, text="Back", **btn_style,
                                command=lambda: controller.show_frame("VehicleTypeFrame"))
        back_button.pack(pady=10)

    def submit_info(self):
        make = self.make_entry.get().strip()
        model = self.model_entry.get().strip()
        color = self.color_entry.get().strip()

        if not make or not model or not color:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        # Insert into DB and update counts
        if self.vehicle_type == "Car":
            insert_car(self.controller.conn, make, model, color)
        else:
            insert_cycle(self.controller.conn, make, model, color)

        # Clear entries for next time
        self.make_entry.delete(0, tk.END)
        self.model_entry.delete(0, tk.END)
        self.color_entry.delete(0, tk.END)

        # If "Pay at Gate", skip payment selection and print ticket immediately.
        if self.controller.payment_mode == "gate":
            messagebox.showinfo("Ticket", "Printing ticket...")
            self.controller.show_frame("MainMenuFrame")
        else:
            self.controller.show_frame("PaymentMethodFrame")

# Payment Method Selection
class PaymentMethodFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller

        label = tk.Label(self, text="Select Payment Method", font=("Helvetica", 32, "bold"), bg="white")
        label.pack(pady=40)

        btn_style = {"font": ("Helvetica", 24), "width": 20, "bd": 3, "relief": "raised"}

        card_button = tk.Button(self, text="Pay via Card", **btn_style,
                                bg="#3F51B5", fg="white",
                                command=lambda: controller.show_frame("CardPaymentFrame"))
        card_button.pack(pady=10)

        cash_button = tk.Button(self, text="Pay via Cash", **btn_style,
                                bg="#FF9800", fg="white",
                                command=lambda: controller.show_frame("CashPaymentFrame"))
        cash_button.pack(pady=10)

        back_button = tk.Button(self, text="Back", **btn_style,
                                bg="#9E9E9E", fg="white",
                                command=lambda: controller.show_frame("CarInfoFrame"))
        back_button.pack(pady=10)

# Card Payment (Processing then Success)
class CardPaymentFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller

        self.label = tk.Label(self, text="Please insert your card and press 'Process Payment'", 
                              font=("Helvetica", 28), bg="white")
        self.label.pack(pady=40)

        process_btn_style = {"font": ("Helvetica", 24), "width": 20, "bd": 3, "relief": "raised", "bg": "#673AB7", "fg": "white"}
        self.process_button = tk.Button(self, text="Process Payment", **process_btn_style,
                                        command=self.process_payment)
        self.process_button.pack(pady=20)

        back_btn_style = {"font": ("Helvetica", 24), "width": 20, "bd": 3, "relief": "raised", "bg": "#9E9E9E", "fg": "white"}
        back_button = tk.Button(self, text="Back", **back_btn_style,
                                command=lambda: controller.show_frame("PaymentMethodFrame"))
        back_button.pack(pady=10)

    def process_payment(self):
        # Disable the button to prevent multiple clicks.
        self.process_button.config(state="disabled")
        self.label.config(text="Processing payment...\nPlease do not remove your card...")
        # After 3 seconds, show payment success options.
        self.after(3000, self.show_payment_success)

    def show_payment_success(self):
        # Clear current widgets
        for widget in self.winfo_children():
            widget.destroy()

        success_label = tk.Label(self, text="Payment Successful!\nWould you like a receipt?", 
                                 font=("Helvetica", 28), bg="white")
        success_label.pack(pady=40)

        btn_style = {"font": ("Helvetica", 24), "width": 15, "bd": 3, "relief": "raised"}
        yes_button = tk.Button(self, text="YES", **btn_style,
                               bg="#4CAF50", fg="white", command=self.print_receipt)
        yes_button.pack(side="left", padx=40, pady=20)

        no_button = tk.Button(self, text="NO", **btn_style,
                              bg="#F44336", fg="white", command=self.no_receipt)
        no_button.pack(side="left", padx=40, pady=20)

    def print_receipt(self):
        # Changed message to include both receipt and ticket printing.
        messagebox.showinfo("Payment", "Printing receipt and ticket...")
        self.controller.show_frame("MainMenuFrame")

    def no_receipt(self):
        messagebox.showinfo("Payment", "Printing ticket...")
        self.controller.show_frame("MainMenuFrame")

# Cash Payment
class CashPaymentFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller

        label = tk.Label(self, text="Insert Cash Amount (Fee is $15)", font=("Helvetica", 28), bg="white")
        label.pack(pady=40)

        self.cash_entry = tk.Entry(self, font=("Helvetica", 28))
        self.cash_entry.pack(pady=10)

        btn_style = {"font": ("Helvetica", 24), "width": 20, "bd": 3, "relief": "raised"}

        pay_button = tk.Button(self, text="Pay", **btn_style,
                               bg="#FF9800", fg="white", command=self.process_cash)
        pay_button.pack(pady=20)

        back_button = tk.Button(self, text="Back", **btn_style,
                                bg="#9E9E9E", fg="white",
                                command=lambda: controller.show_frame("PaymentMethodFrame"))
        back_button.pack(pady=10)

    def process_cash(self):
        try:
            amount = float(self.cash_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid amount.")
            return

        if amount < 15:
            messagebox.showwarning("Insufficient", "Please insert at least $15")
            return

        change = amount - 15
        if change > 0:
            messagebox.showinfo("Change", f"Dispensing ${change:.2f} back.")
        self.show_processing()

    def show_processing(self):
        for widget in self.winfo_children():
            widget.destroy()
        label = tk.Label(self, text="Processing cash payment...\nPlease wait...", 
                         font=("Helvetica", 28), bg="white")
        label.pack(pady=40)
        self.after(3000, self.show_success)

    def show_success(self):
        for widget in self.winfo_children():
            widget.destroy()
        success_label = tk.Label(self, text="Payment Successful!\nWould you like a receipt?", 
                                 font=("Helvetica", 28), bg="white")
        success_label.pack(pady=40)
        btn_style = {"font": ("Helvetica", 24), "width": 15, "bd": 3, "relief": "raised"}
        yes_button = tk.Button(self, text="YES", **btn_style,
                               bg="#4CAF50", fg="white", command=self.print_receipt)
        yes_button.pack(side="left", padx=40, pady=20)
        no_button = tk.Button(self, text="NO", **btn_style,
                              bg="#F44336", fg="white", command=self.no_receipt)
        no_button.pack(side="left", padx=40, pady=20)

    def print_receipt(self):
        messagebox.showinfo("Payment", "Printing receipt and ticket...")
        self.controller.show_frame("MainMenuFrame")

    def no_receipt(self):
        messagebox.showinfo("Payment", "Printing ticket...")
        self.controller.show_frame("MainMenuFrame")

# PIN Entry
class PinEntryFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller

        label = tk.Label(self, text="Enter Your PIN", font=("Helvetica", 32, "bold"), bg="white")
        label.pack(pady=40)

        self.pin_entry = tk.Entry(self, font=("Helvetica", 28), show="*")
        self.pin_entry.pack(pady=20)

        base_btn_style = {"font": ("Helvetica", 24), "width": 15, "bd": 3, "relief": "raised"}
        next_button = tk.Button(self, text="Next", **base_btn_style, bg="#009688", fg="white",
                                command=self.submit_pin)
        next_button.pack(pady=20)

        back_button = tk.Button(self, text="Back", **base_btn_style, bg="#9E9E9E", fg="white",
                                command=lambda: controller.show_frame("MainMenuFrame"))
        back_button.pack(pady=10)

    def submit_pin(self):
        pin = self.pin_entry.get().strip()
        if not pin:
            messagebox.showwarning("PIN Error", "Please enter a PIN.")
            return
        messagebox.showinfo("PIN", "PIN accepted.\nPrinting ticket...")
        self.pin_entry.delete(0, tk.END)
        self.controller.show_frame("MainMenuFrame")

# No Spots Available
class NoSpotsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        label = tk.Label(self, text="Currently there are no spots available\n"
                                    "Estimated wait time: 30 Minutes\n"
                                    "We apologize for the inconvenience", 
                          font=("Helvetica", 28), bg="white", fg="red")
        label.pack(pady=60)
        btn_style = {"font": ("Helvetica", 24), "width": 20, "bd": 3, "relief": "raised", "bg": "#9E9E9E", "fg": "white"}
        back_button = tk.Button(self, text="Back to Menu", **btn_style,
                                command=lambda: controller.show_frame("MainMenuFrame"))
        back_button.pack(pady=20)
    
# Main Security Dashboard
class SecurityDashboardFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller

        tk.Label(
            self,
            text="Security Dashboard",
            font=("Helvetica", 32, "bold"),
            bg="white"
        ).pack(pady=20)

        # Car's Make
        tk.Label(
            self,
            text="Vehicle Make:",
            font=("Helvetica", 24),
            bg="white"
        ).pack(pady=(10,0))
        self.make_entry = tk.Entry(self, font=("Helvetica", 24))
        self.make_entry.pack(pady=(0,10))

        # Car's Model
        tk.Label(
            self,
            text="Vehicle Model:",
            font=("Helvetica", 24),
            bg="white"
        ).pack(pady=(10,0))
        self.model_entry = tk.Entry(self, font=("Helvetica", 24))
        self.model_entry.pack(pady=(0,10))

        # Fine Amount
        tk.Label(
            self,
            text="Fine Amount ($):",
            font=("Helvetica", 24),
            bg="white"
        ).pack(pady=(10,0))
        self.amount_entry = tk.Entry(self, font=("Helvetica", 24))
        self.amount_entry.pack(pady=(0,20))

        # Issue Fine & Back Buttons
        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(pady=10)

        issue_btn = tk.Button(
            btn_frame,
            text="Issue Fine",
            font=("Helvetica", 24),
            width=15,
            bg="#E91E63",
            fg="white",
            bd=3,
            relief="raised",
            command=self.issue_fine
        )
        issue_btn.grid(row=0, column=0, padx=20)

        back_btn = tk.Button(
            btn_frame,
            text="Back to Menu",
            font=("Helvetica", 24),
            width=15,
            bg="#9E9E9E",
            fg="white",
            bd=3,
            relief="raised",
            command=lambda: controller.show_frame("MainMenuFrame")
        )
        back_btn.grid(row=0, column=1, padx=20)

    def issue_fine(self):
        make = self.make_entry.get().strip()
        model = self.model_entry.get().strip()
        amt_text = self.amount_entry.get().strip()

        if not make or not model or not amt_text:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        try:
            amount = float(amt_text)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid fine amount.")
            return

        # Insert into the Fines table
        insert_fine_record(self.controller.conn, make, model, amount)

        # Print the fine ticket
        messagebox.showinfo(
            "Fine Issued",
            f"Fine of ${amount:.2f} issued for {make} {model}.\nPrinting fine ticket..."
        )

        # Clear entries
        self.make_entry.delete(0, tk.END)
        self.model_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)

# Main Entry Point
if __name__ == "__main__":
    app = ParkingLotSystem()
    app.mainloop()
