import streamlit as st
import math
import sys
import os
import pandas as pd
from datetime import datetime


class BaseEntity:


    def __init__(self, name: str):
        self.name = name
        self.created_date = datetime.now()

    def validate(self):

        return len(self.name.strip()) > 0, "Name cannot be empty"

    def get_display_info(self):

        return f"{self.name} (Created: {self.created_date.strftime('%Y-%m-%d')})"


class VehicleEntity(BaseEntity):


    def __init__(self, name: str, vehicle_type: str, track_width: float, tire_circumference: float):
        super().__init__(name)  # INHERITANCE - call parent constructor
        self.vehicle_type = vehicle_type
        self.track_width = track_width
        self.tire_circumference = tire_circumference

    def validate(self):

        name_valid, name_error = super().validate()  # Call parent method

        if not name_valid:
            return False, name_error

        if self.track_width <= 0 or self.track_width > 200:
            return False, "Track width must be between 0 and 200 inches"

        if self.tire_circumference <= 0 or self.tire_circumference > 200:
            return False, "Tire circumference must be between 0 and 200 inches"

        return True, "Valid vehicle"

    def get_display_info(self):

        base_info = super().get_display_info()
        return f"🚗 {base_info} | Type: {self.vehicle_type} | Track Width: {self.track_width}\" | Tire: {self.tire_circumference}\""

    def get_specs_summary(self):

        return f"Track Width: {self.track_width}\", Tire Circumference: {self.tire_circumference}\""


class TrackEntity(BaseEntity):


    def __init__(self, name: str, corner_length: float, banking: float, surface_type: str):
        super().__init__(name)  # INHERITANCE - call parent constructor
        self.corner_length = corner_length
        self.banking = banking
        self.surface_type = surface_type

    def validate(self):

        name_valid, name_error = super().validate()  # Call parent method

        if not name_valid:
            return False, name_error

        if self.corner_length <= 0 or self.corner_length > 5000:
            return False, "Corner length must be between 0 and 5000 feet"

        if self.banking < 0 or self.banking > 90:
            return False, "Banking must be between 0 and 90 degrees"

        return True, "Valid track"

    def get_display_info(self):

        base_info = super().get_display_info()
        return f"🏁 {base_info} | Surface: {self.surface_type} | Corner: {self.corner_length}ft | Banking: {self.banking}°"

    def get_specs_summary(self):

        return f"Corner Length: {self.corner_length}ft, Banking: {self.banking}°, Surface: {self.surface_type}"


# polymorphism help

def validate_entities(entities):

    results = []
    for entity in entities:
        # This calls the appropriate validate() method based on object type
        is_valid, message = entity.validate()
        results.append({
            'entity': entity,
            'valid': is_valid,
            'message': message,
            'type': type(entity).__name__
        })
    return results


def display_entity_info(entities):

    for entity in entities:
        # This calls the appropriate get_display_info() method
        st.write(f"• {entity.get_display_info()}")




# Python path to find modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Configure page
st.set_page_config(
    page_title="Stagger Calculator",
    page_icon="🏁",
    layout="wide"
)

# Import database
try:
    from staggerDB import StaggerDatabase

    db = StaggerDatabase("stagger_calculator.db")
except ImportError as e:
    st.error(f"❌ Cannot import database module: {e}")
    st.stop()
except Exception as e:
    st.error(f"❌ Database connection error: {e}")
    st.stop()

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None
if 'selected_vehicle' not in st.session_state:
    st.session_state.selected_vehicle = "Manual Entry"
if 'selected_track' not in st.session_state:
    st.session_state.selected_track = "Manual Entry"


