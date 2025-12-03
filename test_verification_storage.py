#!/usr/bin/env python
"""Test verification storage system"""

import json
import os
from app import verify_vehicle, get_images, load_verifications

# Clean up old log for fresh test
if os.path.exists('verification_log.json'):
    os.remove('verification_log.json')

print("=" * 60)
print("TESTING VERIFICATION STORAGE SYSTEM")
print("=" * 60)

# Test 1: Verify an authorized vehicle
print("\n[TEST 1] Verify authorized vehicle...")
result1 = verify_vehicle("MH12AB1234", "test_image_1.jpg")
print(f"  Plate: {result1['plate']}")
print(f"  Status: {result1['alert_type'].upper()}")
print(f"  Message: {result1['message']}")

# Test 2: Verify an unauthorized vehicle
print("\n[TEST 2] Verify unauthorized vehicle...")
result2 = verify_vehicle("XX99YY5555", "test_image_2.jpg")
print(f"  Plate: {result2['plate']}")
print(f"  Status: {result2['alert_type'].upper()}")
print(f"  Message: {result2['message']}")

# Test 3: Check verification log contents
print("\n[TEST 3] Load verification records...")
verifications = load_verifications()
print(f"  Total records: {len(verifications)}")
for i, v in enumerate(verifications, 1):
    print(f"  {i}. {v['plate']} - {'AUTHORIZED' if v['is_authorized'] else 'UNAUTHORIZED'} ({v['timestamp']})")

# Test 4: Check get_images output (what template receives)
print("\n[TEST 4] Get images (template format)...")
images = get_images()
print(f"  Total images: {len(images)}")
for i, (filename, date, plate, is_auth) in enumerate(images, 1):
    print(f"  {i}. Plate: {plate} | Date: {date} | Status: {'✓' if is_auth else '✗'}")

# Test 5: Verify JSON file exists
print("\n[TEST 5] Verify JSON file...")
if os.path.exists('verification_log.json'):
    with open('verification_log.json', 'r') as f:
        data = json.load(f)
    print(f"  ✓ verification_log.json exists")
    print(f"  ✓ Contains {len(data['verifications'])} records")
else:
    print(f"  ✗ verification_log.json not found")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED!")
print("=" * 60)
