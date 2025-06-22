import math
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from vehicle_management import VehicleManager
from track_management import TrackManager



def add_vehicle(self):

    self.vehicle_manager.show_add_vehicle_window(self.root, self.update_vehicle_dropdown)


def manage_vehicles(self):

    self.vehicle_manager.show_manage_vehicles_window(self.root, self.update_vehicle_dropdown)








class StaggerCalculatorGUI:


    def __init__(self, user, db, logout_callback):

        self.user = user
        self.db = db
        self.logout_callback = logout_callback
        self.last_calculation = {}

        # Initialize vehicle manager
        self.vehicle_manager = VehicleManager(db, user)

        # initialize track manager
        self.track_manager = TrackManager(db, user)

        # Create main window
        self.root = Tk()
        self.root.title(f"Stagger Calculator - {user['username']} ({user['team_name']})")
        self.root.geometry("550x600")

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # Create the interface
        self.create_widgets()

        # Import calculation module with reference to this GUI
        import calculation
        calculation.set_gui_reference(self)

        # Load initial vehicle dropdown data
        self.update_vehicle_dropdown()

        # Load initial track dropdown data
        self.update_track_dropdown()


    def create_widgets(self):


        # Import calculation module
        import calculation

        ############## Menu Bar ############
        menubar = Menu(self.root)

        # File menu
        file = Menu(menubar, tearoff=0)
        file.add_command(label='Logout', command=self.handle_logout)
        file.add_separator()
        file.add_command(label='Exit', command=self.on_window_close)
        menubar.add_cascade(label='File', menu=file)

        # Vehicles menu
        vehicles = Menu(menubar, tearoff=0)
        vehicles.add_command(label='Add Vehicle', command=self.add_vehicle)
        vehicles.add_separator()
        vehicles.add_command(label='Manage Vehicles', command=self.manage_vehicles)
        menubar.add_cascade(label='Vehicles', menu=vehicles)

        # Tracks menu
        tracks = Menu(menubar, tearoff=0)
        tracks.add_command(label='Add Track', command=self.add_track)
        tracks.add_separator()
        tracks.add_command(label='Manage Tracks', command=self.manage_tracks)
        menubar.add_cascade(label='Tracks', menu=tracks)

        # Data menu
        data = Menu(menubar, tearoff=0)
        data.add_command(label='Stagger Data', command=calculation.show_history)
        menubar.add_cascade(label='Data', menu=data)

        self.root.config(menu=menubar)

        ############## Main Interface ############

        # Spacing
        spaceLabel = Label(self.root, text="")
        spaceLabel.grid(row=0, column=0, pady=10)

        # Vehicle Selection Section
        vehicle_frame = ttk.LabelFrame(self.root, text="Vehicle Selection", padding=5)
        vehicle_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=10, pady=5)

        ttk.Label(vehicle_frame, text="Select Vehicle:").grid(row=0, column=0, sticky='w', padx=5)

        # Create the StringVar and dropdown
        self.vehicle_var = StringVar(value="Manual Entry")
        self.vehicle_dropdown = ttk.Combobox(vehicle_frame, textvariable=self.vehicle_var,
                                             width=25, state="readonly")
        self.vehicle_dropdown.grid(row=0, column=1, padx=5, pady=5)

        # Set initial values
        self.vehicle_dropdown['values'] = ["Manual Entry"]

        # Add the trace
        self.vehicle_dropdown.bind('<<ComboboxSelected>>', self.on_vehicle_changed)

        # Track Selection
        track_frame = ttk.LabelFrame(self.root, text="Track Selection", padding=5)
        track_frame.grid(row=2, column=0, columnspan=4, sticky="ew", padx=10, pady=5)

        ttk.Label(track_frame, text="Select Track:").grid(row=0, column=0, sticky='w', padx=5)

        # StringVar and dropdown for tracks
        self.track_var = StringVar(value="Manual Entry")
        self.track_dropdown = ttk.Combobox(track_frame, textvariable=self.track_var,
                                           width=25, state="readonly")
        self.track_dropdown.grid(row=0, column=1, padx=5, pady=5)

        # Set initial values
        self.track_dropdown['values'] = ["Manual Entry"]

        # Add the trace for track selection
        self.track_dropdown.bind('<<ComboboxSelected>>', self.on_track_changed)




        # Track Width
        trackWidthLabel = Label(self.root, text="Track Width (inches)")
        trackWidthLabel.grid(row=3, column=0, sticky='w', padx=10, pady=5)
        self.twEntry = ttk.Entry(self.root, width=15)
        self.twEntry.grid(row=3, column=1, padx=10, pady=5)

        # Corner Length
        CornerlgthLabel = Label(self.root, text="Corner length (in feet)")
        CornerlgthLabel.grid(row=4, column=0, sticky='w', padx=10, pady=5)
        self.Cornerlengthentry = ttk.Entry(self.root, width=15)
        self.Cornerlengthentry.grid(row=4, column=1, padx=10, pady=5)

        # Tire Circumference
        CircumferenceInsideLabel = Label(self.root, text="Circumference of inside tire (in inches)")
        CircumferenceInsideLabel.grid(row=5, column=0, sticky='w', padx=10, pady=5)
        self.CircumferenceInsideentry = ttk.Entry(self.root, width=15)
        self.CircumferenceInsideentry.grid(row=5, column=1, padx=10, pady=5)

        # Banking
        bankingLabel = Label(self.root, text="Track Banking (in degrees)")
        bankingLabel.grid(row=6, column=0, sticky='w', padx=10, pady=5)
        self.banking_entry = ttk.Entry(self.root, width=15, state='disabled')
        self.banking_entry.grid(row=6, column=1, padx=10, pady=5)


        self.Bank = IntVar(value=0)
        self.Bank.set(0)

        # Bankingbutton = Checkbutton(self.root, text="Has Banking", variable=self.Bank, command=self.toggle_banking)
        self.banking_checkbox = Checkbutton(self.root, text="Has Banking", command=self.toggle_banking)
        self.banking_checkbox.grid(row=6, column=2, sticky='w', padx=10, pady=5)
        # Bankingbutton.grid(row=5, column=2, sticky='w', padx=10, pady=5)

        # Calculate Button
        calcButton = ttk.Button(self.root, text="Calculate Stagger", command=calculation.disp_stagger)
        calcButton.grid(row=7, column=0, columnspan=2, pady=20)

        # Results
        results_frame = ttk.LabelFrame(self.root, text="Results", padding=10)
        results_frame.grid(row=8, column=0, columnspan=4, sticky="ew", padx=10, pady=5)

        StaggerLabel = Label(results_frame, text="Calculated Stagger:")
        StaggerLabel.grid(row=0, column=0, sticky='w', pady=5)
        self.CalcstaggerLabel = Label(results_frame, font="arial 14 bold", fg="blue")
        self.CalcstaggerLabel.grid(row=0, column=1, sticky='w', padx=10, pady=5)

        OutsideTireSizeLabel = Label(results_frame, text="Outside Tire Size:")
        OutsideTireSizeLabel.grid(row=1, column=0, sticky='w', pady=5)
        self.CalcOutterTireLabel = Label(results_frame, font="arial 14 bold", fg="blue")
        self.CalcOutterTireLabel.grid(row=1, column=1, sticky='w', padx=10, pady=5)

        # Database section
        db_frame = ttk.LabelFrame(self.root, text="Save Calculation", padding=10)
        db_frame.grid(row=9, column=0, columnspan=4, sticky="ew", padx=10, pady=5)

        # Notes and save button
        notes_label = Label(db_frame, text="Notes:")
        notes_label.grid(row=0, column=0, sticky='w', pady=2)
        self.notes_entry = ttk.Entry(db_frame, width=30)
        self.notes_entry.grid(row=0, column=1, padx=5, pady=2)

        self.save_button = ttk.Button(db_frame, text="Save Calculation", command=calculation.save_calculation,
                                      state=DISABLED)
        self.save_button.grid(row=0, column=2, padx=10, pady=2)

        # history_button = ttk.Button(db_frame, text="View History", command=calculation.show_history)
        # history_button.grid(row=1, column=0, columnspan=2, pady=10)

    def toggle_banking(self):
        # Manually toggle the value since automatic binding isn't working
        current_value = self.Bank.get()
        new_value = 1 if current_value == 0 else 0
        self.Bank.set(new_value)

        #print(f"Toggled from {current_value} to {new_value}")

        if new_value == 1:
            #print("Enabling banking entry")
            self.banking_entry.config(state='normal')
        else:
            #print("Disabling banking entry")
            self.banking_entry.delete(0, 'end')
            self.banking_entry.config(state='disabled')




    def add_vehicle(self):

        self.vehicle_manager.show_add_vehicle_window(self.root, self.update_vehicle_dropdown)

    def manage_vehicles(self):

        self.vehicle_manager.show_manage_vehicles_window(self.root, self.update_vehicle_dropdown)

    def update_vehicle_dropdown(self):

        print("Updating vehicle dropdown...")
        vehicles = self.vehicle_manager.get_user_vehicles()
        print(f"Found {len(vehicles)} vehicles: {vehicles}")

        vehicle_names = ["Manual Entry"] + [vehicle[0] for vehicle in vehicles]  # vehicle[0] is name
        print(f"Vehicle names for dropdown: {vehicle_names}")

        self.vehicle_dropdown['values'] = vehicle_names

        # If no vehicle selected, default to manual entry
        current_selection = self.vehicle_var.get()
        print(f"Current selection: '{current_selection}'")

        if not current_selection or current_selection not in vehicle_names:
            self.vehicle_var.set("Manual Entry")
            print("Set to Manual Entry")

        print(f"Dropdown values: {self.vehicle_dropdown['values']}")




    def on_vehicle_changed(self, event=None):

        print(f"on_vehicle_changed called with event: {event}")

        # Get the selection directly from the combobox instead of the StringVar
        selected_vehicle = self.vehicle_dropdown.get()
        print(f"Vehicle selected from dropdown.get(): {selected_vehicle}")

        # Also check what the StringVar thinks it is
        stringvar_value = self.vehicle_var.get()
        print(f"StringVar value: {stringvar_value}")

        if selected_vehicle == "Manual Entry":
            # Clear the fields for manual entry
            print("Clearing fields for manual entry")
            self.twEntry.delete(0, END)
            self.CircumferenceInsideentry.delete(0, END)
            self.twEntry.config(state=NORMAL)
            self.CircumferenceInsideentry.config(state=NORMAL)
            print(f"After clearing - track width value: '{self.twEntry.get()}'")
            print("Switched to manual entry mode")
        else:
            # Load vehicle data
            print("Loading vehicle data...")
            vehicle_data = self.vehicle_manager.get_vehicle_by_name(selected_vehicle)
            print(f"Vehicle data retrieved: {vehicle_data}")

            if vehicle_data:
                # Clear fields first
                print("Clearing fields before loading vehicle data")
                self.twEntry.delete(0, END)
                self.CircumferenceInsideentry.delete(0, END)
                print(f"After clearing - track width value: '{self.twEntry.get()}'")

                # Enable fields to allow editing
                self.twEntry.config(state=NORMAL)
                self.CircumferenceInsideentry.config(state=NORMAL)

                # Fill in available data
                if vehicle_data['track_width']:
                    print(f"About to insert track width: {vehicle_data['track_width']}")
                    print(f"Track width entry state before: {self.twEntry['state']}")

                    self.twEntry.insert(0, str(vehicle_data['track_width']))

                    print(f"Track width entry value after insert: '{self.twEntry.get()}'")
                    print(f"Track width entry state after: {self.twEntry['state']}")
                    print(f"Inserted track width: {vehicle_data['track_width']}")

                print("Vehicle loading completed")
            else:
                print("No vehicle data found!")

    def add_track(self):

        self.track_manager.show_add_track_window(self.root, self.update_track_dropdown)

    def manage_tracks(self):

        self.track_manager.show_manage_tracks_window(self.root, self.update_track_dropdown)

    def update_track_dropdown(self):
        """Update track dropdown with saved tracks"""
        print("Updating track dropdown...")
        tracks = self.track_manager.get_user_tracks()
        print(f"Found {len(tracks)} tracks: {tracks}")

        track_names = ["Manual Entry"] + [track[0] for track in tracks]  # track[0] is name
        print(f"Track names for dropdown: {track_names}")

        self.track_dropdown['values'] = track_names

        # If no track selected, default to manual entry
        current_selection = self.track_var.get()
        print(f"Current track selection: '{current_selection}'")

        if not current_selection or current_selection not in track_names:
            self.track_var.set("Manual Entry")
            print("Set track to Manual Entry")

        print(f"Track dropdown values: {self.track_dropdown['values']}")

    def on_track_changed(self, event=None):
        """Handle track selection from dropdown"""
        print(f"on_track_changed called with event: {event}")

        # Get the selection directly from the combobox
        selected_track = self.track_dropdown.get()
        print(f"Track selected from dropdown.get(): {selected_track}")

        # Also check what the StringVar thinks it is
        stringvar_value = self.track_var.get()
        print(f"Track StringVar value: {stringvar_value}")

        if selected_track == "Manual Entry":
            # Clear the fields for manual entry
            print("Clearing track fields for manual entry")
            self.Cornerlengthentry.delete(0, END)
            self.banking_entry.delete(0, END)
            self.banking_checkbox.deselect()
            self.Bank.set(0)
            self.banking_entry.config(state='disabled')

            # Enable fields for manual entry
            self.Cornerlengthentry.config(state=NORMAL)
            print("Switched to manual track entry mode")
        else:
            # Load track data
            print("Loading track data...")
            track_data = self.track_manager.get_track_by_name(selected_track)
            print(f"Track data retrieved: {track_data}")

            if track_data:
                # Clear fields first
                print("Clearing fields before loading track data")
                self.Cornerlengthentry.delete(0, END)
                self.banking_entry.delete(0, END)

                # Enable fields to allow editing
                self.Cornerlengthentry.config(state=NORMAL)

                # Fill in available data
                if track_data['corner_length_ft']:
                    print(f"About to insert corner length: {track_data['corner_length_ft']}")
                    self.Cornerlengthentry.insert(0, str(track_data['corner_length_ft']))
                    print(f"Inserted corner length: {track_data['corner_length_ft']}")

                if track_data['banking_degrees'] is not None and track_data['banking_degrees'] > 0:
                    print(f"About to insert banking: {track_data['banking_degrees']}")
                    self.banking_checkbox.select()
                    self.Bank.set(1)
                    self.banking_entry.config(state='normal')
                    self.banking_entry.insert(0, str(track_data['banking_degrees']))
                    print(f"Inserted banking: {track_data['banking_degrees']}")
                else:
                    # No banking or 0 banking
                    self.banking_checkbox.deselect()
                    self.Bank.set(0)
                    self.banking_entry.config(state='disabled')

                print("Track loading completed")
            else:
                print("No track data found!")

    def handle_logout(self):
        """Handle user logout"""
        response = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if response:
            self.root.destroy()
            self.logout_callback()

    def on_window_close(self):
        """Handle window close event"""
        response = messagebox.askyesno("Exit", "Are you sure you want to exit?")
        if response:
            self.root.destroy()
            self.logout_callback()

    def destroy(self):
        """Destroy the window"""
        if self.root:
            self.root.quit()
            self.root.destroy()


