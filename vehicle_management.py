import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import re
import sqlite3


class AddVehicleWindow:
    def __init__(self, parent, db, user, callback=None):
        self.db = db
        self.user = user
        self.callback = callback

        # Create popup window
        self.window = tk.Toplevel(parent)
        self.window.title("Add New Vehicle")
        self.window.geometry("500x550")  # Made taller to fit all content
        self.window.resizable(False, False)

        # Make it modal
        self.window.transient(parent)
        self.window.grab_set()

        # Center the window
        self.center_window()

        # Create the interface
        self.create_widgets()

        # Focus on first entry
        self.vehicle_name_entry.focus()

    def center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # Title
        title_frame = ttk.Frame(self.window)
        title_frame.pack(pady=15)

        title_label = tk.Label(
            title_frame,
            text="Add New Vehicle",
            font=("Arial", 14, "bold"),
            fg="#2E86AB"
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text=f"Team: {self.user['team_name']}",
            font=("Arial", 9),
            fg="#666666"
        )
        subtitle_label.pack(pady=(5, 0))

        # Main form frame
        form_frame = ttk.LabelFrame(self.window, text="Vehicle Information", padding=15)
        form_frame.pack(fill='x', padx=20, pady=(10, 15))

        # Configure grid weights for better layout
        form_frame.grid_columnconfigure(1, weight=1)

        # Vehicle Name
        ttk.Label(form_frame, text="Vehicle Name:", font=("Arial", 10)).grid(row=0, column=0, sticky='w', pady=8)
        self.vehicle_name_entry = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.vehicle_name_entry.grid(row=0, column=1, pady=8, padx=(10, 0), sticky='ew')

        # Vehicle Type
        ttk.Label(form_frame, text="Vehicle Type:", font=("Arial", 10)).grid(row=1, column=0, sticky='w', pady=8)
        self.vehicle_type_var = tk.StringVar(value="Stock Car")
        self.vehicle_type_combo = ttk.Combobox(form_frame, textvariable=self.vehicle_type_var,
                                               values=["Stock Car", "Modified", "Late Model", "Sprint Car", "Other"],
                                               width=27, font=("Arial", 10))
        self.vehicle_type_combo.grid(row=1, column=1, pady=8, padx=(10, 0), sticky='ew')

        # Track Width
        ttk.Label(form_frame, text="Track Width (inches):", font=("Arial", 10)).grid(row=2, column=0, sticky='w',
                                                                                     pady=8)
        self.track_width_entry = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.track_width_entry.grid(row=2, column=1, pady=8, padx=(10, 0), sticky='ew')

        # Inside Tire Circumference
        ttk.Label(form_frame, text="Inside Tire Circumference (inches):", font=("Arial", 10)).grid(row=3, column=0,
                                                                                                   sticky='w', pady=8)
        self.tire_circ_entry = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.tire_circ_entry.grid(row=3, column=1, pady=8, padx=(10, 0), sticky='ew')

        # Wheelbase (optional)
        ttk.Label(form_frame, text="Wheelbase (inches, optional):", font=("Arial", 10)).grid(row=4, column=0,
                                                                                             sticky='w', pady=8)
        self.wheelbase_entry = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.wheelbase_entry.grid(row=4, column=1, pady=8, padx=(10, 0), sticky='ew')

        # Weight (optional)
        ttk.Label(form_frame, text="Weight (lbs, optional):", font=("Arial", 10)).grid(row=5, column=0, sticky='w',
                                                                                       pady=8)
        self.weight_entry = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.weight_entry.grid(row=5, column=1, pady=8, padx=(10, 0), sticky='ew')

        # Notes
        ttk.Label(form_frame, text="Notes:", font=("Arial", 10)).grid(row=6, column=0, sticky='nw', pady=8)

        # Create frame for text widget with scrollbar
        text_frame = ttk.Frame(form_frame)
        text_frame.grid(row=6, column=1, pady=8, padx=(10, 0), sticky='ew')

        self.notes_text = tk.Text(text_frame, width=30, height=3, font=("Arial", 10))
        notes_scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=notes_scrollbar.set)

        self.notes_text.pack(side='left', fill='both', expand=True)
        notes_scrollbar.pack(side='right', fill='y')

        # Button frame - Make sure it's visible
        button_frame = ttk.Frame(self.window)
        button_frame.pack(pady=20, padx=20)

        # Save button
        save_button = ttk.Button(
            button_frame,
            text="💾 Save Vehicle",
            command=self.save_vehicle,
            width=20
        )
        save_button.pack(side='left', padx=10)

        # Cancel button
        cancel_button = ttk.Button(
            button_frame,
            text="❌ Cancel",
            command=self.close_window,
            width=20
        )
        cancel_button.pack(side='left', padx=10)

        # Bind Enter key to save
        self.window.bind('<Return>', lambda e: self.save_vehicle())
        self.window.bind('<Escape>', lambda e: self.close_window())

        # Add some example data placeholders with different approach
        self.add_placeholders()

        # Make save button more prominent
        save_button.configure(style='Accent.TButton') if hasattr(save_button, 'configure') else None

    def add_placeholders(self):
        """Add placeholder text to help users"""
        # Add some helpful tooltips/examples
        self.vehicle_name_entry.insert(0, "e.g., Car #42")
        self.track_width_entry.insert(0, "e.g., 60.0")
        self.tire_circ_entry.insert(0, "e.g., 82.5")
        self.wheelbase_entry.insert(0, "e.g., 108.0")
        self.weight_entry.insert(0, "e.g., 3200")

        # Clear placeholders when user clicks
        def clear_placeholder(entry, placeholder):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)

        def restore_placeholder(entry, placeholder):
            if not entry.get():
                entry.insert(0, placeholder)

        placeholders = [
            (self.vehicle_name_entry, "e.g., Car #42"),
            (self.track_width_entry, "e.g., 60.0"),
            (self.tire_circ_entry, "e.g., 82.5"),
            (self.wheelbase_entry, "e.g., 108.0"),
            (self.weight_entry, "e.g., 3200")
        ]

        for entry, placeholder in placeholders:
            entry.bind('<FocusIn>', lambda e, ent=entry, ph=placeholder: clear_placeholder(ent, ph))
            entry.bind('<FocusOut>', lambda e, ent=entry, ph=placeholder: restore_placeholder(ent, ph))

    def validate_inputs(self):

        errors = []

        # Vehicle name is required
        name = self.vehicle_name_entry.get().strip()
        if not name or name == "e.g., Car #42":
            errors.append("Vehicle name is required")

        # Optional field validation - only validate if user entered something
        track_width_str = self.track_width_entry.get().strip()
        if track_width_str and track_width_str != "e.g., 60.0":
            try:
                track_width = float(track_width_str)
                if track_width <= 0:
                    errors.append("Track width must be a positive number")
                # elif track_width > 100:
                #     errors.append("Track width seems unrealistic (>100 inches)")
            except ValueError:
                errors.append("Track width must be a valid number")

        # Tire circumference validation - only if entered
        tire_circ_str = self.tire_circ_entry.get().strip()
        if tire_circ_str and tire_circ_str != "e.g., 82.5":
            try:
                tire_circ = float(tire_circ_str)
                if tire_circ <= 0:
                    errors.append("Tire circumference must be a positive number")
                # elif tire_circ < 60 or tire_circ > 120:
                #     errors.append("Tire circumference seems unrealistic (should be 60-120 inches)")
            except ValueError:
                errors.append("Tire circumference must be a valid number")

        # Optional fields validation
        wheelbase_str = self.wheelbase_entry.get().strip()
        if wheelbase_str and wheelbase_str != "e.g., 108.0":
            try:
                wheelbase = float(wheelbase_str)
                if wheelbase <= 0:
                    errors.append("Wheelbase must be a positive number")
            except ValueError:
                errors.append("Wheelbase must be a valid number")

        weight_str = self.weight_entry.get().strip()
        if weight_str and weight_str != "e.g., 3200":
            try:
                weight = float(weight_str)
                if weight <= 0:
                    errors.append("Weight must be a positive number")
            except ValueError:
                errors.append("Weight must be a valid number")

        return errors

    def save_vehicle(self):

        # Validate inputs
        errors = self.validate_inputs()
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return

        # Get values
        name = self.vehicle_name_entry.get().strip()
        vehicle_type = self.vehicle_type_var.get()

        # Optional values - only include if user entered them
        track_width_str = self.track_width_entry.get().strip()
        track_width = None
        if track_width_str and track_width_str != "e.g., 60.0":
            track_width = float(track_width_str)

        tire_circ_str = self.tire_circ_entry.get().strip()
        tire_circ = None
        if tire_circ_str and tire_circ_str != "e.g., 82.5":
            tire_circ = float(tire_circ_str)

        wheelbase_str = self.wheelbase_entry.get().strip()
        wheelbase = float(wheelbase_str) if wheelbase_str and wheelbase_str != "e.g., 108.0" else None

        weight_str = self.weight_entry.get().strip()
        weight = float(weight_str) if weight_str and weight_str != "e.g., 3200" else None

        notes = self.notes_text.get("1.0", tk.END).strip()

        # Create notes with additional info
        additional_info = []
        if wheelbase:
            additional_info.append(f"Wheelbase: {wheelbase}\"")
        if weight:
            additional_info.append(f"Weight: {weight} lbs")
        if notes:
            additional_info.append(f"Notes: {notes}")

        combined_notes = " | ".join(additional_info)

        # Save to database with optional values
        success, message = self.db.save_vehicle(
            vehicle_name=name,
            track_width=track_width,  # Can be None
            inside_tire_circumference=tire_circ,  # Can be None
            vehicle_type=vehicle_type,
            user_id=self.user['id']
        )

        if success:
            # Show what was saved
            saved_info = f"Vehicle '{name}' saved successfully!\n\nSaved information:"
            saved_info += f"\n• Type: {vehicle_type}"
            if track_width:
                saved_info += f"\n• Track Width: {track_width}\""
            if tire_circ:
                saved_info += f"\n• Tire Circumference: {tire_circ}\""
            if additional_info:
                saved_info += f"\n• Additional: {combined_notes}"

            messagebox.showinfo("Success", saved_info)

            # Call callback if provided (to refresh dropdowns)
            if self.callback:
                self.callback()
                self.close_window()
        else:
            messagebox.showerror("Error", message)

    def close_window(self):

        self.window.grab_release()
        self.window.destroy()


