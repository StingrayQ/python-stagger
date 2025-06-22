

import math
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import stagger_gui

# Global references (set by GUI)
gui = None
db = None
current_user = None
last_calculation = {}

def set_gui_reference(gui_instance):
    """Set reference to GUI instance"""
    global gui, db, current_user
    gui = gui_instance
    db = gui_instance.db
    current_user = gui_instance.user

############## Functions that get info############
def track_width():
    """Gets the track width from center line of left wheel to the center line of the right wheel"""
    try:
        # Handle both enabled and disabled states
        if gui.twEntry['state'] == 'disabled':
            # Field is disabled (vehicle selected), get the value directly
            numTw = float(gui.twEntry.get())
        else:
            # Field is enabled (manual entry)
            numTw = float(gui.twEntry.get())
        return numTw
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number for track width")
        return None

def rad_turn():
    """Distance the inside tire travels through corner"""
    try:
        numRi = float(gui.Cornerlengthentry.get())
        return numRi
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number for corner length")
        return None

def circ_in():
    """Circumference of inside tire (measure tire)"""
    try:
        # Handle both enabled and disabled states
        if gui.CircumferenceInsideentry['state'] == 'disabled':
            # Field is disabled (vehicle selected), get the value directly
            circInside = float(gui.CircumferenceInsideentry.get())
        else:
            # Field is enabled (manual entry)
            circInside = float(gui.CircumferenceInsideentry.get())
        return circInside
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number for tire circumference")
        return None

def track_bank():
    """Gets track banking"""
    try:
        if gui.Bank.get() == 1:
            return float(gui.banking_entry.get()) if gui.banking_entry.get() else 0
        return 0
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number for banking")
        return None

# def showBank():
#     """Enable/disable banking entry based on checkbox"""
#     if gui.Bank.get() == 1:
#         gui.banking_entry.config(state='normal')
#     elif gui.Bank.get() == 0:
#         # deletes any info in the banking entry box before disabling the field
#         gui.banking_entry.delete(0, END)
#         gui.banking_entry.config(state='disabled')

###########################Calculation########################

def disp_stagger():
    """Calculates the stagger by subtracting the outside tire from the inside tire size"""
    global last_calculation

    # Get values with error checking
    tw = track_width()
    rt = rad_turn()
    ci = circ_in()
    banking = track_bank()

    # Check if all values are valid
    if tw is None or rt is None or ci is None or banking is None:
        return

    try:
        if gui.Bank.get() == 0:
            # turns feet to inches
            calc_rad_turn = rt * 12
            outside_tire_rad = tw + calc_rad_turn
            # distance outside tire travels through turn
            dist_out_travel = (outside_tire_rad * 2) * (math.pi / 2)
            # distance inside tire travels through turn
            dist_in_travel = (calc_rad_turn * 2) * (math.pi / 2)
            circ_out = ci * dist_out_travel / dist_in_travel
            stagger = (circ_out - ci)
            gui.CalcstaggerLabel.config(text=f"{stagger:.2f}" + '"')
            gui.CalcOutterTireLabel.config(text=f"{circ_out:.2f}" + '"')
        elif gui.Bank.get() == 1:
            # turns feet to inches
            calc_rad_turn = rt * 12
            outside_tire_rad = tw + calc_rad_turn
            # distance outside tire travels through turn
            dist_out_travel = (outside_tire_rad * 2) * (math.pi / 2)
            # distance inside tire travels through turn
            dist_in_travel = (calc_rad_turn * 2) * (math.pi / 2)
            circ_out = ci * dist_out_travel / dist_in_travel
            stagger = (circ_out - ci)
            bankStagger = (math.cos(math.radians(banking)) * stagger)
            bank_circ_out = ci + bankStagger
            gui.CalcstaggerLabel.config(text=f"{bankStagger:.2f}" + '"')
            gui.CalcOutterTireLabel.config(text=f"{bank_circ_out:.2f}" + '"')
            stagger = bankStagger
            circ_out = bank_circ_out

        # Store calculation for saving
        last_calculation = {
            'track_width': tw,
            'corner_length': rt,
            'inside_tire_circ': ci,
            'banking': banking,
            'stagger': stagger,
            'outside_circ': circ_out
        }

        # Enable save button
        gui.save_button.config(state=NORMAL)

    except Exception as e:
        messagebox.showerror("Calculation Error", f"Error in calculation: {e}")

