"""
Admin Panel - User management dashboard for license approval/cancellation
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime
from license_manager import LicenseManager, AdminLicenseManager

class AdminPanel:
    """Admin panel for managing user licenses"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.admin_mgr = AdminLicenseManager()
        self.license_mgr = LicenseManager()
        
        # Create main window
        if parent:
            self.window = tk.Toplevel(parent)
        else:
            self.window = tk.Tk()
            
        self.window.title("AriTyper Admin Panel")
        self.window.geometry("900x650")
        self.window.configure(bg='#1a1a2e')
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.window.winfo_screenheight() // 2) - (650 // 2)
        self.window.geometry(f"900x650+{x}+{y}")
        
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.window, bg='#1a1a2e')
        header_frame.pack(fill='x', padx=20, pady=15)
        
        title = tk.Label(
            header_frame,
            text="⚙️ AriTyper Admin Panel",
            font=("Arial", 20, "bold"),
            bg='#1a1a2e',
            fg='#ffffff'
        )
        title.pack(side='left')
        
        # Refresh button
        refresh_btn = tk.Button(
            header_frame,
            text="🔄 Refresh",
            font=("Arial", 10),
            bg='#16213e',
            fg='#ffffff',
            padx=15,
            pady=5,
            command=self.refresh_data
        )
        refresh_btn.pack(side='right')
        
        # Main content - Notebook (tabs)
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Tab 1: Pending Payments
        self.tab_pending = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(self.tab_pending, text="📥 Pending Payments")
        self.setup_pending_tab()
        
        # Tab 2: Active Licenses
        self.tab_licenses = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(self.tab_licenses, text="✅ Active Licenses")
        self.setup_licenses_tab()
        
        # Tab 3: Generate License
        self.tab_generate = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(self.tab_generate, text="🔑 Generate License")
        self.setup_generate_tab()
        
        # Tab 4: Settings
        self.tab_settings = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(self.tab_settings, text="⚙️ Settings")
        self.setup_settings_tab()
        
    def setup_pending_tab(self):
        """Pending payments tab"""
        # Info label
        info = tk.Label(
            self.tab_pending,
            text="Review pending payment requests and approve them",
            font=("Arial", 10),
            bg='#1a1a2e',
            fg='#888888'
        )
        info.pack(anchor='w', padx=20, pady=10)
        
        # Treeview frame
        tree_frame = tk.Frame(self.tab_pending, bg='#1a1a2e')
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Treeview
        columns = ('phone', 'transaction', 'device_id', 'network', 'amount', 'date')
        self.pending_tree = ttk.Treeview(
            tree_frame, 
            columns=columns, 
            show='headings',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.pending_tree.yview)
        
        # Columns
        self.pending_tree.heading('phone', text='Phone Number')
        self.pending_tree.heading('transaction', text='Transaction ID')
        self.pending_tree.heading('device_id', text='Device ID')
        self.pending_tree.heading('network', text='Network')
        self.pending_tree.heading('amount', text='Amount')
        self.pending_tree.heading('date', text='Submitted')
        
        self.pending_tree.column('phone', width=120)
        self.pending_tree.column('transaction', width=150)
        self.pending_tree.column('device_id', width=130)
        self.pending_tree.column('network', width=80)
        self.pending_tree.column('amount', width=80)
        self.pending_tree.column('date', width=150)
        
        self.pending_tree.pack(fill='both', expand=True)
        
        # Buttons
        btn_frame = tk.Frame(self.tab_pending, bg='#1a1a2e')
        btn_frame.pack(fill='x', padx=20, pady=15)
        
        approve_btn = tk.Button(
            btn_frame,
            text="✅ Approve Selected",
            font=("Arial", 11, "bold"),
            bg='#00ff88',
            fg='#1a1a2e',
            padx=20,
            pady=8,
            command=self.approve_selected
        )
        approve_btn.pack(side='left', padx=5)
        
        reject_btn = tk.Button(
            btn_frame,
            text="❌ Reject Selected",
            font=("Arial", 11),
            bg='#ff6b6b',
            fg='#ffffff',
            padx=20,
            pady=8,
            command=self.reject_selected
        )
        reject_btn.pack(side='left', padx=5)
        
    def setup_licenses_tab(self):
        """Active licenses tab"""
        # Info label
        info = tk.Label(
            self.tab_licenses,
            text="View and manage active subscriptions",
            font=("Arial", 10),
            bg='#1a1a2e',
            fg='#888888'
        )
        info.pack(anchor='w', padx=20, pady=10)
        
        # Treeview frame
        tree_frame = tk.Frame(self.tab_licenses, bg='#1a1a2e')
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Treeview
        columns = ('license_key', 'device_id', 'phone', 'plan', 'expires', 'status')
        self.licenses_tree = ttk.Treeview(
            tree_frame, 
            columns=columns, 
            show='headings',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.licenses_tree.yview)
        
        # Columns
        self.licenses_tree.heading('license_key', text='License Key')
        self.licenses_tree.heading('device_id', text='Device ID')
        self.licenses_tree.heading('phone', text='Phone')
        self.licenses_tree.heading('plan', text='Plan')
        self.licenses_tree.heading('expires', text='Expires')
        self.licenses_tree.heading('status', text='Status')
        
        self.licenses_tree.column('license_key', width=140)
        self.licenses_tree.column('device_id', width=130)
        self.licenses_tree.column('phone', width=100)
        self.licenses_tree.column('plan', width=80)
        self.licenses_tree.column('expires', width=120)
        self.licenses_tree.column('status', width=80)
        
        self.licenses_tree.pack(fill='both', expand=True)
        
        # Buttons
        btn_frame = tk.Frame(self.tab_licenses, bg='#1a1a2e')
        btn_frame.pack(fill='x', padx=20, pady=15)
        
        cancel_btn = tk.Button(
            btn_frame,
            text="🚫 Cancel Subscription",
            font=("Arial", 11),
            bg='#ff6b6b',
            fg='#ffffff',
            padx=20,
            pady=8,
            command=self.cancel_subscription
        )
        cancel_btn.pack(side='left', padx=5)
        
        extend_btn = tk.Button(
            btn_frame,
            text="⏰ Extend License",
            font=("Arial", 11),
            bg='#ffd93d',
            fg='#1a1a2e',
            padx=20,
            pady=8,
            command=self.extend_license
        )
        extend_btn.pack(side='left', padx=5)
        
    def setup_generate_tab(self):
        """Generate license tab"""
        # Form frame
        form_frame = tk.Frame(self.tab_generate, bg='#1a1a2e')
        form_frame.pack(fill='x', padx=30, pady=20)
        
        # Plan selection
        tk.Label(
            form_frame,
            text="Subscription Plan:",
            font=("Arial", 12),
            bg='#1a1a2e',
            fg='#ffffff'
        ).pack(anchor='w', pady=(10, 5))
        
        self.plan_var = tk.StringVar(value="monthly")
        
        plan_frame = tk.Frame(form_frame, bg='#1a1a2e')
        plan_frame.pack(anchor='w', pady=5)
        
        tk.Radiobutton(
            plan_frame,
            text="Monthly (30 days)",
            variable=self.plan_var,
            value="monthly",
            font=("Arial", 10),
            bg='#1a1a2e',
            fg='#ffffff',
            selectcolor='#16213e'
        ).pack(side='left', padx=10)
        
        tk.Radiobutton(
            plan_frame,
            text="3 Months",
            variable=self.plan_var,
            value="3months",
            font=("Arial", 10),
            bg='#1a1a2e',
            fg='#ffffff',
            selectcolor='#16213e'
        ).pack(side='left', padx=10)
        
        tk.Radiobutton(
            plan_frame,
            text="6 Months",
            variable=self.plan_var,
            value="6months",
            font=("Arial", 10),
            bg='#1a1a2e',
            fg='#ffffff',
            selectcolor='#16213e'
        ).pack(side='left', padx=10)
        
        tk.Radiobutton(
            plan_frame,
            text="1 Year",
            variable=self.plan_var,
            value="yearly",
            font=("Arial", 10),
            bg='#1a1a2e',
            fg='#ffffff',
            selectcolor='#16213e'
        ).pack(side='left', padx=10)
        
        # Generate button
        generate_btn = tk.Button(
            form_frame,
            text="🔑 Generate License Key",
            font=("Arial", 12, "bold"),
            bg='#00ff88',
            fg='#1a1a2e',
            padx=20,
            pady=10,
            command=self.generate_license
        )
        generate_btn.pack(anchor='w', pady=20)
        
        # Generated key display
        self.generated_key_label = tk.Label(
            form_frame,
            text="",
            font=("Courier", 14, "bold"),
            bg='#16213e',
            fg='#00ff88',
            padx=10,
            pady=10
        )
        self.generated_key_label.pack(anchor='w', pady=10)
        
        # Copy button
        self.copy_btn = tk.Button(
            form_frame,
            text="📋 Copy to Clipboard",
            font=("Arial", 10),
            bg='#16213e',
            fg='#ffffff',
            padx=15,
            pady=5,
            command=self.copy_key,
            state='disabled'
        )
        self.copy_btn.pack(anchor='w')
        
        # Info
        tk.Label(
            form_frame,
            text="💡 Generated keys are automatically approved and ready to use.",
            font=("Arial", 10),
            bg='#1a1a2e',
            fg='#888888'
        ).pack(anchor='w', pady=20)
        
    def setup_settings_tab(self):
        """Settings tab"""
        # Payment config
        config_frame = tk.LabelFrame(
            self.tab_settings,
            text="💳 Payment Configuration",
            font=("Arial", 12, "bold"),
            bg='#1a1a2e',
            fg='#ffffff',
            padx=20,
            pady=15
        )
        config_frame.pack(fill='x', padx=20, pady=15)
        
        # Airtel number
        tk.Label(
            config_frame,
            text="Airtel Number:",
            font=("Arial", 11),
            bg='#1a1a2e',
            fg='#ffffff'
        ).grid(row=0, column=0, sticky='w', pady=5)
        
        self.airtel_entry = tk.Entry(config_frame, font=("Arial", 11), bg='#16213e', fg='#ffffff', insertbackground='#ffffff')
        self.airtel_entry.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        
        # MTN number
        tk.Label(
            config_frame,
            text="MTN Number:",
            font=("Arial", 11),
            bg='#1a1a2e',
            fg='#ffffff'
        ).grid(row=1, column=0, sticky='w', pady=5)
        
        self.mtn_entry = tk.Entry(config_frame, font=("Arial", 11), bg='#16213e', fg='#ffffff', insertbackground='#ffffff')
        self.mtn_entry.grid(row=1, column=1, padx=10, pady=5, sticky='ew')
        
        # Amount
        tk.Label(
            config_frame,
            text="Amount (UGX):",
            font=("Arial", 11),
            bg='#1a1a2e',
            fg='#ffffff'
        ).grid(row=2, column=0, sticky='w', pady=5)
        
        self.amount_entry = tk.Entry(config_frame, font=("Arial", 11), bg='#16213e', fg='#ffffff', insertbackground='#ffffff')
        self.amount_entry.grid(row=2, column=1, padx=10, pady=5, sticky='ew')
        
        config_frame.columnconfigure(1, weight=1)
        
        # Load current config
        self.load_payment_config()
        
        # Save button
        save_btn = tk.Button(
            config_frame,
            text="💾 Save Configuration",
            font=("Arial", 11, "bold"),
            bg='#00ff88',
            fg='#1a1a2e',
            padx=15,
            pady=8,
            command=self.save_payment_config
        )
        save_btn.grid(row=3, column=0, columnspan=2, pady=15)
        
        # Stats
        stats_frame = tk.LabelFrame(
            self.tab_settings,
            text="📊 Statistics",
            font=("Arial", 12, "bold"),
            bg='#1a1a2e',
            fg='#ffffff',
            padx=20,
            pady=15
        )
        stats_frame.pack(fill='both', expand=True, padx=20, pady=15)
        
        self.stats_label = tk.Label(
            stats_frame,
            text="",
            font=("Arial", 11),
            bg='#1a1a2e',
            fg='#aaaaaa',
            justify='left'
        )
        self.stats_label.pack(anchor='w')
        
    def load_payment_config(self):
        """Load payment configuration"""
        try:
            from payment_window import PAYMENT_INFO
            self.airtel_entry.insert(0, PAYMENT_INFO.get('airtel_number', ''))
            self.mtn_entry.insert(0, PAYMENT_INFO.get('mtn_number', ''))
            self.amount_entry.insert(0, PAYMENT_INFO.get('amount', '50'))
        except:
            pass
    
    def save_payment_config(self):
        """Save payment configuration"""
        messagebox.showinfo("Settings", "Configuration saved!\n\nNote: Update PAYMENT_INFO in payment_window.py to persist changes.")
        
    def refresh_data(self):
        """Refresh all data"""
        self.load_pending_payments()
        self.load_active_licenses()
        self.update_stats()
        
    def load_pending_payments(self):
        """Load pending payments"""
        # Clear tree
        for item in self.pending_tree.get_children():
            self.pending_tree.delete(item)
        
        try:
            if os.path.exists("pending_payments.json"):
                with open("pending_payments.json", 'r') as f:
                    payments = json.load(f)
                    
                for p in payments:
                    if p.get('status') == 'pending':
                        self.pending_tree.insert('', 'end', values=(
                            p.get('phone_number', ''),
                            p.get('transaction_id', ''),
                            p.get('device_id', ''),
                            p.get('network', ''),
                            p.get('amount', ''),
                            p.get('submitted_at', '')[:16]
                        ))
        except Exception as e:
            print(f"Error loading payments: {e}")
            
    def load_active_licenses(self):
        """Load active licenses"""
        # Clear tree
        for item in self.licenses_tree.get_children():
            self.licenses_tree.delete(item)
        
        try:
            if os.path.exists("approved_licenses.json"):
                with open("approved_licenses.json", 'r') as f:
                    licenses = json.load(f)
                    
                for key, info in licenses.items():
                    if info.get('status') == 'approved':
                        self.licenses_tree.insert('', 'end', values=(
                            key,
                            info.get('device_id', 'N/A'),
                            info.get('phone_number', 'N/A'),
                            info.get('plan', 'monthly'),
                            info.get('expires_at', 'N/A')[:10],
                            info.get('status', 'active')
                        ))
        except Exception as e:
            print(f"Error loading licenses: {e}")
            
    def update_stats(self):
        """Update statistics"""
        try:
            pending_count = 0
            active_count = 0
            
            if os.path.exists("pending_payments.json"):
                with open("pending_payments.json", 'r') as f:
                    pending = json.load(f)
                    pending_count = len([p for p in pending if p.get('status') == 'pending'])
                    
            if os.path.exists("approved_licenses.json"):
                with open("approved_licenses.json", 'r') as f:
                    licenses = json.load(f)
                    active_count = len([l for l in licenses.values() if l.get('status') == 'approved'])
                    
            stats_text = f"""
📊 Current Statistics:
━━━━━━━━━━━━━━━━━━━━━
• Pending Payments: {pending_count}
• Active Licenses: {active_count}
• Total Generated: {len(licenses) if os.path.exists('approved_licenses.json') else 0}
            """
            
            self.stats_label.config(text=stats_text)
        except:
            pass
        
    def approve_selected(self):
        """Approve selected payment"""
        selection = self.pending_tree.selection()
        if not selection:
            messagebox.showwarning("Select Payment", "Please select a payment to approve")
            return
            
        item = self.pending_tree.item(selection[0])
        values = item['values']
        
        phone = values[0]
        transaction_id = values[1]
        device_id = values[2]
        network = values[3]
        
        # Get months based on plan
        plan = simpledialog.askstring("Select Plan", "Enter plan (1, 3, 6, or 12 months):", initialvalue="1")
        if not plan:
            return
            
        try:
            months = int(plan)
        except:
            messagebox.showerror("Error", "Invalid plan")
            return
        
        # Generate license key
        license_key = self.admin_mgr.approve_payment(
            phone_number=phone,
            transaction_id=transaction_id,
            plan=f"{months}month",
            months=months
        )
        
        # Remove from pending
        try:
            with open("pending_payments.json", 'r') as f:
                payments = json.load(f)
                
            payments = [p for p in payments if p.get('transaction_id') != transaction_id]
            
            with open("pending_payments.json", 'w') as f:
                json.dump(payments, f, indent=2)
        except:
            pass
        
        messagebox.showinfo(
            "Payment Approved",
            f"✅ Payment approved!\n\n"
            f"License Key: {license_key}\n\n"
            f"Share this key with the user."
        )
        
        self.refresh_data()
        
    def reject_selected(self):
        """Reject selected payment"""
        selection = self.pending_tree.selection()
        if not selection:
            messagebox.showwarning("Select Payment", "Please select a payment to reject")
            return
            
        item = self.pending_tree.item(selection[0])
        values = item['values']
        
        transaction_id = values[1]
        
        confirm = messagebox.askyesno(
            "Reject Payment",
            f"Are you sure you want to reject this payment?\n\nTransaction: {transaction_id}"
        )
        
        if confirm:
            # Remove from pending
            try:
                with open("pending_payments.json", 'r') as f:
                    payments = json.load(f)
                    
                payments = [p for p in payments if p.get('transaction_id') != transaction_id]
                
                with open("pending_payments.json", 'w') as f:
                    json.dump(payments, f, indent=2)
            except:
                pass
                
            messagebox.showinfo("Rejected", "Payment rejected and removed.")
            self.refresh_data()
            
    def cancel_subscription(self):
        """Cancel selected subscription"""
        selection = self.licenses_tree.selection()
        if not selection:
            messagebox.showwarning("Select License", "Please select a license to cancel")
            return
            
        item = self.licenses_tree.item(selection[0])
        license_key = item['values'][0]
        
        reason = simpledialog.askstring("Cancel Reason", "Enter reason for cancellation (optional):")
        
        if self.admin_mgr.cancel_subscription(license_key, reason or "Manual cancellation"):
            messagebox.showinfo("Cancelled", f"License {license_key} has been cancelled.")
            self.refresh_data()
        else:
            messagebox.showerror("Error", "Failed to cancel license")
            
    def extend_license(self):
        """Extend selected license"""
        selection = self.licenses_tree.selection()
        if not selection:
            messagebox.showwarning("Select License", "Please select a license to extend")
            return
            
        item = self.licenses_tree.item(selection[0])
        license_key = item['values'][0]
        
        months = simpledialog.askinteger("Extend License", "How many months to add?", initialvalue=1)
        if not months or months <= 0:
            return
            
        # Load and extend
        try:
            with open("approved_licenses.json", 'r') as f:
                licenses = json.load(f)
                
            if license_key in licenses:
                from datetime import datetime, timedelta
                current_exp = licenses[license_key].get('expires_at', datetime.now().isoformat())
                current_exp_date = datetime.fromisoformat(current_exp)
                new_exp = current_exp_date + timedelta(days=30 * months)
                
                licenses[license_key]['expires_at'] = new_exp.isoformat()
                licenses[license_key]['extended_at'] = datetime.now().isoformat()
                licenses[license_key]['extension_months'] = months
                
                with open("approved_licenses.json", 'w') as f:
                    json.dump(licenses, f, indent=2)
                    
                messagebox.showinfo("Extended", f"License extended by {months} months!")
                self.refresh_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extend: {str(e)}")
            
    def generate_license(self):
        """Generate new license key"""
        plan = self.plan_var.get()
        
        months_map = {
            "monthly": 1,
            "3months": 3,
            "6months": 6,
            "yearly": 12
        }
        
        months = months_map.get(plan, 1)
        
        license_key = self.admin_mgr.generate_license_key(plan, months)
        
        self.generated_key_label.config(text=license_key)
        self.copy_btn.config(state='normal')
        
    def copy_key(self):
        """Copy generated key to clipboard"""
        key = self.generated_key_label.cget("text")
        if key:
            self.window.clipboard_clear()
            self.window.clipboard_append(key)
            messagebox.showinfo("Copied", "License key copied to clipboard!")


if __name__ == "__main__":
    app = AdminPanel()
    app.window.mainloop()