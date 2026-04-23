#!/usr/bin/env python3
"""
Test script for AriTyper monetization flow
Tests the complete payment and licensing system
"""
import os
import json
import tempfile
from datetime import datetime, timedelta
from license_manager import LicenseManager, AdminLicenseManager
from payment_window import PAYMENT_INFO

def test_device_id_generation():
    """Test device ID generation"""
    print("🔧 Testing Device ID Generation...")
    
    lm = LicenseManager()
    device_id = lm.get_device_id()
    
    print(f"✅ Generated Device ID: {device_id}")
    
    # Test consistency
    lm2 = LicenseManager()
    device_id2 = lm2.get_device_id()
    
    if device_id == device_id2:
        print("✅ Device ID generation is consistent")
    else:
        print("❌ Device ID generation is inconsistent")
        return False
    
    return True

def test_license_validation():
    """Test license validation"""
    print("\n🔐 Testing License Validation...")
    
    lm = LicenseManager()
    
    # Test no license
    result = lm.validate_license()
    if not result.get('valid') and 'No license found' in result.get('message', ''):
        print("✅ Correctly detects no license")
    else:
        print("❌ Failed to detect no license")
        return False
    
    return True

def test_payment_submission():
    """Test payment submission"""
    print("\n💳 Testing Payment Submission...")
    
    # Test phone validation
    from payment_window import PaymentWindow
    
    # Create a dummy root for testing
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        
        pw = PaymentWindow(root, "ARI-TEST123456")
        
        # Test Uganda phone validation
        test_phones = [
            ("0772123456", True),
            ("0782123456", True), 
            ("0752123456", True),
            ("031212345", True),  # 9 digits for landline
            ("032212345", True),
            ("256772123456", True),
            ("+256772123456", True),
            ("12345", False),
            ("abc123", False)
        ]
        
        for phone, expected in test_phones:
            result = pw.validate_uganda_phone(phone)
            if result == expected:
                print(f"✅ Phone {phone}: {result}")
            else:
                print(f"❌ Phone {phone}: Expected {expected}, got {result}")
                return False
        
        root.destroy()
        
    except Exception as e:
        print(f"❌ Payment window test failed: {e}")
        return False
    
    return True

def test_admin_license_generation():
    """Test admin license generation"""
    print("\n🔑 Testing Admin License Generation...")
    
    admin = AdminLicenseManager()
    
    # Generate a test license
    license_key = admin.generate_license_key("monthly", 1)
    
    if license_key.startswith("ARI-") and len(license_key) == 16:
        print(f"✅ Generated license key: {license_key}")
    else:
        print(f"❌ Invalid license key format: {license_key}")
        return False
    
    # Check if license is stored
    approved_licenses = admin.get_all_licenses()
    if license_key in approved_licenses:
        print("✅ License key stored correctly")
    else:
        print("❌ License key not stored")
        return False
    
    return True

def test_payment_info():
    """Test payment information configuration"""
    print("\n📋 Testing Payment Configuration...")
    
    required_fields = ['airtel_number', 'mtn_number', 'amount', 'currency']
    
    for field in required_fields:
        if field in PAYMENT_INFO and PAYMENT_INFO[field]:
            print(f"✅ {field}: {PAYMENT_INFO[field]}")
        else:
            print(f"❌ Missing {field}")
            return False
    
    # Check Uganda format
    if PAYMENT_INFO['currency'] == 'UGX' and PAYMENT_INFO['amount'] == '10000':
        print("✅ Uganda payment configuration correct")
    else:
        print("❌ Payment configuration incorrect")
        return False
    
    return True

def test_complete_flow():
    """Test the complete monetization flow"""
    print("\n🔄 Testing Complete Flow...")
    
    try:
        # 1. Generate device ID
        lm = LicenseManager()
        device_id = lm.get_device_id()
        print(f"Step 1 - Device ID: {device_id}")
        
        # 2. Admin generates license
        admin = AdminLicenseManager()
        license_key = admin.generate_license_key("monthly", 1)
        print(f"Step 2 - License Key: {license_key}")
        
        # 3. User activates license
        activation = lm.activate_license(license_key, "0772123456")
        if activation.get('success'):
            print("Step 3 - ✅ License activated successfully")
        else:
            print(f"Step 3 - ❌ License activation failed: {activation.get('message')}")
            return False
        
        # 4. Validate license
        validation = lm.validate_license()
        if validation.get('valid'):
            print("Step 4 - ✅ License validation passed")
        else:
            print(f"Step 4 - ❌ License validation failed: {validation.get('message')}")
            return False
        
        # 5. Check license data
        license_data = validation.get('license_data', {})
        if (license_data.get('device_id') == device_id and 
            license_data.get('status') == 'active' and
            license_data.get('license_key') == license_key):
            print("Step 5 - ✅ License data correct")
        else:
            print("Step 5 - ❌ License data incorrect")
            return False
        
        print("✅ Complete flow test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Complete flow test failed: {e}")
        return False

def cleanup_test_files():
    """Clean up test files"""
    print("\n🧹 Cleaning up test files...")
    
    test_files = [
        "license.json",
        "approved_licenses.json", 
        "pending_payments.json",
        "payments.json"
    ]
    
    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"✅ Removed {file}")
            except:
                print(f"❌ Could not remove {file}")

def main():
    """Run all tests"""
    print("🚀 Starting AriTyper Monetization System Tests\n")
    print("=" * 50)
    
    tests = [
        ("Device ID Generation", test_device_id_generation),
        ("License Validation", test_license_validation),
        ("Payment Submission", test_payment_submission),
        ("Admin License Generation", test_admin_license_generation),
        ("Payment Configuration", test_payment_info),
        ("Complete Flow", test_complete_flow)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
        print("-" * 30)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The monetization system is ready.")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    # Clean up
    cleanup_test_files()
    
    print("\n💡 Next Steps:")
    print("1. Update PAYMENT_INFO in payment_window.py with your actual phone numbers")
    print("2. Deploy the website to your hosting service")
    print("3. Test the payment flow with real transactions")
    print("4. Set up the admin panel to monitor payments")
    print("5. Configure the update server for online updates")

if __name__ == "__main__":
    main()
