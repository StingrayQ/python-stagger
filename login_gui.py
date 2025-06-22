

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import re

class LoginWindow:


    def __init__(self, database, login_success_callback, exit_callback):

        self.db = database
        self.login_success_callback = login_success_callback
        self.exit_callback = exit_callback

        # Create main window
        self.root = tk.Tk()
        self.root.title("Stagger Calculator - Login")
        self.root.geometry("400x600")
        self.root.resizable(False, False)

        # Center the window
        self.center_window()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # Create the interface
        self.create_widgets()

        # Start the main loop
        self.root.mainloop()

# centers the window on the screen
    def center_window(self):

        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):


        # Title
        title_frame = ttk.Frame(self.root)
        title_frame.pack(pady=20)

        title_label = tk.Label(
            title_frame,
            text="🏁 Stagger Calculator",
            font=("Arial", 18, "bold"),
            fg="#2E86AB"
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="Professional Racing Setup Tool",
            font=("Arial", 10),
            fg="#666666"
        )
        subtitle_label.pack(pady=(5, 0))

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=20, pady=20)

        # Login tab
        self.login_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.login_frame, text="Login")
        self.create_login_tab()

        # Register tab
        self.register_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.register_frame, text="Register")
        self.create_register_tab()

        # Buttons frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        exit_button = ttk.Button(
            button_frame,
            text="Exit",
            command=self.on_window_close,
            width=15
        )
        exit_button.pack()

    def create_login_tab(self):

        # Spacing
        ttk.Label(self.login_frame, text="").pack(pady=10)

        # Username
        ttk.Label(self.login_frame, text="Username:", font=("Arial", 10)).pack(anchor='w', padx=20)
        self.login_username = ttk.Entry(self.login_frame, width=25, font=("Arial", 11))
        self.login_username.pack(pady=(5, 15), padx=20)

        # Password
        ttk.Label(self.login_frame, text="Password:", font=("Arial", 10)).pack(anchor='w', padx=20)
        self.login_password = ttk.Entry(self.login_frame, width=25, font=("Arial", 11), show="*")
        self.login_password.pack(pady=(5, 20), padx=20)

        # Login button
        login_button = ttk.Button(
            self.login_frame,
            text="Login",
            command=self.handle_login,
            width=20
        )
        login_button.pack(pady=10)

        # Bind Enter key to login
        self.login_username.bind('<Return>', lambda e: self.handle_login())
        self.login_password.bind('<Return>', lambda e: self.handle_login())

        # Demo credentials info
        demo_frame = ttk.LabelFrame(self.login_frame, text="Demo Account", padding=10)
        demo_frame.pack(pady=20, padx=20, fill='x')

        ttk.Label(demo_frame, text="Username: demo", font=("Arial", 9)).pack(anchor='w')
        ttk.Label(demo_frame, text="Password: demo123", font=("Arial", 9)).pack(anchor='w')

        demo_button = ttk.Button(
            demo_frame,
            text="Use Demo Account",
            command=self.use_demo_account
        )
        demo_button.pack(pady=(10, 0))

    def create_register_tab(self):

        # Spacing
        ttk.Label(self.register_frame, text="").pack(pady=10)

        # Username
        ttk.Label(self.register_frame, text="Username:", font=("Arial", 10)).pack(anchor='w', padx=20)
        self.reg_username = ttk.Entry(self.register_frame, width=25, font=("Arial", 11))
        self.reg_username.pack(pady=(5, 10), padx=20)

        # Email
        ttk.Label(self.register_frame, text="Email:", font=("Arial", 10)).pack(anchor='w', padx=20)
        self.reg_email = ttk.Entry(self.register_frame, width=25, font=("Arial", 11))
        self.reg_email.pack(pady=(5, 10), padx=20)

        # Team name
        ttk.Label(self.register_frame, text="Team Name:", font=("Arial", 10)).pack(anchor='w', padx=20)
        self.reg_team = ttk.Entry(self.register_frame, width=25, font=("Arial", 11))
        self.reg_team.pack(pady=(5, 10), padx=20)

        # Password
        ttk.Label(self.register_frame, text="Password:", font=("Arial", 10)).pack(anchor='w', padx=20)
        self.reg_password = ttk.Entry(self.register_frame, width=25, font=("Arial", 11), show="*")
        self.reg_password.pack(pady=(5, 10), padx=20)

        # Confirm password
        ttk.Label(self.register_frame, text="Confirm Password:", font=("Arial", 10)).pack(anchor='w', padx=20)
        self.reg_confirm = ttk.Entry(self.register_frame, width=25, font=("Arial", 11), show="*")
        self.reg_confirm.pack(pady=(5, 20), padx=20)

        # Register button
        register_button = ttk.Button(
            self.register_frame,
            text="Create Account",
            command=self.handle_register,
            width=20
        )
        register_button.pack(pady=10)

        # Bind Enter key to register
        self.reg_confirm.bind('<Return>', lambda e: self.handle_register())

    def use_demo_account(self):

        self.login_username.delete(0, tk.END)
        self.login_username.insert(0, "demo")
        self.login_password.delete(0, tk.END)
        self.login_password.insert(0, "demo123")

    def validate_email(self, email):

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def handle_login(self):

        username = self.login_username.get().strip()
        password = self.login_password.get()

        if not username or not password:
            messagebox.showerror("Login Error", "Please enter both username and password.")
            return

        # Try to authenticate
        user_data = self.db.authenticate_user(username, password)

        if user_data:
            # Success! Close this window and call the callback
            self.root.withdraw()  # Hide the window first
            self.login_success_callback(user_data)
            self.root.quit()  # Exit the mainloop
            self.root.destroy()  # Destroy the window
        else:
            messagebox.showerror("Login Error", "Invalid username or password.")
            self.login_password.delete(0, tk.END)  # Clear password field

    def handle_register(self):

        username = self.reg_username.get().strip()
        email = self.reg_email.get().strip()
        team_name = self.reg_team.get().strip()
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()

        # Validation
        if not all([username, email, team_name, password, confirm]):
            messagebox.showerror("Registration Error", "Please fill in all fields.")
            return

        if len(username) < 3:
            messagebox.showerror("Registration Error", "Username must be at least 3 characters.")
            return

        if not self.validate_email(email):
            messagebox.showerror("Registration Error", "Please enter a valid email address.")
            return

        if len(password) < 6:
            messagebox.showerror("Registration Error", "Password must be at least 6 characters.")
            return

        if password != confirm:
            messagebox.showerror("Registration Error", "Passwords do not match.")
            return

        # Try to create account
        success, user_id, message = self.db.create_user(username, email, password, team_name)

        if success:
            messagebox.showinfo("Registration Successful", message)
            # Switch to login tab and fill username
            self.notebook.select(0)  # Switch to login tab
            self.login_username.delete(0, tk.END)
            self.login_username.insert(0, username)
            self.login_password.focus()
            # Clear registration fields
            self.reg_username.delete(0, tk.END)
            self.reg_email.delete(0, tk.END)
            self.reg_team.delete(0, tk.END)
            self.reg_password.delete(0, tk.END)
            self.reg_confirm.delete(0, tk.END)
        else:
            messagebox.showerror("Registration Error", message)

    def on_window_close(self):

        self.exit_callback()

    def destroy(self):

        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass

# Test the login window
if __name__ == "__main__":
    from staggerDB import StaggerDatabase

    def test_login_success(user_data):
        print(f"Login successful: {user_data}")
        root.quit()

    def test_exit():
        print("Exit requested")
        root.quit()

    # Create test database and ensure demo user exists
    db = StaggerDatabase("test_login.db")
    db.create_user("demo", "demo@test.com", "demo123", "Demo Racing Team")

    root = tk.Tk()
    root.withdraw()  # Hide the root window

    login = LoginWindow(db, test_login_success, test_exit)

    root.mainloop()