def simple_login():
    st.title("🏁 Stagger Calculator Login")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("login_form"):
            st.markdown("### Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")

            if login_button:
                if username and password:
                    try:
                        user = db.authenticate_user(username, password)
                        if user:
                            st.session_state.authenticated = True
                            st.session_state.user = user
                            st.success(f"Welcome, {user['username']}!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
                    except Exception as e:
                        st.error(f"Login error: {e}")
                else:
                    st.warning("Please enter username and password")

        # Demo credentials
        with st.expander("🔍 Demo Account"):
            st.info("Username: demo\nPassword: demo123")


def calculate_stagger_smart_angle(track_width, corner_length_ft, inside_tire_circumference, banking_degrees=0):
    """Calculate stagger with smart angle selection and track type determination"""
    try:
        # Estimate corner angle based on corner length
        if corner_length_ft < 350:
            corner_angle_degrees = 120.0  # Tight bullring
            track_type = "🏁 Tight Bullring"
        elif corner_length_ft < 500:
            corner_angle_degrees = 110.0  # Typical short track
            track_type = "🏁 Short Track"
        elif corner_length_ft < 700:
            corner_angle_degrees = 100.0  # Standard oval
            track_type = "🏁 Standard Oval"
        elif corner_length_ft < 1000:
            corner_angle_degrees = 90.0  # Wide speedway corners
            track_type = "🏁 Wide Speedway"
        else:
            corner_angle_degrees = 80.0  # Very wide superspeedway
            track_type = "🏁 Superspeedway"

        # Convert corner arc length to radius
        angle_radians = math.radians(corner_angle_degrees)
        Ri_feet = corner_length_ft / angle_radians

        # Apply your exact racing formula
        Ri = Ri_feet * 12  # Radius to inside tire (inches)
        T = track_width  # Track width (inches)
        Ro = Ri + T  # Radius to outside tire (inches)

        # Calculate distances traveled
        Di = Ri * 2 * math.pi / 2  # Inside tire distance
        Do = Ro * 2 * math.pi / 2  # Outside tire distance

        # Calculate tire circumferences
        Ci = inside_tire_circumference  # Inside tire (given)
        Co = Ci * (Do / Di)  # Outside tire needed

        # Calculate stagger
        stagger = Co - Ci

        # Apply banking correction
        if banking_degrees > 0:
            banking_factor = math.cos(math.radians(banking_degrees))
            stagger = stagger * banking_factor
            Co = Ci + stagger

        return stagger, Co, corner_angle_degrees, track_type

    except Exception as e:
        st.error(f"Calculation error: {e}")
        return None, None, None, None


def load_user_vehicles():

    try:
        vehicles = db.get_user_vehicles(st.session_state.user['id'])
        vehicle_options = ["Manual Entry"] + [vehicle[0] for vehicle in vehicles]
        return vehicle_options, vehicles
    except Exception as e:
        st.error(f"Error loading vehicles: {e}")
        return ["Manual Entry"], []


def load_user_tracks():

    try:
        tracks = db.get_user_tracks(st.session_state.user['id'])
        track_options = ["Manual Entry"] + [track[0] for track in tracks]
        return track_options, tracks
    except Exception as e:
        st.error(f"Error loading tracks: {e}")
        return ["Manual Entry"], []


def get_vehicle_data(vehicle_name, vehicles):

    for vehicle in vehicles:
        if vehicle[0] == vehicle_name:
            return {
                'track_width': vehicle[1],
                'inside_tire_circumference': vehicle[2],
                'vehicle_type': vehicle[3]
            }
    return None


def get_track_data(track_name, tracks):

    for track in tracks:
        if track[0] == track_name:
            return {
                'corner_length_ft': track[1],
                'banking_degrees': track[2],
                'surface_type': track[3]
            }
    return None


def vehicle_management():
    st.header("🚗 Vehicle Management")

    tab1, tab2, tab3 = st.tabs(["Add Vehicle", "Edit Vehicle", "Manage Vehicles"])

    with tab1:
        st.subheader("Add New Vehicle")

        with st.form("add_vehicle_form"):
            vehicle_name = st.text_input("Vehicle Name", placeholder="e.g., Car #42")
            vehicle_type = st.selectbox("Vehicle Type",
                                        ["Stock Car", "Modified", "Late Model", "Sprint Car", "Other"])

            col1, col2 = st.columns(2)
            with col1:
                track_width = st.number_input("Track Width (inches)",
                                              min_value=0.0, value=60.0, step=0.1)
            with col2:
                tire_circumference = st.number_input("Inside Tire Circumference (inches)",
                                                     min_value=0.0, value=82.5, step=0.1)

            if st.form_submit_button("💾 Save Vehicle"):
                # CREATE VEHICLE OBJECT AND VALIDATE
                vehicle_obj = VehicleEntity(vehicle_name, vehicle_type, track_width, tire_circumference)
                is_valid, error_msg = vehicle_obj.validate()

                if not is_valid:
                    st.error(f"❌ {error_msg}")
                else:
                    # Save to database using existing code
                    success, message = db.save_vehicle(
                        vehicle_name=vehicle_obj.name,
                        track_width=vehicle_obj.track_width,
                        inside_tire_circumference=vehicle_obj.tire_circumference,
                        vehicle_type=vehicle_obj.vehicle_type,
                        user_id=st.session_state.user['id']
                    )

                    if success:
                        st.success(f"✅ {message}")
                        # SHOW VEHICLE INFO
                        st.info(f"📋 Created: {vehicle_obj.get_display_info()}")
                        st.rerun()
                    else:
                        st.error(message)

    with tab2:
        st.subheader("Edit Vehicle")

        vehicles = db.get_user_vehicles(st.session_state.user['id'])

        if vehicles:
            vehicle_names = [v[0] for v in vehicles]
            selected_vehicle_name = st.selectbox("Select vehicle to edit:",
                                                 ["Select..."] + vehicle_names)

            if selected_vehicle_name != "Select...":
                # Get vehicle data
                vehicle_id = db.get_vehicle_id_by_name(st.session_state.user['id'], selected_vehicle_name)
                vehicle_data = db.get_vehicle_by_id(vehicle_id, st.session_state.user['id'])

                if vehicle_data:
                    # ENHANCED VEHICLE SELECTION INFO
                    current_vehicle = VehicleEntity(
                        vehicle_data[1],
                        vehicle_data[4],
                        float(vehicle_data[2]) if vehicle_data[2] else 60.0,
                        float(vehicle_data[3]) if vehicle_data[3] else 82.5
                    )

                    # # SHOW CURRENT VEHICLE INFO
                    # st.info(f"Current: {current_vehicle.get_display_info()}")

                    with st.form("edit_vehicle_form"):
                        new_vehicle_name = st.text_input("Vehicle Name", value=current_vehicle.name)
                        new_vehicle_type = st.selectbox("Vehicle Type",
                                                        ["Stock Car", "Modified", "Late Model", "Sprint Car", "Other"],
                                                        index=["Stock Car", "Modified", "Late Model", "Sprint Car",
                                                               "Other"].index(
                                                            current_vehicle.vehicle_type) if current_vehicle.vehicle_type in [
                                                            "Stock Car", "Modified", "Late Model", "Sprint Car",
                                                            "Other"] else 0)

                        col1, col2 = st.columns(2)
                        with col1:
                            new_track_width = st.number_input("Track Width (inches)",
                                                              min_value=0.0,
                                                              value=current_vehicle.track_width,
                                                              step=0.1)
                        with col2:
                            new_tire_circumference = st.number_input("Inside Tire Circumference (inches)",
                                                                     min_value=0.0,
                                                                     value=current_vehicle.tire_circumference,
                                                                     step=0.1)

                        if st.form_submit_button("💾 Update Vehicle"):
                            # CREATE UPDATED VEHICLE AND VALIDATE
                            updated_vehicle = VehicleEntity(new_vehicle_name, new_vehicle_type, new_track_width,
                                                            new_tire_circumference)
                            is_valid, error_msg = updated_vehicle.validate()

                            if not is_valid:
                                st.error(f"❌ {error_msg}")
                            else:
                                success, message = db.update_vehicle(
                                    vehicle_id=vehicle_id,
                                    user_id=st.session_state.user['id'],
                                    vehicle_name=updated_vehicle.name,
                                    track_width=updated_vehicle.track_width,
                                    inside_tire_circumference=updated_vehicle.tire_circumference,
                                    vehicle_type=updated_vehicle.vehicle_type
                                )

                                if success:
                                    st.success(f"✅ {message}")
                                    st.info(f"📋 Updated: {updated_vehicle.get_display_info()}")
                                    st.rerun()
                                else:
                                    st.error(message)
        else:
            st.info("No vehicles to edit. Add a vehicle first!")

    with tab3:
        st.subheader("Your Vehicles")

        vehicles = db.get_user_vehicles(st.session_state.user['id'])

        if vehicles:
            
            vehicle_objects = []
            for v in vehicles:
                if v[1] and v[2]:  # Has required data
                    vehicle_obj = VehicleEntity(v[0], v[3], float(v[1]), float(v[2]))
                    vehicle_objects.append(vehicle_obj)

            # # ENHANCED VEHICLE DISPLAY
            # if vehicle_objects:
            #     st.write("**📋 Vehicle Summary:**")
            #     display_entity_info(vehicle_objects)
            #
            #     # Enhanced validation
            #     if st.button("🔍 Validate All Vehicles"):
            #         validation_results = validate_entities(vehicle_objects)
            #         for result in validation_results:
            #             if result['valid']:
            #                 st.success(f"✅ {result['entity'].name}: {result['message']}")
            #             else:
            #                 st.error(f"❌ {result['entity'].name}: {result['message']}")

            # Regular display
            df = pd.DataFrame(vehicles, columns=['Name', 'Track Width', 'Tire Circumference', 'Type', 'Created'])
            df['Track Width'] = df['Track Width'].apply(lambda x: f"{x:.1f}\"" if x else "Not set")
            df['Tire Circumference'] = df['Tire Circumference'].apply(lambda x: f"{x:.1f}\"" if x else "Not set")
            df['Created'] = pd.to_datetime(df['Created']).dt.strftime('%Y-%m-%d')

            st.dataframe(df, use_container_width=True)

            # Delete functionality
            vehicle_to_delete = st.selectbox("Select vehicle to delete",
                                             ["Select..."] + [v[0] for v in vehicles])

            if vehicle_to_delete != "Select...":
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("🗑️ Delete Vehicle", type="secondary"):
                        vehicle_id = db.get_vehicle_id_by_name(st.session_state.user['id'], vehicle_to_delete)
                        if vehicle_id:
                            success, message = db.delete_vehicle(st.session_state.user['id'], vehicle_id)
                            if success:
                                st.success(f"Vehicle '{vehicle_to_delete}' deleted!")
                                st.rerun()
                            else:
                                st.error(message)
                with col2:
                    st.warning("⚠️ This action cannot be undone!")
        else:
            st.info("No vehicles found. Add your first vehicle above!")


def track_management():
    st.header("🏁 Track Management")

    tab1, tab2, tab3 = st.tabs(["Add Track", "Edit Track", "Manage Tracks"])

    with tab1:
        st.subheader("Add New Track")

        with st.form("add_track_form"):
            track_name = st.text_input("Track Name", placeholder="e.g., Bristol Motor Speedway")

            col1, col2 = st.columns(2)
            with col1:
                corner_length = st.number_input("Corner Length (feet)",
                                                min_value=0.0, value=400.0, step=10.0)
                banking = st.number_input("Banking (degrees)",
                                          min_value=0.0, max_value=90.0, value=0.0, step=0.1)
            with col2:
                surface_type = st.selectbox("Surface Type",
                                            ["asphalt", "concrete", "dirt", "clay", "other"])

            if st.form_submit_button("💾 Save Track"):
                # CREATE TRACK OBJECT AND VALIDATE
                track_obj = TrackEntity(track_name, corner_length, banking, surface_type)
                is_valid, error_msg = track_obj.validate()

                if not is_valid:
                    st.error(f"❌ {error_msg}")
                else:
                    success, message = db.save_track(
                        track_name=track_obj.name,
                        corner_length_ft=track_obj.corner_length,
                        banking_degrees=track_obj.banking,
                        surface_type=track_obj.surface_type,
                        user_id=st.session_state.user['id']
                    )

                    if success:
                        st.success(f"✅ {message}")
                        st.info(f"📋 Created: {track_obj.get_display_info()}")
                        st.rerun()
                    else:
                        st.error(message)

    with tab2:
        st.subheader("Edit Track")

        tracks = db.get_user_tracks(st.session_state.user['id'])

        if tracks:
            track_names = [t[0] for t in tracks]
            selected_track_name = st.selectbox("Select track to edit:",
                                               ["Select..."] + track_names)

            if selected_track_name != "Select...":
                # Get track data
                track_id = db.get_track_id_by_name(st.session_state.user['id'], selected_track_name)
                track_data = db.get_track_by_id(track_id, st.session_state.user['id'])

                if track_data:
                    # ENHANCED TRACK SELECTION INFO
                    current_track = TrackEntity(
                        track_data[1],
                        float(track_data[2]) if track_data[2] else 400.0,
                        float(track_data[3]) if track_data[3] else 0.0,
                        track_data[4] if track_data[4] else "asphalt"
                    )

                    # SHOW CURRENT TRACK INFO
                    #st.info(f"Current: {current_track.get_display_info()}")

                    with st.form("edit_track_form"):
                        st.write(f"Editing: **{selected_track_name}**")

                        new_track_name = st.text_input("Track Name", value=current_track.name)

                        col1, col2 = st.columns(2)
                        with col1:
                            new_corner_length = st.number_input("Corner Length (feet)",
                                                                min_value=0.0,
                                                                value=current_track.corner_length,
                                                                step=10.0)
                            new_banking = st.number_input("Banking (degrees)",
                                                          min_value=0.0, max_value=90.0,
                                                          value=current_track.banking,
                                                          step=0.1)
                        with col2:
                            new_surface_type = st.selectbox("Surface Type",
                                                            ["asphalt", "concrete", "dirt", "clay", "other"],
                                                            index=["asphalt", "concrete", "dirt", "clay",
                                                                   "other"].index(
                                                                current_track.surface_type) if current_track.surface_type in [
                                                                "asphalt", "concrete", "dirt", "clay", "other"] else 0)

                        if st.form_submit_button("💾 Update Track"):
                            # CREATE UPDATED TRACK AND VALIDATE
                            updated_track = TrackEntity(new_track_name, new_corner_length, new_banking,
                                                        new_surface_type)
                            is_valid, error_msg = updated_track.validate()

                            if not is_valid:
                                st.error(f"❌ {error_msg}")
                            else:
                                success, message = db.update_track(
                                    track_id=track_id,
                                    user_id=st.session_state.user['id'],
                                    track_name=updated_track.name,
                                    corner_length_ft=updated_track.corner_length,
                                    banking_degrees=updated_track.banking,
                                    surface_type=updated_track.surface_type
                                )

                                if success:
                                    st.success(f"✅ {message}")
                                    st.info(f"📋 Updated: {updated_track.get_display_info()}")
                                    st.rerun()
                                else:
                                    st.error(message)
        else:
            st.info("No tracks to edit. Add a track first!")

    with tab3:
        st.subheader("Your Tracks")

        tracks = db.get_user_tracks(st.session_state.user['id'])

        if tracks:
            # ENHANCED TRACK DISPLAY
            track_objects = []
            for t in tracks:
                if t[1] is not None and t[2] is not None:
                    track_obj = TrackEntity(t[0], float(t[1]), float(t[2]), t[3])
                    track_objects.append(track_obj)

            # if track_objects:
            #     st.write("**📋 Track Summary:**")
            #     display_entity_info(track_objects)
            #
            #     # Enhanced validation
            #     if st.button("🔍 Validate All Tracks"):
            #         validation_results = validate_entities(track_objects)
            #         for result in validation_results:
            #             if result['valid']:
            #                 st.success(f"✅ {result['entity'].name}: {result['message']}")
            #             else:
            #                 st.error(f"❌ {result['entity'].name}: {result['message']}")

            # Create DataFrame for display
            df = pd.DataFrame(tracks, columns=['Name', 'Corner Length', 'Banking', 'Surface', 'Created'])
            df['Corner Length'] = df['Corner Length'].apply(lambda x: f"{x:.1f} ft" if x else "Not set")
            df['Banking'] = df['Banking'].apply(lambda x: f"{x:.1f}°" if x else "Not set")
            df['Created'] = pd.to_datetime(df['Created']).dt.strftime('%Y-%m-%d')

            st.dataframe(df, use_container_width=True)

            # Delete track
            track_to_delete = st.selectbox("Select track to delete",
                                           ["Select..."] + [t[0] for t in tracks])

            if track_to_delete != "Select...":
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("🗑️ Delete Track", type="secondary"):
                        track_id = db.get_track_id_by_name(st.session_state.user['id'], track_to_delete)
                        if track_id:
                            success, message = db.delete_track(st.session_state.user['id'], track_id)
                            if success:
                                st.success(f"Track '{track_to_delete}' deleted!")
                                st.rerun()
                            else:
                                st.error(message)
                with col2:
                    st.warning("⚠️ This action cannot be undone!")
        else:
            st.info("No tracks found. Add your first track above!")


def calculation_history():

    st.header("📊 Calculation History")

    calculations = db.get_user_calculations(st.session_state.user['id'], limit=50)

    if calculations:
        # Create DataFrame
        df = pd.DataFrame(calculations, columns=[
            'Track Width', 'Corner Length', 'Inside Tire Circ', 'Banking',
            'Calculated Stagger', 'Outside Tire Circ', 'Date', 'Notes'
        ])

        # Format columns
        df['Track Width'] = df['Track Width'].apply(lambda x: f"{x:.1f}\"")
        df['Corner Length'] = df['Corner Length'].apply(lambda x: f"{x:.1f} ft")
        df['Inside Tire Circ'] = df['Inside Tire Circ'].apply(lambda x: f"{x:.1f}\"")
        df['Banking'] = df['Banking'].apply(lambda x: f"{x:.1f}°")
        df['Calculated Stagger'] = df['Calculated Stagger'].apply(lambda x: f"{x:.3f}\"")
        df['Outside Tire Circ'] = df['Outside Tire Circ'].apply(lambda x: f"{x:.3f}\"")
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d %H:%M')
        df['Notes'] = df['Notes'].fillna('')

        # Filters
        st.subheader("Filters")
        col1, col2, col3 = st.columns(3)

        with col1:
            min_stagger = st.number_input("Min Stagger", value=0.0, step=0.1)
        with col2:
            max_stagger = st.number_input("Max Stagger", value=10.0, step=0.1)
        with col3:
            search_notes = st.text_input("Search in Notes")

        # Apply filters
        filtered_df = df.copy()
        stagger_values = df['Calculated Stagger'].str.replace('"', '').astype(float)
        filtered_df = filtered_df[(stagger_values >= min_stagger) & (stagger_values <= max_stagger)]

        if search_notes:
            filtered_df = filtered_df[filtered_df['Notes'].str.contains(search_notes, case=False, na=False)]

        st.subheader(f"Results ({len(filtered_df)} calculations)")
        st.dataframe(filtered_df, use_container_width=True)

        # Export functionality
        if st.button("📥 Export to CSV"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"stagger_history_{st.session_state.user['username']}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No calculations found. Start calculating!")


def main_calculator():

    st.title(f"🏁 Stagger Calculator - {st.session_state.user['username']}")

    # Sidebar
    with st.sidebar:
        st.markdown(f"**User:** {st.session_state.user['username']}")
        st.markdown(f"**Team:** {st.session_state.user['team_name']}")

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()

    # Load vehicles and tracks
    vehicle_options, vehicles = load_user_vehicles()
    track_options, tracks = load_user_tracks()

    # Main calculator
    st.header("Calculator")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Input Parameters")

        # Vehicle Selection
        selected_vehicle = st.selectbox("Select Vehicle:", vehicle_options,
                                        index=vehicle_options.index(st.session_state.selected_vehicle)
                                        if st.session_state.selected_vehicle in vehicle_options else 0)

        if selected_vehicle != st.session_state.selected_vehicle:
            st.session_state.selected_vehicle = selected_vehicle
            st.rerun()

        # Track Selection
        selected_track = st.selectbox("Select Track:", track_options,
                                      index=track_options.index(st.session_state.selected_track)
                                      if st.session_state.selected_track in track_options else 0)

        if selected_track != st.session_state.selected_track:
            st.session_state.selected_track = selected_track
            st.rerun()

        if selected_vehicle != "Manual Entry":
            vehicle_data = get_vehicle_data(selected_vehicle, vehicles)
            if vehicle_data:
                selected_vehicle_obj = VehicleEntity(
                    selected_vehicle,
                    vehicle_data['vehicle_type'],
                    vehicle_data['track_width'],
                    vehicle_data['inside_tire_circumference']
                )
                st.info(f"🚗 Using: {selected_vehicle_obj.get_specs_summary()}")

        if selected_track != "Manual Entry":
            track_data = get_track_data(selected_track, tracks)
            if track_data:
                selected_track_obj = TrackEntity(
                    selected_track,
                    track_data['corner_length_ft'],
                    track_data['banking_degrees'],
                    track_data['surface_type']
                )
                st.info(f"🏁 Using: {selected_track_obj.get_specs_summary()}")



        # Get pre-filled values
        vehicle_data = get_vehicle_data(selected_vehicle, vehicles) if selected_vehicle != "Manual Entry" else None
        track_data = get_track_data(selected_track, tracks) if selected_track != "Manual Entry" else None

        # Input fields with pre-filled values
        track_width = st.number_input(
            "Track Width (inches)",
            min_value=30.0,
            max_value=100.0,
            value=float(vehicle_data['track_width']) if vehicle_data and vehicle_data['track_width'] else 60.0,
            step=0.1
        )

        corner_length = st.number_input(
            "Corner Length (feet)",
            min_value=200.0,
            max_value=1500.0,
            value=float(track_data['corner_length_ft']) if track_data and track_data['corner_length_ft'] else 400.0,
            step=10.0,
            help="Arc distance through the corner along the racing line"
        )

        tire_circumference = st.number_input(
            "Inside Tire Circumference (inches)",
            min_value=60.0,
            max_value=120.0,
            value=float(vehicle_data['inside_tire_circumference']) if vehicle_data and vehicle_data[
                'inside_tire_circumference'] else 82.5,
            step=0.1
        )

        has_banking = st.checkbox("Track has banking",
                                  value=bool(track_data and track_data['banking_degrees'] and track_data[
                                      'banking_degrees'] > 0))

        if has_banking:
            banking = st.number_input(
                "Banking (degrees)",
                min_value=0.0,
                max_value=45.0,
                value=float(track_data['banking_degrees']) if track_data and track_data['banking_degrees'] else 0.0,
                step=0.1
            )
        else:
            banking = 0.0

        # Calculate button
        if st.button("🧮 Calculate Stagger", type="primary"):
            result = calculate_stagger_smart_angle(
                track_width,
                corner_length,
                tire_circumference,
                banking
            )

            if result[0] is not None:
                stagger, outside_circ, calculated_angle, track_type = result

                st.session_state.last_calculation = {
                    'stagger': stagger,
                    'outside_circ': outside_circ,
                    'track_width': track_width,
                    'corner_length': corner_length,
                    'tire_circumference': tire_circumference,
                    'banking': banking,
                    'calculated_angle': calculated_angle,
                    'track_type': track_type,
                    'calculated_radius': corner_length / math.radians(calculated_angle)
                }

    with col2:
        st.subheader("Results")

        if 'last_calculation' in st.session_state:
            calc = st.session_state.last_calculation

            # Display main results
            st.markdown("### Calculated Stagger")
            st.markdown(f"<h2 style='color: #1f77b4;'>{calc['stagger']:.3f}\"</h2>",
                        unsafe_allow_html=True)

            st.markdown("### Outside Tire Size")
            st.markdown(f"<h3 style='color: #ff7f0e;'>{calc['outside_circ']:.3f}\"</h3>",
                        unsafe_allow_html=True)

            # Save calculation
            st.markdown("---")
            notes = st.text_area("Notes (optional)")

            if st.button("💾 Save Calculation"):
                try:
                    success, message = db.save_calculation(
                        track_width=calc['track_width'],
                        corner_length_ft=calc['corner_length'],
                        inside_tire_circumference=calc['tire_circumference'],
                        banking_degrees=calc['banking'],
                        calculated_stagger=calc['stagger'],
                        outside_tire_circumference=calc['outside_circ'],
                        notes=notes,
                        user_id=st.session_state.user['id']
                    )

                    if success:
                        st.success("Calculation saved!")
                        # Clear calculation to prevent duplicate saves
                        if 'last_calculation' in st.session_state:
                            del st.session_state.last_calculation
                    else:
                        st.error(f"Error saving: {message}")
                except Exception as e:
                    st.error(f"Save error: {e}")

        else:
            st.info("Enter parameters and click Calculate to see results")


# Main app logic
def main():

    try:
        if not st.session_state.authenticated:
            simple_login()
        else:
            # Create navigation
            tab1, tab2, tab3, tab4 = st.tabs(["🧮 Calculator", "🚗 Vehicles", "🏁 Tracks", "📊 History"])

            with tab1:
                main_calculator()

            with tab2:
                vehicle_management()

            with tab3:
                track_management()

            with tab4:
                calculation_history()

    except Exception as e:
        st.error(f"Application error: {e}")
        st.write("**Error details:**")
        import traceback
        st.code(traceback.format_exc())


if __name__ == "__main__":
    main()