class VehicleManagementWindow:


    def __init__(self, parent, db, user, callback=None):

        self.db = db
        self.user = user
        self.callback = callback

        # Create popup window
        self.window = tk.Toplevel(parent)
        self.window.title("Manage Vehicles")
        self.window.geometry("800x600")
        self.window.resizable(True, True)

        # Make it modal
        self.window.transient(parent)
        self.window.grab_set()

        # Center the window
        self.center_window()

        # Create the interface
        self.create_widgets()

        # Load vehicles
        self.refresh_vehicle_list()

    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):


        # Title
        title_frame = ttk.Frame(self.window)
        title_frame.pack(pady=15, fill='x')

        title_label = tk.Label(
            title_frame,
            text="Manage Vehicles",
            font=("Arial", 16, "bold"),
            fg="#2E86AB"
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text=f"Team: {self.user['team_name']} | User: {self.user['username']}",
            font=("Arial", 10),
            fg="#666666"
        )
        subtitle_label.pack(pady=(5, 0))

        # Main content frame
        content_frame = ttk.Frame(self.window)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Vehicle list frame
        list_frame = ttk.LabelFrame(content_frame, text="Your Vehicles", padding=10)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))

        # Create treeview for vehicle list
        columns = ('Name', 'Type', 'Track Width', 'Tire Circumference', 'Created')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)

        # Define column headings and widths
        column_widths = {
            'Name': 150,
            'Type': 120,
            'Track Width': 100,
            'Tire Circumference': 120,
            'Created': 150
        }

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths[col])

        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        # Button frame
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill='x', pady=10)

        # Add Vehicle button
        add_button = ttk.Button(
            button_frame,
            text="➕ Add New Vehicle",
            command=self.add_new_vehicle,
            width=20
        )
        add_button.pack(side='left', padx=(0, 10))

        # Edit Vehicle button
        edit_button = ttk.Button(
            button_frame,
            text="✏️ Edit Selected",
            command=self.edit_selected_vehicle,
            width=20
        )
        edit_button.pack(side='left', padx=(0, 10))

        # Delete Vehicle button
        delete_button = ttk.Button(
            button_frame,
            text="🗑️ Delete Selected",
            command=self.delete_selected_vehicle,
            width=20
        )
        delete_button.pack(side='left', padx=(0, 10))

        # Refresh button
        refresh_button = ttk.Button(
            button_frame,
            text="🔄 Refresh",
            command=self.refresh_vehicle_list,
            width=15
        )
        refresh_button.pack(side='left', padx=(0, 10))

        # Close button
        close_button = ttk.Button(
            button_frame,
            text="❌ Close",
            command=self.close_window,
            width=15
        )
        close_button.pack(side='right')

        # Status bar
        self.status_label = tk.Label(content_frame, text="", font=("Arial", 9), fg="gray")
        self.status_label.pack(pady=(10, 0))

        # Bind double-click to edit
        self.tree.bind('<Double-1>', lambda e: self.edit_selected_vehicle())

    def refresh_vehicle_list(self):

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get vehicles from database
        vehicles = self.db.get_user_vehicles(self.user['id'])

        # Add vehicles to tree
        for vehicle in vehicles:
            # vehicle format: (name, track_width, inside_tire_circumference, vehicle_type, created_date)
            name = vehicle[0]
            track_width = f"{vehicle[1]}\"" if vehicle[1] is not None else "Not set"
            tire_circ = f"{vehicle[2]}\"" if vehicle[2] is not None else "Not set"
            vehicle_type = vehicle[3]
            created_date = vehicle[4][:10] if len(vehicle) > 4 and vehicle[4] else "Unknown"

            self.tree.insert('', 'end', values=(name, vehicle_type, track_width, tire_circ, created_date))

        # Update status
        count = len(vehicles)
        self.status_label.config(text=f"Showing {count} vehicle{'s' if count != 1 else ''}")

    def add_new_vehicle(self):

        AddVehicleWindow(self.window, self.db, self.user, self.on_vehicle_changed)

    def edit_selected_vehicle(self):


        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a vehicle to edit.")
            return

        # Get selected vehicle data
        item = self.tree.item(selection[0])
        vehicle_name = item['values'][0]

        # Open edit window
        EditVehicleWindow(self.window, self.db, self.user, vehicle_name, self.on_vehicle_changed)

    # Add this method to your VehicleManager class:

    def show_edit_vehicle_window(self, parent, vehicle_name, callback=None):

        EditVehicleWindow(parent, self.db, self.user, vehicle_name, callback)

    def delete_selected_vehicle(self):

        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a vehicle to delete.")
            return

        # Get selected vehicle data
        item = self.tree.item(selection[0])
        vehicle_name = item['values'][0]

        # Confirm deletion
        response = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete '{vehicle_name}'?\n\nThis action cannot be undone."
        )

        if response:
            # Find the vehicle ID and delete it
            vehicles = self.db.get_user_vehicles(self.user['id'])
            for vehicle in vehicles:
                if vehicle[0] == vehicle_name:  # vehicle[0] is the name
                    # Get the full vehicle record with ID
                    vehicle_id = self.get_vehicle_id_by_name(vehicle_name)
                    if vehicle_id:
                        success, message = self.db.delete_vehicle(self.user['id'], vehicle_id)
                        if success:
                            messagebox.showinfo("Success", f"Vehicle '{vehicle_name}' deleted successfully!")
                            self.refresh_vehicle_list()
                            self.on_vehicle_changed()
                        else:
                            messagebox.showerror("Error", f"Failed to delete vehicle: {message}")
                    break

    def get_vehicle_id_by_name(self, vehicle_name):
        return self.db.get_vehicle_id_by_name(self.user['id'], vehicle_name)
        # try:
        #     conn = sqlite3.connect(self.db.db_name, timeout=10.0)
        #     cursor = conn.cursor()
        #
        #     cursor.execute('''
        #                    SELECT id
        #                    FROM vehicles
        #                    WHERE user_id = ?
        #                      AND vehicle_name = ?
        #                    ''', (self.user['id'], vehicle_name))
        #
        #     result = cursor.fetchone()
        #     conn.close()
        #     return result[0] if result else None
        #
        # except Exception as e:
        #     print(f"Error getting vehicle ID: {e}")
        #     return None

    def on_vehicle_changed(self):
        """Called when vehicles are added/edited/deleted"""
        if self.callback:
            self.callback()

    def close_window(self):
        """Close the window"""
        self.window.grab_release()
        self.window.destroy()