############## Database Functions ############
def save_calculation():
    """Save the current calculation to database for the logged-in user"""
    if not last_calculation:
        messagebox.showwarning("Warning", "No calculation to save. Please calculate first.")
        return

    if not current_user:
        messagebox.showerror("Error", "No user logged in!")
        return

    notes = gui.notes_entry.get()

    # Save calculation with user ID
    success, message = db.save_calculation(
        track_width=last_calculation['track_width'],
        corner_length_ft=last_calculation['corner_length'],
        inside_tire_circumference=last_calculation['inside_tire_circ'],
        banking_degrees=last_calculation['banking'],
        calculated_stagger=last_calculation['stagger'],
        outside_tire_circumference=last_calculation['outside_circ'],
        notes=notes,
        user_id=current_user['id']  # Pass the user ID
    )

    if success:
        messagebox.showinfo("Success", f"{message}\nSaved for user: {current_user['username']}")
        gui.notes_entry.delete(0, END)
        gui.save_button.config(state=DISABLED)
    else:
        messagebox.showerror("Error", message)

def show_history():
    """Show calculation history for the logged-in user"""
    if not current_user:
        messagebox.showerror("Error", "No user logged in!")
        return

    # Get calculations for current user only
    calculations = db.get_user_calculations(current_user['id'], limit=50)

    if not calculations:
        messagebox.showinfo("History", f"No calculations found for {current_user['username']}.")
        return

    # Create enhanced history window with search functionality
    create_enhanced_history_window(calculations)

