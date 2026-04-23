"""
Payment Window - User payment submission interface
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime
import json
import os

# Payment configuration - UPDATE THESE
PAYMENT_INFO = {
    "airtel_number": "66562536",        # Your Airtel Uganda merchant number
    "mtn_number": "7074948",            # Your MTN Uganda merchant number
    "amount": "10000",                  # Amount in UGX
    "currency": "UGX",
    "business_name": "AT Tech Solutions Uganda",
    "payment_reason": "AriTyper License Purchase"
}

class PaymentWindow:
    """Payment submission window"""
    
    def __init__(self, parent, device_id, on_payment_submitted=None):
        self.parent = parent
        self.device_id = device_id
        self.on_payment_submitted = on_payment_submitted
        
        self.window = tk.Toplevel(parent)
        self.window.title("Purchase License - AriTyper")
        self.window.geometry("500x600")
        self.window.configure(bg='#1a1a2e')
        self.window.resizable(False, False)
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"500x600+{x}+{y}")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.window, bg='#1a1a2e')
        header_frame.pack(fill='x', padx=20, pady=20)
        
        title = tk.Label(
            header_frame,
            text="🔒 Purchase AriTyper License",
            font=("Arial", 18, "bold"),
            bg='#1a1a2e',
            fg='#ffffff'
        )
        title.pack()
        
        # Device ID display
        device_frame = tk.Frame(self.window, bg='#1a1a2e')
        device_frame.pack(fill='x', padx=20, pady=5)
        
        tk.Label(
            device_frame,
            text=f"Device ID: {self.device_id}",
            font=("Courier", 10),
            bg='#1a1a2e',
            fg='#888888'
        ).pack()
        
        # Payment instructions
        instruct_frame = tk.Frame(self.window, bg='#16213e', padx=20, pady=15)
        instruct_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            instruct_frame,
            text="📱 Payment Instructions",
            font=("Arial", 14, "bold"),
            bg='#16213e',
            fg='#ffffff'
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(
            instruct_frame,
            text=f"Amount to Pay: {PAYMENT_INFO['amount']} {PAYMENT_INFO['currency']}",
            font=("Arial", 12),
            bg='#16213e',
            fg='#00ff88'
        ).pack(anchor='w', pady=2)
        
        # Airtel Money
        airtel_frame = tk.Frame(instruct_frame, bg='#16213e')
        airtel_frame.pack(fill='x', pady=10)
        
        tk.Label(
            airtel_frame,
            text="📲 Airtel Money:",
            font=("Arial", 11, "bold"),
            bg='#16213e',
            fg='#ff6b6b'
        ).pack(anchor='w')
        
        tk.Label(
            airtel_frame,
            text=PAYMENT_INFO['airtel_number'],
            font=("Arial", 14, "bold"),
            bg='#16213e',
            fg='#ffffff'
        ).pack(anchor='w')
        
        # MTN Money
        mtn_frame = tk.Frame(instruct_frame, bg='#16213e')
        mtn_frame.pack(fill='x', pady=10)
        
        tk.Label(
            mtn_frame,
            text="📲 MTN Money:",
            font=("Arial", 11, "bold"),
            bg='#16213e',
            fg='#ffd93d'
        ).pack(anchor='w')
        
        tk.Label(
            mtn_frame,
            text=PAYMENT_INFO['mtn_number'],
            font=("Arial", 14, "bold"),
            bg='#16213e',
            fg='#ffffff'
        ).pack(anchor='w')
        
        tk.Label(
            instruct_frame,
            text="💡 Send money to either number above, then enter\nyour transaction details below.",
            font=("Arial", 10),
            bg='#16213e',
            fg='#aaaaaa'
        ).pack(anchor='w', pady=10)
        
        # Form
        form_frame = tk.Frame(self.window, bg='#1a1a2e')
        form_frame.pack(fill='x', padx=20, pady=10)
        
        # Phone number used
        tk.Label(
            form_frame,
            text="Phone Number Used (for payment):",
            font=("Arial", 11),
            bg='#1a1a2e',
            fg='#ffffff'
        ).pack(anchor='w', pady=(10, 5))
        
        self.phone_entry = tk.Entry(
            form_frame,
            font=("Arial", 12),
            bg='#16213e',
            fg='#ffffff',
            insertbackground='#ffffff'
        )
        self.phone_entry.pack(fill='x', pady=5)
        
        # Transaction ID
        tk.Label(
            form_frame,
            text="Transaction ID / Reference:",
            font=("Arial", 11),
            bg='#1a1a2e',
            fg='#ffffff'
        ).pack(anchor='w', pady=(10, 5))
        
        self.transaction_entry = tk.Entry(
            form_frame,
            font=("Arial", 12),
            bg='#16213e',
            fg='#ffffff',
            insertbackground='#ffffff'
        )
        self.transaction_entry.pack(fill='x', pady=5)
        
        # Network selection
        tk.Label(
            form_frame,
            text="Network:",
            font=("Arial", 11),
            bg='#1a1a2e',
            fg='#ffffff'
        ).pack(anchor='w', pady=(10, 5))
        
        self.network_var = tk.StringVar(value="airtel")
        
        network_frame = tk.Frame(form_frame, bg='#1a1a2e')
        network_frame.pack(fill='x')
        
        tk.Radiobutton(
            network_frame,
            text="Airtel Money",
            variable=self.network_var,
            value="airtel",
            font=("Arial", 10),
            bg='#1a1a2e',
            fg='#ffffff',
            selectcolor='#16213e'
        ).pack(side='left', padx=10)
        
        tk.Radiobutton(
            network_frame,
            text="MTN Money",
            variable=self.network_var,
            value="mtn",
            font=("Arial", 10),
            bg='#1a1a2e',
            fg='#ffffff',
            selectcolor='#16213e'
        ).pack(side='left', padx=10)
        
        # Submit button
        btn_frame = tk.Frame(self.window, bg='#1a1a2e')
        btn_frame.pack(fill='x', padx=20, pady=20)
        
        submit_btn = tk.Button(
            btn_frame,
            text="📤 Submit Payment",
            font=("Arial", 12, "bold"),
            bg='#00ff88',
            fg='#1a1a2e',
            padx=20,
            pady=10,
            command=self.submit_payment
        )
        submit_btn.pack(fill='x')
        
        # Status label
        self.status_label = tk.Label(
            self.window,
            text="",
            font=("Arial", 10),
            bg='#1a1a2e',
            fg='#ff6b6b'
        )
        self.status_label.pack(pady=10)
        
    def validate_uganda_phone(self, phone: str) -> bool:
        """Validate Uganda phone number format"""
        phone = phone.replace(' ', '').replace('-', '').replace('+', '')
        
        # Uganda phone numbers:
        # Mobile: 07/075/077/078/079 (10 digits starting with 07)
        # Landline: 031/032/033/034/039 (9 digits starting with 03)
        # International format: +256XXXXXXXXX (12 digits starting with 256)
        
        if len(phone) == 9 and phone.startswith('03'):
            # Landline numbers: 031, 032, 033, 034, 039
            return phone[2:4] in ['31', '32', '33', '34', '39']
        elif len(phone) == 10 and phone.startswith('07'):
            # Mobile numbers: 075, 077, 078, 079
            return phone[1:3] in ['75', '77', '78', '79']
        elif len(phone) == 12 and phone.startswith('256'):
            # International format
            return True
        return False
    
    def submit_payment(self):
        """Submit payment for approval"""
        phone = self.phone_entry.get().strip()
        transaction_id = self.transaction_entry.get().strip()
        network = self.network_var.get()
        
        # Validation
        if not phone:
            messagebox.showerror("Error", "Please enter your phone number")
            return
            
        if not transaction_id:
            messagebox.showerror("Error", "Please enter transaction ID")
            return
        
        if not self.validate_uganda_phone(phone):
            messagebox.showerror(
                "Error", 
                "Please enter a valid Uganda phone number\n"
                "Format: 07XXXXXXXX, 03XXXXXXXX, or +256XXXXXXXX"
            )
            return
        
        if len(transaction_id) < 4:
            messagebox.showerror("Error", "Transaction ID is too short")
            return
        
        # Save payment request
        payment_request = {
            "device_id": self.device_id,
            "phone_number": phone,
            "transaction_id": transaction_id,
            "network": network,
            "amount": PAYMENT_INFO['amount'],
            "submitted_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        # Save to pending payments
        try:
            pending_file = "pending_payments.json"
            pending = []
            if os.path.exists(pending_file):
                with open(pending_file, 'r') as f:
                    pending = json.load(f)
            
            pending.append(payment_request)
            
            with open(pending_file, 'w') as f:
                json.dump(pending, f, indent=2)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
            return
        
        # Show success message
        self.status_label.config(
            text="✅ Payment submitted! Wait for approval.\nYou will be notified once approved.",
            fg='#00ff88'
        )
        
        messagebox.showinfo(
            "Payment Submitted",
            f"Your payment has been submitted for review.\n\n"
            f"Phone: {phone}\n"
            f"Transaction: {transaction_id}\n\n"
            f"You will receive your license key once approved.\n"
            f"This usually takes a few minutes."
        )
        
        # Close window
        self.window.destroy()
        
        # Callback
        if self.on_payment_submitted:
            self.on_payment_submitted()


class PaymentRequestDB:
    """Database for pending payment requests (for admin)"""
    
    def __init__(self, file_path: str = "pending_payments.json"):
        self.file_path = file_path
        
    def load(self) -> list:
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save(self, payments: list):
        with open(self.file_path, 'w') as f:
            json.dump(payments, f, indent=2)
    
    def add(self, payment: dict):
        payments = self.load()
        payments.append(payment)
        self.save(payments)
    
    def remove(self, transaction_id: str):
        payments = self.load()
        payments = [p for p in payments if p.get('transaction_id') != transaction_id]
        self.save(payments)
    
    def get_all(self) -> list:
        return self.load()


if __name__ == "__main__":
    # Test
    root = tk.Tk()
    root.withdraw()
    
    pw = PaymentWindow(root, "ARI-TEST123456")
    
    root.mainloop()