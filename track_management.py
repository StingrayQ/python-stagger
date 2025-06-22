import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3


class AddTrackWindow:
    def __init__(self, parent, db, user, callback=None):
        self.db = db
        self.user = user
        self.callback = callback

        # Create popup window
        self.window = tk.Toplevel(parent)
        self.window.title("Add New Track")
        self.window.geometry("500x450")
        self.window.resizable(False, False)

        # Make it modal
        self.window.transient(parent)
        self.window.grab_set()

        # Center the window
        self.center_window()

        # Create the interface
        self.create_widgets()

        # Focus on first entry
        self.track_name_entry.focus()

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
            text="Add New Track",
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
        form_frame = ttk.LabelFrame(self.window, text="Track Information", padding=15)
        form_frame.pack(fill='x', padx=20, pady=(10, 15))

        # Configure grid weights for better layout
        form_frame.grid_columnconfigure(1, weight=1)

        # Track Name
        ttk.Label(form_frame, text="Track Name:", font=("Arial", 10)).grid(row=0, column=0, sticky='w', pady=8)
        self.track_name_entry = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.track_name_entry.grid(row=0, column=1, pady=8, padx=(10, 0), sticky='ew')

        # Corner Length
        ttk.Label(form_frame, text="Corner Length (feet, optional):", font=("Arial", 10)).grid(row=1, column=0,
                                                                                               sticky='w', pady=8)
        self.corner_length_entry = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.corner_length_entry.grid(row=1, column=1, pady=8, padx=(10, 0), sticky='ew')

        # Banking
        ttk.Label(form_frame, text="Banking (degrees, optional):", font=("Arial", 10)).grid(row=2, column=0, sticky='w',
                                                                                            pady=8)
        self.banking_entry = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.banking_entry.grid(row=2, column=1, pady=8, padx=(10, 0), sticky='ew')

        # Surface Type
        ttk.Label(form_frame, text="Surface Type:", font=("Arial", 10)).grid(row=3, column=0, sticky='w', pady=8)
        self.surface_type_var = tk.StringVar(value="asphalt")
        self.surface_type_combo = ttk.Combobox(form_frame, textvariable=self.surface_type_var,
                                               values=["asphalt", "concrete", "dirt", "clay", "other"],
                                               width=27, font=("Arial", 10))
        self.surface_type_combo.grid(row=3, column=1, pady=8, padx=(10, 0), sticky='ew')

        # Notes
        ttk.Label(form_frame, text="Notes:", font=("Arial", 10)).grid(row=4, column=0, sticky='nw', pady=8)

        # Create frame for text widget with scrollbar
        text_frame = ttk.Frame(form_frame)
        text_frame.grid(row=4, column=1, pady=8, padx=(10, 0), sticky='ew')

        self.notes_text = tk.Text(text_frame, width=30, height=3, font=("Arial", 10))
        notes_scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=notes_scrollbar.set)

        self.notes_text.pack(side='left', fill='both', expand=True)
        notes_scrollbar.pack(side='right', fill='y')

        # Button frame
        button_frame = ttk.Frame(self.window)
        button_frame.pack(pady=20, padx=20)

        # Save button
        save_button = ttk.Button(
            button_frame,
            text="💾 Save Track",
            command=self.save_track,
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
        self.window.bind('<Return>', lambda e: self.save_track())
        self.window.bind('<Escape>', lambda e: self.close_window())

        # Add placeholders
        self.add_placeholders()

    def add_placeholders(self):
        """Add placeholder text to help users"""
        self.track_name_entry.insert(0, "e.g., Bristol Motor Speedway")
        self.corner_length_entry.insert(0, "e.g., 200")
        self.banking_entry.insert(0, "e.g., 12.5")

        # Clear placeholders when user clicks
        def clear_placeholder(entry, placeholder):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)

        def restore_placeholder(entry, placeholder):
            if not entry.get():
                entry.insert(0, placeholder)

        placeholders = [
            (self.track_name_entry, "e.g., Bristol Motor Speedway"),
            (self.corner_length_entry, "e.g., 200"),
            (self.banking_entry, "e.g., 12.5")
        ]

        for entry, placeholder in placeholders:
            entry.bind('<FocusIn>', lambda e, ent=entry, ph=placeholder: clear_placeholder(ent, ph))
            entry.bind('<FocusOut>', lambda e, ent=entry, ph=placeholder: restore_placeholder(ent, ph))

    def validate_inputs(self):
        """Validate input fields"""
        errors = []

        # Track name is required
        name = self.track_name_entry.get().strip()
        if not name or name == "e.g., Bristol Motor Speedway":
            errors.append("Track name is required")

        # Optional field validation
        corner_length_str = self.corner_length_entry.get().strip()
        if corner_length_str and corner_length_str != "e.g., 200":
            try:
                corner_length = float(corner_length_str)
                if corner_length <= 0:
                    errors.append("Corner length must be a positive number")
                elif corner_length > 5000:  # Reasonable limit
                    errors.append("Corner length seems unrealistic (>5000 feet)")
            except ValueError:
                errors.append("Corner length must be a valid number")

        banking_str = self.banking_entry.get().strip()
        if banking_str and banking_str != "e.g., 12.5":
            try:
                banking = float(banking_str)
                if banking < 0 or banking > 90:
                    errors.append("Banking must be between 0 and 90 degrees")
            except ValueError:
                errors.append("Banking must be a valid number")

        return errors

    def save_track(self):
        """Save the track to database"""
        # Validate inputs
        errors = self.validate_inputs()
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return

        # Get values
        name = self.track_name_entry.get().strip()
        surface_type = self.surface_type_var.get()

        # Optional values
        corner_length_str = self.corner_length_entry.get().strip()
        corner_length = float(corner_length_str) if corner_length_str and corner_length_str != "e.g., 200" else None

        banking_str = self.banking_entry.get().strip()
        banking = float(banking_str) if banking_str and banking_str != "e.g., 12.5" else None

        notes = self.notes_text.get("1.0", tk.END).strip()

        # Save to database
        success, message = self.db.save_track(
            track_name=name,
            corner_length_ft=corner_length,
            banking_degrees=banking,
            surface_type=surface_type,
            user_id=self.user['id']
        )

        if success:
            # Show what was saved
            saved_info = f"Track '{name}' saved successfully!\n\nSaved information:"
            saved_info += f"\n• Surface Type: {surface_type}"
            if corner_length:
                saved_info += f"\n• Corner Length: {corner_length} feet"
            if banking:
                saved_info += f"\n• Banking: {banking}°"
            if notes:
                saved_info += f"\n• Notes: {notes}"

            messagebox.showinfo("Success", saved_info)

            # Call callback if provided
            if self.callback:
                self.callback()
                self.close_window()
        else:
            messagebox.showerror("Error", message)

    def close_window(self):
        """Close the window"""
        self.window.grab_release()
        self.window.destroy()