# For backward compatibility during testing
if __name__ == "__main__":
    # Test mode - create dummy user and database
    print("Running stagger_gui.py in test mode...")

    from staggerDB import StaggerDatabase

    dummy_user = {
        'id': 1,
        'username': 'testuser',
        'team_name': 'Test Team'
    }

    dummy_db = StaggerDatabase("test.db")


    def dummy_logout():
        print("Logout callback called")


    app = StaggerCalculatorGUI(dummy_user, dummy_db, dummy_logout)



















# import math
# from tkinter import *
# from tkinter import ttk
# from tkinter import messagebox
#
# import staggerDB
# import calculation
#
# root = Tk()
# root.title("Stagger Calculator")
#
# ############## GUI Setup ############
#
# # Creating Menubar
# menubar = Menu(root)
# file = Menu(menubar, tearoff=0)
# file.add_command(label='Exit', command=root.destroy)
# menubar.add_cascade(label='File', menu=file)
#
# vehicles = Menu(menubar, tearoff=0)
# tracks= Menu(menubar, tearoff=0)
# data= Menu(menubar, tearoff=0)
#
# menubar.add_cascade(label='Vehicles', menu=vehicles)
# vehicles.add_command(label='Add Vehicle', command=None)
# vehicles.add_separator()
#
# menubar.add_cascade(label='Tracks', menu=tracks)
# tracks.add_command(label='Add Track', command=None)
# tracks.add_separator()
#
# menubar.add_cascade(label='Data', menu=data)
# data.add_command(label='Stagger Data', command=calculation.show_history)
# data.add_separator()
#
#
# spaceLabel = Label(root, text="")
# spaceLabel.grid(row=0, column=0, pady=10)
#
# trackWidthLabel = Label(root, text="Track Width")
# trackWidthLabel.grid(row=1, column=0)
# twEntry = ttk.Entry(root, width=10)
# twEntry.grid(row=1, column=1, padx=10, pady=5)
#
# CornerlgthLabel = Label(root, text="Corner length (in feet)")
# CornerlgthLabel.grid(row=2, column=0, pady=5)
# Cornerlengthentry = ttk.Entry(root, width=10)
# Cornerlengthentry.grid(row=2, column=1, pady=5)
#
# CircumferenceInsideLabel = Label(root, text="Circumference of inside tire (in inches) ")
# CircumferenceInsideLabel.grid(row=3, column=0, pady=5)
# CircumferenceInsideentry = ttk.Entry(root, width=10)
# CircumferenceInsideentry.grid(row=3, column=1,pady=5)
#
# bankingLabel = Label(root, text="Track Banking (in degrees) ")
# bankingLabel.grid(row=4, column=0, pady=5)
# banking_entry = ttk.Entry(root, width=10, state=DISABLED)
# banking_entry.grid(row=4, column=1, pady=5)
#
# Bank = IntVar()
# Bank.set(0)
# Bankingbutton = Checkbutton(root, text="Yes", var=Bank, command=calculation.showBank)
# Bankingbutton.grid(row=4, column=3, pady=5)
#
# calcButton = ttk.Button(root, text="Calculate", command=calculation.disp_stagger)
# calcButton.grid(row=5, column=1, pady=(30, 0))
#
# StaggerLabel = Label(root, text="Stagger ")
# StaggerLabel.grid(row=6, column=0, pady=5)
# CalcstaggerLabel = Label(root, font="ariel 15 bold")
# CalcstaggerLabel.grid(row=6, column=1, pady=5)
#
# OutsideTireSizeLabel = Label(root, text="Outside Tire Size ")
# OutsideTireSizeLabel.grid(row=7, column=0, pady=5)
# CalcOutterTireLabel = Label(root, font="ariel 15 bold")
# CalcOutterTireLabel.grid(row=7, column=1, pady=5)
#
# # Database section
# separator = ttk.Separator(root, orient='horizontal')
# separator.grid(row=8, column=0, columnspan=4, sticky="ew", pady=10, padx=5)
#
# db_label = Label(root, text="DATABASE", font=("Arial", 9, "bold"))
# db_label.grid(row=9, column=0, columnspan=2, pady=5)
#
# # Notes and save button
# notes_label = Label(root, text="Notes:")
# notes_label.grid(row=10, column=0, sticky=W, padx=5, pady=2)
# notes_entry = ttk.Entry(root, width=20)
# notes_entry.grid(row=10, column=1, padx=5, pady=2)
#
# save_button = ttk.Button(root, text="Save Calculation", command=calculation.save_calculation, state=DISABLED)
# save_button.grid(row=11, column=3, padx=5, pady=2)
#
# # history_button = ttk.Button(root, text="View History", command=calculation.show_history)
# # history_button.grid(row=12, column=0, columnspan=2, pady=5)
#
#
#
# # print("Stagger Calculator loaded!")
# # print(f"Database: {db.db_name}")
#
# root.geometry("500x450")
# root.config(menu=menubar)
# root.mainloop()