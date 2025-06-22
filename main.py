

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Import our modules
from staggerDB import StaggerDatabase
from login_gui import LoginWindow
from stagger_gui import StaggerCalculatorGUI

class StaggerCalculatorApp:


    def __init__(self):

        self.db = StaggerDatabase()
        self.current_user = None
        self.login_window = None
        self.main_window = None

        # Start with login
        self.show_login()

    def show_login(self):

        if self.main_window:
            self.main_window.destroy()
            self.main_window = None

        self.login_window = LoginWindow(self.db, self.on_login_success, self.on_app_exit)

    def on_login_success(self, user_data):

        self.current_user = user_data
        print(f"User logged in: {user_data['username']} ({user_data['team_name']})")

        # The login window should already be closing itself
        # Just set login_window to None
        self.login_window = None

        # Show main calculator
        self.show_main_calculator()

    def show_main_calculator(self):

        if not self.current_user:
            messagebox.showerror("Error", "No user logged in!")
            self.show_login()
            return

        # Create main window
        self.main_window = StaggerCalculatorGUI(
            user=self.current_user,
            db=self.db,
            logout_callback=self.on_logout
        )

        # Start the main loop for the calculator window
        try:
            self.main_window.root.mainloop()
        except:
            pass

    def on_logout(self):

        print(f"User logged out: {self.current_user['username']}")
        self.current_user = None

        # Close main window
        if self.main_window:
            try:
                self.main_window.root.quit()  # Exit the calculator's mainloop
                self.main_window.destroy()
            except:
                pass
            self.main_window = None

        # Show login again
        self.show_login()

    def on_app_exit(self):

        print("Application exiting...")
        if self.login_window:
            self.login_window.destroy()
        if self.main_window:
            self.main_window.destroy()
        sys.exit(0)

def main():

    try:
        print("Starting Stagger Calculator Application...")
        app = StaggerCalculatorApp()



    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Startup Error", f"Failed to start application:\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()