def create_enhanced_history_window(calculations):
    """Create an enhanced history window with search and export functionality"""

    # Create history window
    history_window = Toplevel(gui.root)
    history_window.title(f"Calculation History - {current_user['username']} ({current_user['team_name']})")
    history_window.geometry("1100x600")

    # Create main frame
    main_frame = ttk.Frame(history_window)
    main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # Title
    title_label = Label(main_frame,
                       text=f"Stagger Calculation History - {current_user['team_name']}",
                       font=("Arial", 14, "bold"))
    title_label.pack(pady=(0, 10))

    # Search frame
    search_frame = ttk.LabelFrame(main_frame, text="Search & Filter", padding=10)
    search_frame.pack(fill=X, pady=(0, 10))

    # Search controls
    search_row1 = ttk.Frame(search_frame)
    search_row1.pack(fill=X, pady=2)

    ttk.Label(search_row1, text="Date From:").pack(side=LEFT, padx=(0, 5))
    date_from_entry = ttk.Entry(search_row1, width=12)
    date_from_entry.pack(side=LEFT, padx=(0, 10))

    ttk.Label(search_row1, text="Date To:").pack(side=LEFT, padx=(0, 5))
    date_to_entry = ttk.Entry(search_row1, width=12)
    date_to_entry.pack(side=LEFT, padx=(0, 10))

    ttk.Label(search_row1, text="Min Stagger:").pack(side=LEFT, padx=(0, 5))
    min_stagger_entry = ttk.Entry(search_row1, width=8)
    min_stagger_entry.pack(side=LEFT, padx=(0, 10))

    ttk.Label(search_row1, text="Max Stagger:").pack(side=LEFT, padx=(0, 5))
    max_stagger_entry = ttk.Entry(search_row1, width=8)
    max_stagger_entry.pack(side=LEFT, padx=(0, 10))

    search_row2 = ttk.Frame(search_frame)
    search_row2.pack(fill=X, pady=2)

    ttk.Label(search_row2, text="Notes contain:").pack(side=LEFT, padx=(0, 5))
    notes_search_entry = ttk.Entry(search_row2, width=20)
    notes_search_entry.pack(side=LEFT, padx=(0, 10))

    # Search and Export buttons
    button_frame = ttk.Frame(search_frame)
    button_frame.pack(fill=X, pady=(10, 0))

    search_button = ttk.Button(button_frame, text="Search",
                              command=lambda: filter_results())
    search_button.pack(side=LEFT, padx=(0, 10))

    clear_button = ttk.Button(button_frame, text="Clear Filters",
                             command=lambda: clear_filters())
    clear_button.pack(side=LEFT, padx=(0, 10))

    export_csv_button = ttk.Button(button_frame, text="Export to CSV",
                                  command=lambda: export_to_csv())
    export_csv_button.pack(side=LEFT, padx=(0, 10))

    # Results frame
    results_frame = ttk.LabelFrame(main_frame, text="Calculation Results", padding=5)
    results_frame.pack(fill=BOTH, expand=True)

    # Create treeview for displaying history
    columns = ('Date', 'Stagger', 'Track Width', 'Corner Length', 'Tire Circ', 'Banking', 'Outside Tire', 'Notes')
    tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)

    # Define column headings and widths
    column_widths = {
        'Date': 140,
        'Stagger': 80,
        'Track Width': 90,
        'Corner Length': 100,
        'Tire Circ': 80,
        'Banking': 70,
        'Outside Tire': 90,
        'Notes': 200
    }

    for col in columns:
        tree.heading(col, text=col, command=lambda c=col: sort_treeview(tree, c, False))
        tree.column(col, width=column_widths[col])

    # Add scrollbars
    v_scrollbar = ttk.Scrollbar(results_frame, orient=VERTICAL, command=tree.yview)
    h_scrollbar = ttk.Scrollbar(results_frame, orient=HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

    # Pack treeview and scrollbars
    tree.grid(row=0, column=0, sticky='nsew')
    v_scrollbar.grid(row=0, column=1, sticky='ns')
    h_scrollbar.grid(row=1, column=0, sticky='ew')

    results_frame.grid_rowconfigure(0, weight=1)
    results_frame.grid_columnconfigure(0, weight=1)

    # Status label
    status_label = Label(main_frame, text="", font=("Arial", 9))
    status_label.pack(pady=(5, 0))

    # Store original data for filtering
    original_data = calculations

    def populate_tree(data):

        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)

        # Add data to treeview
        for calc in data:
            # Format the data for display
            date_str = calc[6][:10] if calc[6] else "Unknown"  # Only take YYYY-MM-DD part
            row_data = (
                date_str,
                f"{calc[4]:.3f}\"",      # calculated_stagger
                f"{calc[0]:.1f}\"",      # track_width
                f"{calc[1]:.1f} ft",     # corner_length_ft
                f"{calc[2]:.1f}\"",      # inside_tire_circumference
                f"{calc[3]:.1f}°",       # banking_degrees
                f"{calc[5]:.3f}\"",      # outside_tire_circumference
                calc[7] if calc[7] else ""  # notes
            )
            tree.insert('', END, values=row_data)

        # Update status
        status_label.config(text=f"Showing {len(data)} calculations")

    def filter_results():

        filtered_data = original_data.copy()

        # Apply filters (basic implementation)
        date_from = date_from_entry.get().strip()
        date_to = date_to_entry.get().strip()
        min_stagger = min_stagger_entry.get().strip()
        max_stagger = max_stagger_entry.get().strip()
        notes_search = notes_search_entry.get().strip().lower()

        if notes_search:
            filtered_data = [calc for calc in filtered_data
                           if notes_search in (calc[7] or "").lower()]

        if min_stagger:
            try:
                min_val = float(min_stagger)
                filtered_data = [calc for calc in filtered_data if calc[4] >= min_val]
            except ValueError:
                pass

        if max_stagger:
            try:
                max_val = float(max_stagger)
                filtered_data = [calc for calc in filtered_data if calc[4] <= max_val]
            except ValueError:
                pass

        populate_tree(filtered_data)

    def clear_filters():

        date_from_entry.delete(0, END)
        date_to_entry.delete(0, END)
        min_stagger_entry.delete(0, END)
        max_stagger_entry.delete(0, END)
        notes_search_entry.delete(0, END)
        populate_tree(original_data)


    def export_to_csv():
        try:
            from tkinter import filedialog
            import csv
            from datetime import datetime

            # Get current items in tree
            items = []
            for child in tree.get_children():
                items.append(tree.item(child)['values'])

            if not items:
                messagebox.showwarning("No Data", "No data to export.")
                return

            # Create default filename
            default_filename = f"stagger_history_{current_user['username']}_{datetime.now().strftime('%Y%m%d')}.csv"

            # Ask user for save location (without initialvalue)
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title=f"Export Calculation History - Save as: {default_filename}"
            )

            if filename:
                # If user didn't add .csv extension, add it
                if not filename.lower().endswith('.csv'):
                    filename += '.csv'

                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)

                    # Write header information
                    writer.writerow([f"Stagger Calculation History - {current_user['team_name']}"])
                    writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                    writer.writerow([f"User: {current_user['username']}"])
                    writer.writerow([])  # Empty row

                    # Write column headers
                    writer.writerow(columns)

                    # Write data
                    for item in items:
                        writer.writerow(item)

                messagebox.showinfo("Export Successful",
                                    f"Data exported successfully to:\n{filename}\n\nTotal records: {len(items)}")

        except ImportError as e:
            messagebox.showerror("Import Error", f"Required module not available: {e}")
        except PermissionError:
            messagebox.showerror("Permission Error",
                                 "Cannot write to the selected file. Please choose a different location or close the file if it's open in another program.")
        except FileNotFoundError:
            messagebox.showerror("File Error", "The selected directory does not exist. Please choose a valid location.")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data:\n{str(e)}")


    # def export_to_csv():
    #
    #     from tkinter import filedialog
    #     import csv
    #     from datetime import datetime
    #
    #     # Get current items in tree
    #     items = []
    #     for child in tree.get_children():
    #         items.append(tree.item(child)['values'])
    #
    #     if not items:
    #         messagebox.showwarning("No Data", "No data to export.")
    #         return
    #
    #     # Ask user for save location
    #     filename = filedialog.asksaveasfilename(
    #         defaultextension=".csv",
    #         filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
    #         title="Export Calculation History",
    #         initialvalue=f"stagger_history_{current_user['username']}_{datetime.now().strftime('%Y%m%d')}.csv"
    #     )
    #
    #     if filename:
    #         try:
    #             with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
    #                 writer = csv.writer(csvfile)
    #
    #                 # Write header
    #                 writer.writerow([f"Stagger Calculation History - {current_user['team_name']}"])
    #                 writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
    #                 writer.writerow([f"User: {current_user['username']}"])
    #                 writer.writerow([])  # Empty row
    #
    #                 # Write column headers
    #                 writer.writerow(columns)
    #
    #                 # Write data
    #                 writer.writerows(items)
    #
    #             messagebox.showinfo("Export Successful", f"Data exported to:\n{filename}")
    #
    #         except Exception as e:
    #             messagebox.showerror("Export Error", f"Failed to export data:\n{e}")

    def sort_treeview(tree, col, reverse):

        data = [(tree.set(child, col), child) for child in tree.get_children('')]

        # Try to sort numerically if possible
        try:
            if col == 'Date':
                # Sort dates properly (YYYY-MM-DD format)
                data.sort(key=lambda x: x[0] if x[0] != "Unknown" else "0000-00-00", reverse=reverse)
            elif col in ['Stagger', 'Track Width', 'Tire Circ', 'Banking', 'Outside Tire']:
                # Remove units and convert to float for numeric columns
                data.sort(key=lambda x: float(x[0].replace('"', '').replace('°', '').replace(' ft', '')),
                          reverse=reverse)
            else:
                # Sort alphabetically for other columns
                data.sort(key=lambda x: x[0].lower(), reverse=reverse)
        except (ValueError, AttributeError):
            # Fallback to simple alphabetical sort
            data.sort(key=lambda x: str(x[0]), reverse=reverse)

        # Rearrange items in sorted positions
        for index, (val, child) in enumerate(data):
            tree.move(child, '', index)

        # Update column heading to show sort direction
        for c in columns:
            if c == col:
                tree.heading(c, text=f"{c} {'↓' if reverse else '↑'}",
                             command=lambda c=col: sort_treeview(tree, c, not reverse))
            else:
                tree.heading(c, text=c,
                             command=lambda c=c: sort_treeview(tree, c, False))

    # Initially populate with all data
    populate_tree(original_data)

    # Add help text
    help_text = "💡 Click column headers to sort • Use filters to narrow results • Export creates a timestamped CSV report"
    help_label = Label(main_frame, text=help_text, font=("Arial", 8), fg="gray")
    help_label.pack(pady=(5, 0))










