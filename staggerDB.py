import sqlite3
import hashlib
import secrets
from datetime import datetime


class StaggerDatabase:
    def __init__(self, db_name='stagger_calculator.db'):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        # initialize db
        conn = None
        try:
            conn = sqlite3.connect(self.db_name, timeout=10.0)
            cursor = conn.cursor()

            # Enable WAL mode for better concurrency
            cursor.execute('PRAGMA journal_mode=WAL;')

            # Check if this is a new database or needs migration
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
            users_table_exists = cursor.fetchone() is not None

            if not users_table_exists:
                # New database - create all tables with proper schema
                self.create_new_database_schema(cursor)
            else:
                # Existing database - check if migration is needed
                self.migrate_existing_database(cursor)

            conn.commit()
            print(f"Database initialized: {self.db_name}")

        except Exception as e:
            print(f"Error initializing database: {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

        # Create demo user if it doesn't exist
        self.create_demo_user()

    def create_new_database_schema(self, cursor):

        # Users table for authentication
        cursor.execute('''
                       CREATE TABLE users
                       (
                           id            INTEGER PRIMARY KEY,
                           username      TEXT UNIQUE NOT NULL,
                           email         TEXT UNIQUE NOT NULL,
                           password_hash TEXT        NOT NULL,
                           salt          TEXT        NOT NULL,
                           team_name     TEXT,
                           created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           last_login    TIMESTAMP
                       )
                       ''')

        # Calculations table with user_id
        cursor.execute('''
                       CREATE TABLE calculations
                       (
                           id                         INTEGER PRIMARY KEY,
                           user_id                    INTEGER,
                           track_width                REAL,
                           corner_length_ft           REAL,
                           inside_tire_circumference  REAL,
                           banking_degrees            REAL      DEFAULT 0,
                           calculated_stagger         REAL,
                           outside_tire_circumference REAL,
                           calculation_date           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           notes                      TEXT,
                           FOREIGN KEY (user_id) REFERENCES users (id)
                       )
                       ''')

        # Tracks table with user_id
        cursor.execute('''
                       CREATE TABLE tracks
                       (
                           id               INTEGER PRIMARY KEY,
                           user_id          INTEGER,
                           track_name       TEXT,
                           corner_length_ft REAL,
                           banking_degrees  REAL      DEFAULT 0,
                           surface_type     TEXT      DEFAULT 'asphalt',
                           created_date     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           FOREIGN KEY (user_id) REFERENCES users (id)
                       )
                       ''')

        # Vehicles table with user_id
        cursor.execute('''
                       CREATE TABLE vehicles
                       (
                           id                        INTEGER PRIMARY KEY,
                           user_id                   INTEGER,
                           vehicle_name              TEXT,
                           track_width               REAL,
                           inside_tire_circumference REAL,
                           vehicle_type              TEXT      DEFAULT 'Stock Car',
                           created_date              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           FOREIGN KEY (user_id) REFERENCES users (id)
                       )
                       ''')

    def migrate_existing_database(self, cursor):

        print("Checking database schema for migrations...")

        # Check if calculations table has user_id column
        cursor.execute("PRAGMA table_info(calculations)")
        calc_columns = [column[1] for column in cursor.fetchall()]

        if 'user_id' not in calc_columns:
            print("Migrating calculations table...")
            # Add user_id column to calculations table
            cursor.execute('ALTER TABLE calculations ADD COLUMN user_id INTEGER')

            # Set all existing calculations to demo user (id = 1) if it exists
            cursor.execute("SELECT id FROM users WHERE username = 'demo'")
            demo_user = cursor.fetchone()
            if demo_user:
                cursor.execute('UPDATE calculations SET user_id = ? WHERE user_id IS NULL', (demo_user[0],))
                print("Assigned existing calculations to demo user")

        # Check if tracks table has user_id column
        cursor.execute("PRAGMA table_info(tracks)")
        track_columns = [column[1] for column in cursor.fetchall()]

        if 'user_id' not in track_columns:
            print("Migrating tracks table...")
            cursor.execute('ALTER TABLE tracks ADD COLUMN user_id INTEGER')

            # Set all existing tracks to demo user if it exists
            cursor.execute("SELECT id FROM users WHERE username = 'demo'")
            demo_user = cursor.fetchone()
            if demo_user:
                cursor.execute('UPDATE tracks SET user_id = ? WHERE user_id IS NULL', (demo_user[0],))
                print("Assigned existing tracks to demo user")

        # Check if vehicles table has user_id column
        cursor.execute("PRAGMA table_info(vehicles)")
        vehicle_columns = [column[1] for column in cursor.fetchall()]

        if 'user_id' not in vehicle_columns:
            print("Migrating vehicles table...")
            cursor.execute('ALTER TABLE vehicles ADD COLUMN user_id INTEGER')

            # Set all existing vehicles to demo user if it exists
            cursor.execute("SELECT id FROM users WHERE username = 'demo'")
            demo_user = cursor.fetchone()
            if demo_user:
                cursor.execute('UPDATE vehicles SET user_id = ? WHERE user_id IS NULL', (demo_user[0],))
                print("Assigned existing vehicles to demo user")

    def get_database_info(self):

        try:
            conn = sqlite3.connect(self.db_name, timeout=10.0)
            cursor = conn.cursor()

            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [table[0] for table in cursor.fetchall()]

            print(f"Database tables: {tables}")

            # Check structure of each table
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                print(f"Table '{table}' columns: {[col[1] for col in columns]}")

            conn.close()

        except Exception as e:
            print(f"Error getting database info: {e}")

    def create_demo_user(self):

        try:
            # Check if demo user already exists first
            conn = sqlite3.connect(self.db_name, timeout=10.0)
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE username = ?', ('demo',))
            existing = cursor.fetchone()
            conn.close()

            if existing:
                print("Demo user already exists")
                return

            # Create demo user
            success, user_id, message = self.create_user("demo", "demo@test.com", "demo123", "Demo Racing Team")
            if success:
                print("Demo user created successfully")
            else:
                print(f"Demo user creation failed: {message}")
        except Exception as e:
            print(f"Error creating demo user: {e}")

    # ================== USER AUTHENTICATION METHODS ==================

    def create_user(self, username, email, password, team_name):

        conn = None
        try:
            # Generate salt and hash password
            salt = secrets.token_hex(16)
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)

            conn = sqlite3.connect(self.db_name, timeout=10.0)  # Add timeout
            cursor = conn.cursor()

            cursor.execute('''
                           INSERT INTO users (username, email, password_hash, salt, team_name)
                           VALUES (?, ?, ?, ?, ?)
                           ''', (username, email, password_hash.hex(), salt, team_name))

            conn.commit()
            user_id = cursor.lastrowid
            return True, user_id, "Account created successfully!"

        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                return False, None, "Username already exists!"
            elif "email" in str(e):
                return False, None, "Email already registered!"
            else:
                return False, None, "Registration failed!"
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                print(f"Database locked error in create_user: {e}")
                return False, None, "Database is busy, please try again."
            else:
                return False, None, f"Database error: {e}"
        except Exception as e:
            return False, None, f"Error creating user: {e}"
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

    def authenticate_user(self, username, password):

        conn = None
        try:
            conn = sqlite3.connect(self.db_name, timeout=10.0)  # Add timeout
            cursor = conn.cursor()

            cursor.execute('''
                           SELECT id, username, password_hash, salt, team_name, email
                           FROM users
                           WHERE username = ?
                           ''', (username,))

            user = cursor.fetchone()

            if user:
                stored_hash = user[2]
                salt = user[3]
                password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)

                if password_hash.hex() == stored_hash:
                    # Update last login
                    cursor.execute('UPDATE users SET last_login = ? WHERE id = ?',
                                   (datetime.now(), user[0]))
                    conn.commit()

                    return {
                        'id': user[0],
                        'username': user[1],
                        'team_name': user[4],
                        'email': user[5]
                    }

            return None

        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                print(f"Database locked error in authenticate_user: {e}")
                # Try again after a short delay
                import time
                time.sleep(0.1)
                return None
            else:
                print(f"Database operational error in authenticate_user: {e}")
                return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

    # ================== UPDATED CALCULATION METHODS ==================

    def save_calculation(self, track_width, corner_length_ft, inside_tire_circumference,
                         banking_degrees, calculated_stagger, outside_tire_circumference,
                         notes="", user_id=None):

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute('''
                           INSERT INTO calculations
                           (user_id, track_width, corner_length_ft, inside_tire_circumference, banking_degrees,
                            calculated_stagger, outside_tire_circumference, notes)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                           ''', (user_id, track_width, corner_length_ft, inside_tire_circumference, banking_degrees,
                                 calculated_stagger, outside_tire_circumference, notes))

            conn.commit()
            conn.close()
            return True, "Calculation saved successfully!"

        except Exception as e:
            return False, f"Error saving calculation: {e}"

    def get_calculations(self, user_id=None, limit=20):
        """Get calculation history (optionally filtered by user)"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            if user_id:
                cursor.execute('''
                               SELECT track_width,
                                      corner_length_ft,
                                      inside_tire_circumference,
                                      banking_degrees,
                                      calculated_stagger,
                                      outside_tire_circumference,
                                      calculation_date,
                                      notes
                               FROM calculations
                               WHERE user_id = ?
                               ORDER BY calculation_date DESC LIMIT ?
                               ''', (user_id, limit))
            else:
                cursor.execute('''
                               SELECT track_width,
                                      corner_length_ft,
                                      inside_tire_circumference,
                                      banking_degrees,
                                      calculated_stagger,
                                      outside_tire_circumference,
                                      calculation_date,
                                      notes
                               FROM calculations
                               ORDER BY calculation_date DESC LIMIT ?
                               ''', (limit,))

            calculations = cursor.fetchall()
            conn.close()
            return calculations

        except Exception as e:
            print(f"Error getting calculations: {e}")
            return []

    def get_user_calculations(self, user_id, limit=20):

        return self.get_calculations(user_id=user_id, limit=limit)

    # ================== UPDATED TRACK METHODS ==================

    def save_track(self, track_name, corner_length_ft, banking_degrees=0, surface_type="asphalt", user_id=None):

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute('''
                           INSERT INTO tracks (user_id, track_name, corner_length_ft, banking_degrees, surface_type)
                           VALUES (?, ?, ?, ?, ?)
                           ''', (user_id, track_name, corner_length_ft, banking_degrees, surface_type))

            conn.commit()
            conn.close()
            return True, f"Track '{track_name}' saved successfully!"

        except sqlite3.IntegrityError:
            return False, "Track name already exists!"
        except Exception as e:
            return False, f"Error saving track: {e}"

    def get_tracks(self, user_id=None):

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            if user_id:
                cursor.execute('''
                               SELECT track_name, corner_length_ft, banking_degrees, surface_type, created_date
                               FROM tracks
                               WHERE user_id = ?
                               ORDER BY track_name
                               ''', (user_id,))
            else:
                cursor.execute('''
                               SELECT track_name, corner_length_ft, banking_degrees, surface_type, created_date
                               FROM tracks
                               ORDER BY track_name
                               ''')

            tracks = cursor.fetchall()
            conn.close()
            return tracks

        except Exception as e:
            print(f"Error getting tracks: {e}")
            return []

    def get_user_tracks(self, user_id):

        return self.get_tracks(user_id=user_id)

    # ================== UPDATED VEHICLE METHODS ==================

    def save_vehicle(self, vehicle_name, track_width, inside_tire_circumference, vehicle_type="Stock Car",
                     user_id=None):

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute('''
                           INSERT INTO vehicles (user_id, vehicle_name, track_width, inside_tire_circumference,
                                                 vehicle_type)
                           VALUES (?, ?, ?, ?, ?)
                           ''', (user_id, vehicle_name, track_width, inside_tire_circumference, vehicle_type))

            conn.commit()
            conn.close()
            return True, f"Vehicle '{vehicle_name}' saved successfully!"

        except sqlite3.IntegrityError:
            return False, "Vehicle name already exists!"
        except Exception as e:
            return False, f"Error saving vehicle: {e}"

    def get_vehicles(self, user_id=None):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            if user_id:
                cursor.execute('''
                               SELECT vehicle_name, track_width, inside_tire_circumference, vehicle_type, created_date
                               FROM vehicles
                               WHERE user_id = ?
                               ORDER BY vehicle_name
                               ''', (user_id,))
            else:
                cursor.execute('''
                               SELECT vehicle_name, track_width, inside_tire_circumference, vehicle_type, created_date
                               FROM vehicles
                               ORDER BY vehicle_name
                               ''')

            vehicles = cursor.fetchall()
            conn.close()
            return vehicles

        except Exception as e:
            print(f"Error getting vehicles: {e}")
            return []

    def get_user_vehicles(self, user_id):

        return self.get_vehicles(user_id=user_id)

    # Add these methods to your StaggerDatabase class in staggerDB.py:

    def get_vehicle_id_by_name(self, user_id, vehicle_name):
        """Get vehicle ID by name for a specific user"""
        try:
            conn = sqlite3.connect(self.db_name, timeout=10.0)
            cursor = conn.cursor()

            cursor.execute('''
                           SELECT id
                           FROM vehicles
                           WHERE user_id = ?
                             AND vehicle_name = ?
                           ''', (user_id, vehicle_name))

            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None

        except Exception as e:
            print(f"Error getting vehicle ID: {e}")
            return None

    def get_vehicle_by_id(self, vehicle_id, user_id):
        """Get a specific vehicle by ID (for editing)"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute('''
                           SELECT id, vehicle_name, track_width, inside_tire_circumference, vehicle_type, created_date
                           FROM vehicles
                           WHERE id = ?
                             AND user_id = ?
                           ''', (vehicle_id, user_id))

            vehicle = cursor.fetchone()
            conn.close()
            return vehicle

        except Exception as e:
            print(f"Error getting vehicle by ID: {e}")
            return None

    def update_vehicle(self, vehicle_id, user_id, vehicle_name, track_width, inside_tire_circumference, vehicle_type):
        """Update an existing vehicle"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute('''
                           UPDATE vehicles
                           SET vehicle_name              = ?,
                               track_width               = ?,
                               inside_tire_circumference = ?,
                               vehicle_type              = ?
                           WHERE id = ?
                             AND user_id = ?
                           ''',
                           (vehicle_name, track_width, inside_tire_circumference, vehicle_type, vehicle_id, user_id))

            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return True, f"Vehicle '{vehicle_name}' updated successfully!"
            else:
                conn.close()
                return False, "Vehicle not found or access denied!"

        except sqlite3.IntegrityError as e:
            if "vehicle_name" in str(e).lower():
                return False, "Vehicle name already exists!"
            else:
                return False, f"Database constraint error: {e}"
        except Exception as e:
            return False, f"Error updating vehicle: {e}"


    def delete_vehicle(self, user_id, vehicle_id):
        """Delete a vehicle (only if user owns it)"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name, timeout=10.0)
            cursor = conn.cursor()

            cursor.execute('DELETE FROM vehicles WHERE id = ? AND user_id = ?', (vehicle_id, user_id))

            if cursor.rowcount > 0:
                conn.commit()
                return True, "Vehicle deleted successfully!"
            else:
                return False, "Vehicle not found or access denied!"

        except Exception as e:
            return False, f"Error deleting vehicle: {e}"
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass


    def get_track_id_by_name(self, user_id, track_name):

        try:
            conn = sqlite3.connect(self.db_name, timeout=10.0)
            cursor = conn.cursor()

            cursor.execute('''
                           SELECT id
                           FROM tracks
                           WHERE user_id = ? AND track_name = ?
                           ''', (user_id, track_name))

            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None

        except Exception as e:
            print(f"Error getting track ID: {e}")
            return None

    def get_track_by_id(self, track_id, user_id):

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute('''
                           SELECT id, track_name, corner_length_ft, banking_degrees, surface_type, created_date
                           FROM tracks
                           WHERE id = ? AND user_id = ?
                           ''', (track_id, user_id))

            track = cursor.fetchone()
            conn.close()
            return track

        except Exception as e:
            print(f"Error getting track by ID: {e}")
            return None


if __name__ == "__main__":
    # Test the database
    print("Testing StaggerDatabase...")
    db = StaggerDatabase("test_stagger.db")

    # Test authentication
    user = db.authenticate_user("demo", "demo123")
    if user:
        print(f"Demo user authenticated: {user}")

        # Test saving a calculation
        success, msg = db.save_calculation(60, 200, 82, 12, 1.25, 83.25, "Test calculation", user['id'])
        print(f"Save calculation: {msg}")

        # Test getting calculations
        calculations = db.get_user_calculations(user['id'])
        print(f"Found {len(calculations)} calculations for user")
    else:
        print("Demo user authentication failed")

    print("Database test complete!")