class EditTrackWindow:
    def __init__(self, parent, db, user, track_name, callback=None):
        self.db = db
        self.user = user
        self.track_name = track_name
        self.callback = callback
        self.original_track_data = None

        # Create popup window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Edit Track - {track_name}")
        self.window.geometry("500x400")
        self.window.resizable(False, False)

        # Make it modal
        self.window.transient(parent)
        self.window.grab_set()

        # Center the window
        self.center_window()

        # Load the current track data
        self.load_track_data()

        # Create the interface
        self.create_widgets()

        # Populate the form with current data
        self.populate_form()

        # Focus on first entry
        self.track_name_entry.focus()

    def center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def load_track_data(self):
        """Load the current track data from database"""
        try:
            track_id = self.db.get_track_id_by_name(self.user['id'], self.track_name)
            if not track_id:
                messagebox.showerror("Error", f"Track '{self.track_name}' not found!")
                self.close_window()
                return

            track_data = self.db.get_track_by_id(track_id, self.user['id'])
            if track_data:
                self.original_track_data = {
                    'id': track_data[0],
                    'name': track_data[1],
                    'corner_length_ft': track_data[2],
                    'banking_degrees': track_data[3],
                    'surface_type': track_data[4],
                    'created_date': track_data[5]
                }
            else:
                messagebox.showerror("Error", f"Track '{self.track_name}' not found!")
                self.close_window()

        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading track data: {str(e)}")
            self.close_window()

    def create_widgets(self):
        # Title
        title_frame = ttk.Frame(self.window)
        title_frame.pack(pady=15)

        title_label = tk.Label(
            title_frame,
            text=f"Edit Track - {self.track_name}",
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
        form_frame = ttk.LabelFrame(self.window, text="Track Information", padding=15)
        form_frame.pack(fill='x', padx=20, pady=(10, 15))

        # Configure grid weights for better layout
        form_frame.grid_columnconfigure(1, weight=1)

        # Track Name
        ttk.Label(form_frame, text="Track Name:", font=("Arial", 10)).grid(row=0, column=0, sticky='w', pady=8)
        self.track_name_entry = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.track_name_entry.grid(row=0, column=1, pady=8, padx=(10, 0), sticky='ew')

        # Corner Length
        ttk.Label(form_frame, text="Corner Length (feet, optional):", font=("Arial", 10)).grid(row=1, column=0,
                                                                                               sticky='w', pady=8)
        self.corner_length_entry = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.corner_length_entry.grid(row=1, column=1, pady=8, padx=(10, 0), sticky='ew')

        # Banking
        ttk.Label(form_frame, text="Banking (degrees, optional):", font=("Arial", 10)).grid(row=2, column=0, sticky='w',
                                                                                            pady=8)
        self.banking_entry = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.banking_entry.grid(row=2, column=1, pady=8, padx=(10, 0), sticky='ew')

        # Surface Type
        ttk.Label(form_frame, text="Surface Type:", font=("Arial", 10)).grid(row=3, column=0, sticky='w', pady=8)
        self.surface_type_var = tk.StringVar(value="asphalt")
        self.surface_type_combo = ttk.Combobox(form_frame, textvariable=self.surface_type_var,
                                               values=["asphalt", "concrete", "dirt", "clay", "other"],
                                               width=27, font=("Arial", 10))
        self.surface_type_combo.grid(row=3, column=1, pady=8, padx=(10, 0), sticky='ew')

        # Notes
        ttk.Label(form_frame, text="Notes:", font=("Arial", 10)).grid(row=4, column=0, sticky='nw', pady=8)

        # Create frame for text widget with scrollbar
        text_frame = ttk.Frame(form_frame)
        text_frame.grid(row=4, column=1, pady=8, padx=(10, 0), sticky='ew')

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
            text="💾 Update Track",
            command=self.update_track,
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
        self.window.bind('<Return>', lambda e: self.update_track())
        self.window.bind('<Escape>', lambda e: self.close_window())

    def populate_form(self):

        if not self.original_track_data:
            return

        # Clear any existing data
        self.track_name_entry.delete(0, tk.END)
        self.corner_length_entry.delete(0, tk.END)
        self.banking_entry.delete(0, tk.END)
        self.notes_text.delete("1.0", tk.END)

        # Populate with current data
        self.track_name_entry.insert(0, self.original_track_data['name'])
        self.surface_type_var.set(self.original_track_data['surface_type'])

        if self.original_track_data['corner_length_ft'] is not None:
            self.corner_length_entry.insert(0, str(self.original_track_data['corner_length_ft']))

        if self.original_track_data['banking_degrees'] is not None:
            self.banking_entry.insert(0, str(self.original_track_data['banking_degrees']))

    def validate_inputs(self):

        errors = []

        # Track name is required
        name = self.track_name_entry.get().strip()
        if not name:
            errors.append("Track name is required")

        # Check if name changed and if new name already exists
        if name != self.original_track_data['name']:
            tracks = self.db.get_user_tracks(self.user['id'])
            existing_names = [track[0] for track in tracks]
            if name in existing_names:
                errors.append("A track with this name already exists")

        # Optional field validation
        corner_length_str = self.corner_length_entry.get().strip()
        if corner_length_str:
            try:
                corner_length = float(corner_length_str)
                if corner_length <= 0:
                    errors.append("Corner length must be a positive number")
                # elif corner_length > 5000:
                #     errors.append("Corner length seems unrealistic (>5000 feet)")
            except ValueError:
                errors.append("Corner length must be a valid number")

        banking_str = self.banking_entry.get().strip()
        if banking_str:
            try:
                banking = float(banking_str)
                if banking < 0 or banking > 90:
                    errors.append("Banking must be between 0 and 90 degrees")
            except ValueError:
                errors.append("Banking must be a valid number")

        return errors

    def update_track(self):

        # Validate inputs
        errors = self.validate_inputs()
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return

        # Get values
        name = self.track_name_entry.get().strip()
        surface_type = self.surface_type_var.get()

        # Optional values
        corner_length_str = self.corner_length_entry.get().strip()
        corner_length = float(corner_length_str) if corner_length_str else None

        banking_str = self.banking_entry.get().strip()
        banking = float(banking_str) if banking_str else None

        # Use the database method to update
        success, message = self.db.update_track(
            track_id=self.original_track_data['id'],
            user_id=self.user['id'],
            track_name=name,
            corner_length_ft=corner_length,
            banking_degrees=banking,
            surface_type=surface_type
        )

        if success:
            messagebox.showinfo("Success", message)

            # Call callback if provided
            if self.callback:
                self.callback()

            self.close_window()
        else:
            messagebox.showerror("Error", message)

    def close_window(self):

        self.window.grab_release()
        self.window.destroy()


class TrackManagementWindow:


    def __init__(self, parent, db, user, callback=None):
        self.db = db
        self.user = user
        self.callback = callback

        # Create popup window
        self.window = tk.Toplevel(parent)
        self.window.title("Manage Tracks")
        self.window.geometry("800x600")
        self.window.resizable(True, True)

        # Make it modal
        self.window.transient(parent)
        self.window.grab_set()

        # Center the window
        self.center_window()

        # Create the interface
        self.create_widgets()

        # Load tracks
        self.refresh_track_list()

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
        title_frame.pack(pady=15, fill='x')

        title_label = tk.Label(
            title_frame,
            text="Manage Tracks",
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

        # Track list frame
        list_frame = ttk.LabelFrame(content_frame, text="Your Tracks", padding=10)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))

        # Create treeview for track list
        columns = ('Name', 'Corner Length', 'Banking', 'Surface', 'Created')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)

        # Define column headings and widths
        column_widths = {
            'Name': 200,
            'Corner Length': 120,
            'Banking': 100,
            'Surface': 100,
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

        # Add Track button
        add_button = ttk.Button(
            button_frame,
            text="➕ Add New Track",
            command=self.add_new_track,
            width=20
        )
        add_button.pack(side='left', padx=(0, 10))

        # Edit Track button
        edit_button = ttk.Button(
            button_frame,
            text="✏️ Edit Selected",
            command=self.edit_selected_track,
            width=20
        )
        edit_button.pack(side='left', padx=(0, 10))

        # Delete Track button
        delete_button = ttk.Button(
            button_frame,
            text="🗑️ Delete Selected",
            command=self.delete_selected_track,
            width=20
        )
        delete_button.pack(side='left', padx=(0, 10))

        # Refresh button
        refresh_button = ttk.Button(
            button_frame,
            text="🔄 Refresh",
            command=self.refresh_track_list,
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
        self.tree.bind('<Double-1>', lambda e: self.edit_selected_track())

    def refresh_track_list(self):

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get tracks from database
        tracks = self.db.get_user_tracks(self.user['id'])

        # Add tracks to tree
        for track in tracks:
            # track format: (name, corner_length_ft, banking_degrees, surface_type, created_date)
            name = track[0]
            corner_length = f"{track[1]} ft" if track[1] is not None else "Not set"
            banking = f"{track[2]}°" if track[2] is not None else "Not set"
            surface = track[3] if track[3] else "Unknown"
            created_date = track[4][:10] if len(track) > 4 and track[4] else "Unknown"

            self.tree.insert('', 'end', values=(name, corner_length, banking, surface, created_date))

        # Update status
        count = len(tracks)
        self.status_label.config(text=f"Showing {count} track{'s' if count != 1 else ''}")

    def add_new_track(self):

        AddTrackWindow(self.window, self.db, self.user, self.on_track_changed)

    def edit_selected_track(self):

        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a track to edit.")
            return

        # Get selected track data
        item = self.tree.item(selection[0])
        track_name = item['values'][0]

        # Open edit window
        EditTrackWindow(self.window, self.db, self.user, track_name, self.on_track_changed)

    def delete_selected_track(self):

        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a track to delete.")
            return

        # Get selected track data
        item = self.tree.item(selection[0])
        track_name = item['values'][0]

        # Confirm deletion
        response = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete '{track_name}'?\n\nThis action cannot be undone."
        )

        if response:
            # Get track ID and delete it
            track_id = self.db.get_track_id_by_name(self.user['id'], track_name)
            if track_id:
                success, message = self.db.delete_track(self.user['id'], track_id)
                if success:
                    messagebox.showinfo("Success", f"Track '{track_name}' deleted successfully!")
                    self.refresh_track_list()
                    self.on_track_changed()
                else:
                    messagebox.showerror("Error", f"Failed to delete track: {message}")
            else:
                messagebox.showerror("Error", f"Track '{track_name}' not found!")

    def on_track_changed(self):

        if self.callback:
            self.callback()

    def close_window(self):

        self.window.grab_release()
        self.window.destroy()


class TrackManager:


    def __init__(self, db, user):
        self.db = db
        self.user = user

    def show_add_track_window(self, parent, callback=None):

        AddTrackWindow(parent, self.db, self.user, callback)

    def show_manage_tracks_window(self, parent, callback=None):

        TrackManagementWindow(parent, self.db, self.user, callback)

    def get_user_tracks(self):

        return self.db.get_user_tracks(self.user['id'])

    def get_track_by_name(self, track_name):

        tracks = self.get_user_tracks()
        for track in tracks:
            if track[0] == track_name:  # track_name is at index 0
                return {
                    'name': track[0],
                    'corner_length_ft': track[1] if track[1] is not None else None,
                    'banking_degrees': track[2] if track[2] is not None else None,
                    'surface_type': track[3]
                }
        return None