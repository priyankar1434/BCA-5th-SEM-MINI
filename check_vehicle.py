import json
import os
from datetime import datetime

class VehicleValidator:
    def __init__(self, db_file='vehicle_database.json'):
        """Initialize the vehicle validator with the database file."""
        self.db_file = db_file
        self.history_file = 'verification_history.json'
        self._ensure_database_exists()
        self.authorized_vehicles = self._load_vehicles()
        self.verification_history = self._load_history()
    
    def _ensure_database_exists(self):
        """Create an empty database file if it doesn't exist."""
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w') as f:
                json.dump({"authorized_vehicles": []}, f, indent=4)
    
    def _load_vehicles(self):
        """Load the list of authorized vehicles from the JSON file."""
        try:
            with open(self.db_file, 'r') as f:
                data = json.load(f)
                # Convert all vehicle numbers to uppercase for case-insensitive comparison
                return [v.upper() for v in data.get('authorized_vehicles', [])]
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _load_history(self):
        """Load verification history from file."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        return []
    
    def _save_history(self):
        """Save verification history to file."""
        with open(self.history_file, 'w') as f:
            json.dump(self.verification_history, f, indent=4, default=str)
    
    def is_vehicle_authorized(self, vehicle_number):
        """Check if a vehicle number is in the authorized list and log the verification."""
        is_authorized = vehicle_number.upper() in self.authorized_vehicles
        
        # Log this verification
        verification = {
            'vehicle_number': vehicle_number.upper(),
            'status': 'AUTHORIZED' if is_authorized else 'UNAUTHORIZED',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'date': datetime.now().strftime("%Y-%m-%d")
        }
        
        self.verification_history.append(verification)
        # Keep only the last 100 entries to prevent the file from growing too large
        self.verification_history = self.verification_history[-100:]
        self._save_history()
        
        return is_authorized
    
    def add_vehicle(self, vehicle_number):
        """Add a new vehicle number to the authorized list."""
        if not self.is_vehicle_authorized(vehicle_number):
            self.authorized_vehicles.append(vehicle_number.upper())
            self._save_vehicles()
            return True
        return False
    
    def remove_vehicle(self, vehicle_number):
        """Remove a vehicle number from the authorized list."""
        vehicle_upper = vehicle_number.upper()
        if vehicle_upper in self.authorized_vehicles:
            self.authorized_vehicles.remove(vehicle_upper)
            self._save_vehicles()
            return True
        return False
    
    def _save_vehicles(self):
        """Save the current list of authorized vehicles to the JSON file."""
        with open(self.db_file, 'w') as f:
            json.dump({"authorized_vehicles": sorted(self.authorized_vehicles)}, f, indent=4)
    
    def get_all_vehicles(self):
        """Get all authorized vehicles."""
        return sorted(self.authorized_vehicles)
        
    def get_verification_history(self, limit=10):
        """Get recent verification history."""
        return self.verification_history[-limit:][::-1]  # Return most recent first

def main():
    # Initialize the vehicle validator
    validator = VehicleValidator()
    
    print("Vehicle Authorization System")
    print("-" * 30)
    print(f"Total Authorized Vehicles: {len(validator.authorized_vehicles)}\n")
    
    while True:
        print("\nOptions:")
        print("1. Check Vehicle")
        print("2. Add Vehicle")
        print("3. Remove Vehicle")
        print("4. View All Vehicles")
        print("5. View Verification History")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            vehicle_number = input("Enter vehicle number: ").strip()
            if validator.is_vehicle_authorized(vehicle_number):
                print(f"✓ SUCCESS: {vehicle_number} is AUTHORIZED")
            else:
                print(f"✗ ALERT: {vehicle_number} is UNAUTHORIZED")
        
        elif choice == '2':
            vehicle_number = input("Enter vehicle number to add: ").strip()
            if validator.add_vehicle(vehicle_number):
                print(f"✓ Vehicle {vehicle_number} added successfully")
            else:
                print(f"✗ Vehicle {vehicle_number} already exists")
        
        elif choice == '3':
            vehicle_number = input("Enter vehicle number to remove: ").strip()
            if validator.remove_vehicle(vehicle_number):
                print(f"✓ Vehicle {vehicle_number} removed successfully")
            else:
                print(f"✗ Vehicle {vehicle_number} not found")
        
        elif choice == '4':
            vehicles = validator.get_all_vehicles()
            print(f"\nAuthorized Vehicles ({len(vehicles)}):")
            for i, vehicle in enumerate(vehicles, 1):
                print(f"  {i}. {vehicle}")
        
        elif choice == '5':
            print("\nRecent Verification History:")
            print("-" * 50)
            print(f"{'Date/Time':<20} | {'Vehicle Number':<15} | {'Status'}")
            print("-" * 50)
            for entry in validator.get_verification_history(10):
                print(f"{entry['timestamp']:<20} | {entry['vehicle_number']:<15} | {entry['status']}")
            
        elif choice == '6':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
    
    while True:
        print("\nOptions:")
        print("1. Check vehicle authorization")
        print("2. Add new authorized vehicle")
        print("3. List all authorized vehicles")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            vehicle_num = input("\nEnter vehicle number: ").strip()
            if validator.is_vehicle_authorized(vehicle_num):
                print(f"\n✅ Vehicle {vehicle_num.upper()} is AUTHORIZED.")
            else:
                print(f"\n❌ Vehicle {vehicle_num.upper()} is NOT AUTHORIZED.")
                
        elif choice == '2':
            vehicle_num = input("\nEnter vehicle number to authorize: ").strip()
            if validator.add_vehicle(vehicle_num):
                print(f"\n✅ Vehicle {vehicle_num.upper()} has been added to the authorized list.")
            else:
                print(f"\nℹ️ Vehicle {vehicle_num.upper()} is already in the authorized list.")
                
        elif choice == '3':
            print("\nAuthorized Vehicles:")
            print("-" * 20)
            if not validator.authorized_vehicles:
                print("No vehicles in the database.")
            else:
                for i, vehicle in enumerate(sorted(validator.authorized_vehicles), 1):
                    print(f"{i}. {vehicle}")
                    
        elif choice == '4':
            print("\nExiting...")
            break
            
        else:
            print("\n❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