# import math
# from tkinter import *
# from tkinter import ttk
# from tkinter import messagebox
# from staggerDB import StaggerDatabase
# import stagger_gui
#
# # Initialize database
# db = StaggerDatabase()
#
# def get_root():
#     return stagger_gui.root
#
# # root = Tk()
# # root.title("Stagger Calculator")
#
# # Global variable to store last calculation
# last_calculation = {}
#
#
# ############## Functions that get info############
# def track_width():
#     """Gets the track width from center line of left wheel to the center line of the right wheel"""
#     try:
#         numTw = float(stagger_gui.twEntry.get())
#         return numTw
#     except ValueError:
#         messagebox.showerror("Input Error", "Please enter a valid number for track width")
#         return None
#
#
# def rad_turn():
#     """Distance the inside tire travels through corner"""
#     try:
#         numRi = float(stagger_gui.Cornerlengthentry.get())
#         return numRi
#     except ValueError:
#         messagebox.showerror("Input Error", "Please enter a valid number for corner length")
#         return None
#
#
# def circ_in():
#     """Circumference of inside tire (measure tire)"""
#     try:
#         circInside = float(stagger_gui.CircumferenceInsideentry.get())
#         return circInside
#     except ValueError:
#         messagebox.showerror("Input Error", "Please enter a valid number for tire circumference")
#         return None
#
#
# def track_bank():
#     """Gets track banking"""
#     try:
#         if stagger_gui.Bank.get() == 1:
#             return float(stagger_gui.banking_entry.get()) if stagger_gui.banking_entry.get() else 0
#         return 0
#     except ValueError:
#         messagebox.showerror("Input Error", "Please enter a valid number for banking")
#         return None
#
#
# def showBank():
#     """Enable/disable banking entry based on checkbox"""
#     if stagger_gui.Bank.get() == 1:
#         stagger_gui.banking_entry.config(state=NORMAL)
#     elif stagger_gui.Bank.get() == 0:
#         # deletes any info in the banking entry box before disabling the field
#         stagger_gui.banking_entry.delete(0, END)
#         stagger_gui.banking_entry.config(state=DISABLED)
#
#
# ###########################Calculation########################
#
# def disp_stagger():
#     """Calculates the stagger by subtracting the outside tire from the inside tire size"""
#     global last_calculation
#
#     # Get values with error checking
#     tw = track_width()
#     rt = rad_turn()
#     ci = circ_in()
#     banking = track_bank()
#
#     # Check if all values are valid
#     if tw is None or rt is None or ci is None or banking is None:
#         return
#
#     try:
#         if stagger_gui.Bank.get() == 0:
#             # turns feet to inches
#             calc_rad_turn = rt * 12
#             outside_tire_rad = tw + calc_rad_turn
#             # distance outside tire travels through turn
#             dist_out_travel = (outside_tire_rad * 2) * (math.pi / 2)
#             # distance inside tire travels through turn
#             dist_in_travel = (calc_rad_turn * 2) * (math.pi / 2)
#             circ_out = ci * dist_out_travel / dist_in_travel
#             stagger = (circ_out - ci)
#             stagger_gui.CalcstaggerLabel.config(text=f"{stagger:.2f}" + '"')
#             stagger_gui.CalcOutterTireLabel.config(text=f"{circ_out:.2f}" + '"')
#         elif stagger_gui.Bank.get() == 1:
#             # turns feet to inches
#             calc_rad_turn = rt * 12
#             outside_tire_rad = tw + calc_rad_turn
#             # distance outside tire travels through turn
#             dist_out_travel = (outside_tire_rad * 2) * (math.pi / 2)
#             # distance inside tire travels through turn
#             dist_in_travel = (calc_rad_turn * 2) * (math.pi / 2)
#             circ_out = ci * dist_out_travel / dist_in_travel
#             stagger = (circ_out - ci)
#             bankStagger = (math.cos(math.radians(banking)) * stagger)
#             bank_circ_out = ci + bankStagger
#             stagger_gui.CalcstaggerLabel.config(text=f"{bankStagger:.2f}" + '"')
#             stagger_gui.CalcOutterTireLabel.config(text=f"{bank_circ_out:.2f}" + '"')
#             stagger = bankStagger
#             circ_out = bank_circ_out
#
#         # Store calculation for saving
#         last_calculation = {
#             'track_width': tw,
#             'corner_length': rt,
#             'inside_tire_circ': ci,
#             'banking': banking,
#             'stagger': stagger,
#             'outside_circ': circ_out
#         }
#
#         # Enable save button
#         stagger_gui.save_button.config(state=NORMAL)
#
#     except Exception as e:
#         messagebox.showerror("Calculation Error", f"Error in calculation: {e}")
#
#
# ############## Database Functions ############
# def save_calculation():
#     """Save the current calculation to database"""
#     if not last_calculation:
#         messagebox.showwarning("Warning", "No calculation to save. Please calculate first.")
#         return
#
#     notes = stagger_gui.notes_entry.get()
#
#     success, message = db.save_calculation(
#         track_width=last_calculation['track_width'],
#         corner_length_ft=last_calculation['corner_length'],
#         inside_tire_circumference=last_calculation['inside_tire_circ'],
#         banking_degrees=last_calculation['banking'],
#         calculated_stagger=last_calculation['stagger'],
#         outside_tire_circumference=last_calculation['outside_circ'],
#         notes=notes
#     )
#
#     if success:
#         messagebox.showinfo("Success", message)
#         stagger_gui.notes_entry.delete(0, END)
#         stagger_gui.save_button.config(state=DISABLED)
#     else:
#         messagebox.showerror("Error", message)
#
#
# def show_history():
#
#     calculations = db.get_calculations(limit=20)
#
#     if not calculations:
#         messagebox.showinfo("History", "No calculations found in database.")
#         return
#
#     # Create history window
#     history_window = Toplevel(get_root())
#     history_window.title("Calculation History")
#     history_window.geometry("900x400")
#
#     # Create treeview for displaying history
#     columns = ('Notes', 'Date', 'Calculated Stagger','Inner Tire Circ', 'Outside Tire', 'Vehicle Track Width', 'Corner Length', 'Banking')
#     tree = ttk.Treeview(history_window, columns=columns, show='headings')
#
#     # Define column headings and widths
#     for col in columns:
#         tree.heading(col, text=col)
#         if col == 'Notes':
#             tree.column(col, width=150)
#         else:
#             tree.column(col, width=100)
#
#     # Add data to treeview
#     for calc in calculations:
#         # Format the data for display
#         date_str = calc[6][:19] if calc[6] else "Unknown"  # calculation_date
#         row_data = (
#             calc[7] if calc[7] else "",  # notes
#             date_str,
#             f"{calc[4]:.2f}\"",  # calculated_stagger
#             f"{calc[2]:.2f}\"",  # inside_tire_circumference
#             f"{calc[5]:.2f}\"",  # outside_tire_circumference
#             f"{calc[0]:.1f}\"",  # track_width
#             f"{calc[1]:.1f} ft",  # corner_length_ft
#             f"{calc[3]:.1f}°",  # banking_degrees
#
#
#         )
#         tree.insert('', END, values=row_data)
#
#     # Add scrollbar
#     scrollbar = ttk.Scrollbar(history_window, orient=VERTICAL, command=tree.yview)
#     tree.configure(yscrollcommand=scrollbar.set)
#
#     # Pack everything
#     tree.pack(side=LEFT, fill=BOTH, expand=True, padx=(10, 0), pady=10)
#     scrollbar.pack(side=RIGHT, fill=Y, pady=10, padx=(0, 10))
#
#
# # ############## GUI Setup ############
# #
# # # Creating Menubar
# # menubar = Menu(root)
# # file = Menu(menubar, tearoff=0)
# # file.add_command(label='Exit', command=root.destroy)
# # menubar.add_cascade(label='File', menu=file)
# #
# # vehicles = Menu(menubar, tearoff=0)
# # tracks= Menu(menubar, tearoff=0)
# # data= Menu(menubar, tearoff=0)
# #
# # menubar.add_cascade(label='Vehicles', menu=vehicles)
# # vehicles.add_command(label='Add Vehicle', command=None)
# # vehicles.add_separator()
# #
# # menubar.add_cascade(label='Tracks', menu=tracks)
# # tracks.add_command(label='Add Track', command=None)
# # tracks.add_separator()
# #
# # menubar.add_cascade(label='Data', menu=data)
# # data.add_command(label='Stagger Data', command=show_history)
# # data.add_separator()
# #
# #
# # spaceLabel = Label(root, text="")
# # spaceLabel.grid(row=0, column=0, pady=10)
# #
# # trackWidthLabel = Label(root, text="Track Width")
# # trackWidthLabel.grid(row=1, column=0)
# # twEntry = ttk.Entry(root, width=10)
# # twEntry.grid(row=1, column=1, padx=10, pady=5)
# #
# # CornerlgthLabel = Label(root, text="Corner length (in feet)")
# # CornerlgthLabel.grid(row=2, column=0, pady=5)
# # Cornerlengthentry = ttk.Entry(root, width=10)
# # Cornerlengthentry.grid(row=2, column=1, pady=5)
# #
# # CircumferenceInsideLabel = Label(root, text="Circumference of inside tire (in inches) ")
# # CircumferenceInsideLabel.grid(row=3, column=0, pady=5)
# # CircumferenceInsideentry = ttk.Entry(root, width=10)
# # CircumferenceInsideentry.grid(row=3, column=1,pady=5)
# #
# # bankingLabel = Label(root, text="Track Banking (in degrees) ")
# # bankingLabel.grid(row=4, column=0, pady=5)
# # banking_entry = ttk.Entry(root, width=10, state=DISABLED)
# # banking_entry.grid(row=4, column=1, pady=5)
# #
# # Bank = IntVar()
# # Bank.set(0)
# # Bankingbutton = Checkbutton(root, text="Yes", var=Bank, command=showBank)
# # Bankingbutton.grid(row=4, column=3, pady=5)
# #
# # calcButton = ttk.Button(root, text="Calculate", command=disp_stagger)
# # calcButton.grid(row=5, column=1, pady=(30, 0))
# #
# # StaggerLabel = Label(root, text="Stagger ")
# # StaggerLabel.grid(row=6, column=0, pady=5)
# # CalcstaggerLabel = Label(root, font="ariel 15 bold")
# # CalcstaggerLabel.grid(row=6, column=1, pady=5)
# #
# # OutsideTireSizeLabel = Label(root, text="Outside Tire Size ")
# # OutsideTireSizeLabel.grid(row=7, column=0, pady=5)
# # CalcOutterTireLabel = Label(root, font="ariel 15 bold")
# # CalcOutterTireLabel.grid(row=7, column=1, pady=5)
# #
# # # Database section
# # separator = ttk.Separator(root, orient='horizontal')
# # separator.grid(row=8, column=0, columnspan=4, sticky="ew", pady=10, padx=5)
# #
# # db_label = Label(root, text="DATABASE", font=("Arial", 9, "bold"))
# # db_label.grid(row=9, column=0, columnspan=2, pady=5)
# #
# # # Notes and save button
# # notes_label = Label(root, text="Notes:")
# # notes_label.grid(row=10, column=0, sticky=W, padx=5, pady=2)
# # notes_entry = ttk.Entry(root, width=20)
# # notes_entry.grid(row=10, column=1, padx=5, pady=2)
# #
# # save_button = ttk.Button(root, text="Save Calculation", command=save_calculation, state=DISABLED)
# # save_button.grid(row=11, column=3, padx=5, pady=2)
# #
# # history_button = ttk.Button(root, text="View History", command=show_history)
# # history_button.grid(row=12, column=0, columnspan=2, pady=5)
# #
# #
# #
# # print("Stagger Calculator loaded!")
# # print(f"Database: {db.db_name}")
# #
# # root.geometry("500x450")
# # root.config(menu=menubar)
# # root.mainloop()
#
#
#
#
#
#
# # import math
# # from tkinter import *
# # from tkinter import ttk
# #
# # root = Tk()
# # root.title("Stagger Calculator")
# #
# #
# # ############## Functions that get info############
# # def track_width():
# #     # gets the track width from center line of left wheel to the center line of the right wheel
# #     numTw = int(TWentry.get())
# #     return numTw
# #
# #
# # def rad_turn():
# #     # distance the inside tire travels through corner
# #     numRi = int(Cornerlengthentry.get())
# #     return numRi
# #
# #
# # def circ_in():
# #     # circumference of inside tire (measure tire)
# #     circInside = float(CircumferenceInsideentry.get())
# #     return circInside
# #
# # def track_bank():
# #     # gets track banking
# #     banking = float(banking_entry.get())
# #     return banking
# #
# # def showBank():
# #     if Bank.get() == 1:
# #         banking_entry.config(state=NORMAL)
# #     elif Bank.get() == 0:
# #         # deletes any info in the banking entry box before disabling the field
# #         banking_entry.delete(0, END)
# #         banking_entry.config(state=DISABLED)
# # ###########################Calculation########################
# #
# # # calculates the stagger by subtracting the outside tire from the inside tire size
# # def disp_stagger():
# #     if Bank.get() == 0:
# #         # turns feet to inches
# #         calc_rad_turn = rad_turn() * 12
# #         outside_tire_rad = track_width() + calc_rad_turn
# #         # distance outside tire travels through turn
# #         dist_out_travel = (outside_tire_rad * 2) * (math.pi / 2)
# #         # distance inside tire travels through turn
# #         dist_in_travel = (calc_rad_turn * 2) * (math.pi / 2)
# #         circ_out = circ_in() * dist_out_travel / dist_in_travel
# #         stagger = (circ_out - circ_in())
# #         CalcstaggerLabel.config(text=f"{stagger:.2f}" + '"')
# #         CalcOutterTireLabel.config(text=f"{circ_out:.2f}" + '"')
# #     elif Bank.get() == 1:
# #         # turns feet to inches
# #         calc_rad_turn = rad_turn() * 12
# #         outside_tire_rad = track_width() + calc_rad_turn
# #         # distance outside tire travels through turn
# #         dist_out_travel = (outside_tire_rad * 2) * (math.pi / 2)
# #         # distance inside tire travels through turn
# #         dist_in_travel = (calc_rad_turn * 2) * (math.pi / 2)
# #         circ_out = circ_in() * dist_out_travel / dist_in_travel
# #         stagger = (circ_out - circ_in())
# #         bankStagger = (math.cos(math.radians(track_bank())) * stagger)
# #         bank_circ_out = circ_in() + bankStagger
# #         CalcstaggerLabel.config(text=f"{bankStagger:.2f}" + '"')
# #         CalcOutterTireLabel.config(text=f"{bank_circ_out:.2f}" + '"')
# #
# #     return stagger, circ_out
# #
# #
# #
# #
# #
# #
# #
# # trackWidthLabel = Label(root, text="Track Width")
# # trackWidthLabel.grid(row=0, column=0)
# # TWentry = ttk.Entry(root, width=10)
# # TWentry.grid(row=0, column=1)
# # CornerlgthLabel = Label(root, text="Corner length (in feet)")
# # CornerlgthLabel.grid(row=1, column=0)
# # Cornerlengthentry = ttk.Entry(root, width=10)
# # Cornerlengthentry.grid(row=1, column=1)
# # CircumferenceInsideLabel = Label(root, text="Circumference of inside tire (in inches) ")
# # CircumferenceInsideLabel.grid(row=2, column=0)
# # CircumferenceInsideentry = ttk.Entry(root, width=10)
# # CircumferenceInsideentry.grid(row=2, column=1)
# # CalcstaggerLabel = Label(root, font="ariel 15 bold")
# # CalcstaggerLabel.grid(row=5, column=1)
# # CalcOutterTireLabel = Label(root, font="ariel 15 bold")
# # CalcOutterTireLabel.grid(row=6, column=1)
# # calcButton = ttk.Button(root, text="Calculate", command=disp_stagger)
# # calcButton.grid(row=4, column=1, pady=(30, 0))
# # StaggerLabel = Label(root, text="Stagger ")
# # StaggerLabel.grid(row=5, column=0)
# # OutsideTireSizeLabel = Label(root, text="Outside Tire Size ")
# # OutsideTireSizeLabel.grid(row=6, column=0)
# # Bank = IntVar()
# # Bank.set(0)
# # Bankingbutton = Checkbutton(root, text="Yes", var=Bank, command=showBank)
# # Bankingbutton.grid(row=3, column=3)
# # bankingLabel = Label(root, text="Track Banking (in degrees) ")
# # bankingLabel.grid(row=3, column=0)
# # banking_entry = ttk.Entry(root, width=10, state=DISABLED)
# # banking_entry.grid(row=3, column=1)
# #
# #
# # root.geometry("400x300")
# # root.mainloop()