class VehicleManager:
    """Main vehicle management class"""

    def __init__(self, db, user):
        self.db = db
        self.user = user

    def show_add_vehicle_window(self, parent, callback=None):
        """Show the add vehicle window"""
        AddVehicleWindow(parent, self.db, self.user, callback)

    def show_manage_vehicles_window(self, parent, callback=None):
        """Show the vehicle management window"""
        VehicleManagementWindow(parent, self.db, self.user, callback)

    def get_user_vehicles(self):
        """Get all vehicles for the current user"""
        return self.db.get_user_vehicles(self.user['id'])

    def get_vehicle_by_name(self, vehicle_name):
        """Get specific vehicle by name for current user"""
        vehicles = self.get_user_vehicles()
        for vehicle in vehicles:
            if vehicle[0] == vehicle_name:  # vehicle_name is at index 0
                return {
                    'name': vehicle[0],
                    'track_width': vehicle[1] if vehicle[1] is not None else None,
                    'inside_tire_circumference': vehicle[2] if vehicle[2] is not None else None,
                    'vehicle_type': vehicle[3]
                }
        return None

class EditVehicleWindow:
    def __init__(self, parent, db, user, vehicle_name, callback=None):
        self.db = db
        self.user = user
        self.vehicle_name = vehicle_name
        self.callback = callback
        self.original_vehicle_data = None

        # Create popup window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Edit Vehicle - {vehicle_name}")
        self.window.geometry("500x550")
        self.window.resizable(False, False)

        # Make it modal
        self.window.transient(parent)
        self.window.grab_set()

        # Center the window
        self.center_window()

        # Load the current vehicle data
        self.load_vehicle_data()

        # Create the interface
        self.create_widgets()

        # Populate the form with current data
        self.populate_form()

        # Focus on first entry
        self.vehicle_name_entry.focus()

    def center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def load_vehicle_data(self):
        """Load the current vehicle data from database using the database method"""
        try:
            # Get vehicle ID first
            vehicle_id = self.db.get_vehicle_id_by_name(self.user['id'], self.vehicle_name)

            if not vehicle_id:
                messagebox.showerror("Error", f"Vehicle '{self.vehicle_name}' not found!")
                self.close_window()
                return

            # Get full vehicle data
            vehicle_data = self.db.get_vehicle_by_id(vehicle_id, self.user['id'])

            if vehicle_data:
                self.original_vehicle_data = {
                    'id': vehicle_data[0],
                    'name': vehicle_data[1],
                    'track_width': vehicle_data[2],
                    'inside_tire_circumference': vehicle_data[3],
                    'vehicle_type': vehicle_data[4],
                    'created_date': vehicle_data[5]
                }
            else:
                messagebox.showerror("Error", f"Vehicle '{self.vehicle_name}' not found!")
                self.close_window()

        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading vehicle data: {str(e)}")
            self.close_window()

    def update_vehicle(self):
        """Update the vehicle in database using the database method"""
        # Validate inputs
        errors = self.validate_inputs()
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return

        # Get values
        name = self.vehicle_name_entry.get().strip()
        vehicle_type = self.vehicle_type_var.get()

        # Optional values
        track_width_str = self.track_width_entry.get().strip()
        track_width = float(track_width_str) if track_width_str else None

        tire_circ_str = self.tire_circ_entry.get().strip()
        tire_circ = float(tire_circ_str) if tire_circ_str else None

        # Use the database method to update
        success, message = self.db.update_vehicle(
            vehicle_id=self.original_vehicle_data['id'],
            user_id=self.user['id'],
            vehicle_name=name,
            track_width=track_width,
            inside_tire_circumference=tire_circ,
            vehicle_type=vehicle_type
        )

        if success:
            messagebox.showinfo("Success", message)

            # Call callback if provided (to refresh dropdowns and lists)
            if self.callback:
                self.callback()

            self.close_window()
        else:
            messagebox.showerror("Error", message)

    def create_widgets(self):
        # Title
        title_frame = ttk.Frame(self.window)
        title_frame.pack(pady=15)

        title_label = tk.Label(
            title_frame,
            text=f"Edit Vehicle - {self.vehicle_name}",
            font=("Arial", 14, "bold"),
            fg="#2E86AB"
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text=f"Team: {self.user['team_name']}",
            font=("Arial", 9),
            fg="#666666"
        )
        subtitle_label.pack(pady=(5, 0))

        # Main form frame
        form_frame = ttk.LabelFrame(self.window, text="Vehicle Information", padding=15)
        form_frame.pack(fill='x', padx=20, pady=(10, 15))

        # Configure grid weights for better layout
        form_frame.grid_columnconfigure(1, weight=1)

        # Vehicle Name
        ttk.Label(form_frame, text="Vehicle Name:", font=("Arial", 10)).grid(row=0, column=0, sticky='w', pady=8)
        self.vehicle_name_entry = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.vehicle_name_entry.grid(row=0, column=1, pady=8, padx=(10, 0), sticky='ew')

        # Vehicle Type
        ttk.Label(form_frame, text="Vehicle Type:", font=("Arial", 10)).grid(row=1, column=0, sticky='w', pady=8)
        self.vehicle_type_var = tk.StringVar(value="Stock Car")
        self.vehicle_type_combo = ttk.Combobox(form_frame, textvariable=self.vehicle_type_var,
                                               values=["Stock Car", "Modified", "Late Model", "Sprint Car", "Other"],
                                               width=27, font=("Arial", 10))
        self.vehicle_type_combo.grid(row=1, column=1, pady=8, padx=(10, 0), sticky='ew')

        # Track Width
        ttk.Label(form_frame, text="Track Width (inches):", font=("Arial", 10)).grid(row=2, column=0, sticky='w',
                                                                                     pady=8)
        self.track_width_entry = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.track_width_entry.grid(row=2, column=1, pady=8, padx=(10, 0), sticky='ew')

        # Inside Tire Circumference
        ttk.Label(form_frame, text="Inside Tire Circumference (inches):", font=("Arial", 10)).grid(row=3, column=0,
                                                                                                   sticky='w', pady=8)
        self.tire_circ_entry = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.tire_circ_entry.grid(row=3, column=1, pady=8, padx=(10, 0), sticky='ew')

        # Wheelbase (optional) - Note: This might not be in your current DB schema
        ttk.Label(form_frame, text="Wheelbase (inches, optional):", font=("Arial", 10)).grid(row=4, column=0,
                                                                                             sticky='w', pady=8)
        self.wheelbase_entry = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.wheelbase_entry.grid(row=4, column=1, pady=8, padx=(10, 0), sticky='ew')

        # Weight (optional) - Note: This might not be in your current DB schema
        ttk.Label(form_frame, text="Weight (lbs, optional):", font=("Arial", 10)).grid(row=5, column=0, sticky='w',
                                                                                       pady=8)
        self.weight_entry = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.weight_entry.grid(row=5, column=1, pady=8, padx=(10, 0), sticky='ew')

        # Notes
        ttk.Label(form_frame, text="Notes:", font=("Arial", 10)).grid(row=6, column=0, sticky='nw', pady=8)

        # Create frame for text widget with scrollbar
        text_frame = ttk.Frame(form_frame)
        text_frame.grid(row=6, column=1, pady=8, padx=(10, 0), sticky='ew')

        self.notes_text = tk.Text(text_frame, width=30, height=3, font=("Arial", 10))
        notes_scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=notes_scrollbar.set)

        self.notes_text.pack(side='left', fill='both', expand=True)
        notes_scrollbar.pack(side='right', fill='y')

        # Button frame
        button_frame = ttk.Frame(self.window)
        button_frame.pack(pady=20, padx=20)

        # Update button
        update_button = ttk.Button(
            button_frame,
            text="💾 Update Vehicle",
            command=self.update_vehicle,
            width=20
        )
        update_button.pack(side='left', padx=10)

        # Cancel button
        cancel_button = ttk.Button(
            button_frame,
            text="❌ Cancel",
            command=self.close_window,
            width=20
        )
        cancel_button.pack(side='left', padx=10)

        # Bind Enter key to update
        self.window.bind('<Return>', lambda e: self.update_vehicle())
        self.window.bind('<Escape>', lambda e: self.close_window())

    def populate_form(self):
        """Populate the form with current vehicle data"""
        if not self.original_vehicle_data:
            return

        # Clear any existing data
        self.vehicle_name_entry.delete(0, tk.END)
        self.track_width_entry.delete(0, tk.END)
        self.tire_circ_entry.delete(0, tk.END)
        self.wheelbase_entry.delete(0, tk.END)
        self.weight_entry.delete(0, tk.END)
        self.notes_text.delete("1.0", tk.END)

        # Populate with current data
        self.vehicle_name_entry.insert(0, self.original_vehicle_data['name'])
        self.vehicle_type_var.set(self.original_vehicle_data['vehicle_type'])

        if self.original_vehicle_data['track_width'] is not None:
            self.track_width_entry.insert(0, str(self.original_vehicle_data['track_width']))

        if self.original_vehicle_data['inside_tire_circumference'] is not None:
            self.tire_circ_entry.insert(0, str(self.original_vehicle_data['inside_tire_circumference']))

    def validate_inputs(self):
        """Validate input fields"""
        errors = []

        # Vehicle name is required
        name = self.vehicle_name_entry.get().strip()
        if not name:
            errors.append("Vehicle name is required")

        # Check if name changed and if new name already exists
        if name != self.original_vehicle_data['name']:
            vehicles = self.db.get_user_vehicles(self.user['id'])
            existing_names = [vehicle[0] for vehicle in vehicles]
            if name in existing_names:
                errors.append("A vehicle with this name already exists")

        # Optional field validation
        track_width_str = self.track_width_entry.get().strip()
        if track_width_str:
            try:
                track_width = float(track_width_str)
                if track_width <= 0:
                    errors.append("Track width must be a positive number")
                elif track_width > 100:
                    errors.append("Track width seems unrealistic (>100 inches)")
            except ValueError:
                errors.append("Track width must be a valid number")

        tire_circ_str = self.tire_circ_entry.get().strip()
        if tire_circ_str:
            try:
                tire_circ = float(tire_circ_str)
                if tire_circ <= 0:
                    errors.append("Tire circumference must be a positive number")
                elif tire_circ < 60 or tire_circ > 120:
                    errors.append("Tire circumference seems unrealistic (should be 60-120 inches)")
            except ValueError:
                errors.append("Tire circumference must be a valid number")

        wheelbase_str = self.wheelbase_entry.get().strip()
        if wheelbase_str:
            try:
                wheelbase = float(wheelbase_str)
                if wheelbase <= 0:
                    errors.append("Wheelbase must be a positive number")
            except ValueError:
                errors.append("Wheelbase must be a valid number")

        weight_str = self.weight_entry.get().strip()
        if weight_str:
            try:
                weight = float(weight_str)
                if weight <= 0:
                    errors.append("Weight must be a positive number")
            except ValueError:
                errors.append("Weight must be a valid number")

        return errors

    def update_vehicle(self):
        """Update the vehicle in database"""
        # Validate inputs
        errors = self.validate_inputs()
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return

        # Get values
        name = self.vehicle_name_entry.get().strip()
        vehicle_type = self.vehicle_type_var.get()

        # Optional values
        track_width_str = self.track_width_entry.get().strip()
        track_width = float(track_width_str) if track_width_str else None

        tire_circ_str = self.tire_circ_entry.get().strip()
        tire_circ = float(tire_circ_str) if tire_circ_str else None

        wheelbase_str = self.wheelbase_entry.get().strip()
        wheelbase = float(wheelbase_str) if wheelbase_str else None

        weight_str = self.weight_entry.get().strip()
        weight = float(weight_str) if weight_str else None

        notes = self.notes_text.get("1.0", tk.END).strip()

        # Update in database
        try:
            conn = sqlite3.connect(self.db.db_name, timeout=10.0)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE vehicles 
                SET vehicle_name = ?, track_width = ?, inside_tire_circumference = ?, vehicle_type = ?
                WHERE id = ? AND user_id = ?
            ''', (name, track_width, tire_circ, vehicle_type, self.original_vehicle_data['id'], self.user['id']))

            conn.commit()
            conn.close()

            # Show success message
            messagebox.showinfo("Success", f"Vehicle '{name}' updated successfully!")

            # Call callback if provided (to refresh dropdowns and lists)
            if self.callback:
                self.callback()

            self.close_window()

        except Exception as e:
            messagebox.showerror("Database Error", f"Error updating vehicle: {str(e)}")

    def close_window(self):
        """Close the window"""
        self.window.grab_release()
        self.window.destroy()


# Test the vehicle management window
if __name__ == "__main__":
    import tkinter as tk
    from staggerDB import StaggerDatabase

    # Create test setup
    root = tk.Tk()
    root.title("Vehicle Management Test")
    root.geometry("300x200")

    # Test database and user
    db = StaggerDatabase("test_vehicles.db")
    test_user = {'id': 1, 'username': 'testuser', 'team_name': 'Test Racing Team'}

    # Create vehicle manager
    vm = VehicleManager(db, test_user)

    # Test button
    def test_add_vehicle():
        vm.show_add_vehicle_window(root, lambda: print("Vehicle added callback!"))

    test_button = tk.Button(root, text="Test Add Vehicle", command=test_add_vehicle)
    test_button.pack(pady=50)

    root.mainloop()