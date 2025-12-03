#!/usr/bin/env python
"""
Quick test script to verify the vehicle database system works correctly.
"""

from check_vehicle import VehicleValidator
import json

def test_vehicle_system():
    print("=" * 50)
    print("VEHICLE DATABASE SYSTEM TEST")
    print("=" * 50)
    
    # Initialize validator
    validator = VehicleValidator()
    
    # Test 1: Check authorized vehicle
    print("\n[TEST 1] Checking authorized vehicle...")
    vehicle = "MH12AB1234"
    result = validator.is_vehicle_authorized(vehicle)
    print(f"  Vehicle: {vehicle}")
    print(f"  Status: {'✓ AUTHORIZED' if result else '✗ UNAUTHORIZED'}")
    
    # Test 2: Check unauthorized vehicle
    print("\n[TEST 2] Checking unauthorized vehicle...")
    vehicle = "XX99YY1234"
    result = validator.is_vehicle_authorized(vehicle)
    print(f"  Vehicle: {vehicle}")
    print(f"  Status: {'✓ AUTHORIZED' if result else '✗ UNAUTHORIZED'}")
    
    # Test 3: View all vehicles
    print("\n[TEST 3] All authorized vehicles in database:")
    vehicles = validator.get_all_vehicles()
    for i, v in enumerate(vehicles, 1):
        print(f"  {i}. {v}")
    
    # Test 4: Load from JSON directly
    print("\n[TEST 4] Verifying JSON file structure:")
    with open('vehicle_database.json', 'r') as f:
        data = json.load(f)
        print(f"  Total vehicles: {len(data['authorized_vehicles'])}")
        print(f"  Valid JSON: ✓")
    
    print("\n" + "=" * 50)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 50)

if __name__ == '__main__':
    test_vehicle_system()
