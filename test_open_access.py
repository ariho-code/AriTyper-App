#!/usr/bin/env python3
"""
Test script for AriTyper open access.

AriTyper is free: there is no activation step, no payment gate and no license
server. These tests assert the app stays unlocked — including when no license
file exists and no server is reachable.
"""
import importlib
import json
import os
import shutil
import tempfile

from license_manager import LicenseManager
from device_client import EnhancedLicenseManager

# Every app variant and its top-level class.
APP_VARIANTS = [
    ("arityper_activated",   "AriTyperActivated"),
    ("arityper_streamlined", "AriTyperStreamlined"),
    ("arityper_simple",      "AriTyperSimple"),
    ("arityper_final",       "AriTyperFinal"),
    ("arityper_working",     "AriTyperWorking"),
]

# Wording that would mean the user is still being blocked or asked to pay.
BLOCKING_TERMS = [
    "Payment Required",
    "Payment &",
    "Activate License",
    "Transaction ID",
    "UGX",
    "License Required",
    "Checking license",
    "Contact Admin",
    "Purchase",
]


def test_device_id_generation():
    """Device ID still works — it is used for display only, not for locking."""
    print("🔧 Testing Device ID Generation...")

    device_id = LicenseManager().get_device_id()
    print(f"✅ Generated Device ID: {device_id}")

    if device_id != LicenseManager().get_device_id():
        print("❌ Device ID generation is inconsistent")
        return False

    print("✅ Device ID generation is consistent")
    return True


def test_validation_without_license_file():
    """With no license.json at all, the app must still be unlocked."""
    print("\n🔓 Testing Validation With No License File...")

    tmpdir = tempfile.mkdtemp()
    try:
        missing = os.path.join(tmpdir, "does_not_exist.json")
        result = LicenseManager(license_file=missing).validate_license()

        if not result.get("valid"):
            print(f"❌ Blocked without a license file: {result.get('message')}")
            return False

        print(f"✅ Valid with no license file: {result.get('message')}")
        return True
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_validation_with_foreign_license():
    """A license issued to a different device must NOT lock this one out."""
    print("\n🔓 Testing Validation With Another Device's License...")

    tmpdir = tempfile.mkdtemp()
    try:
        path = os.path.join(tmpdir, "license.json")
        with open(path, "w") as f:
            json.dump({
                "license_key": "ARI-SOMEONEELSE",
                "device_id":   "ARI-NOTTHISDEVICE",
                "device_lock": True,
                "status":      "expired",
                "expires_at":  "2020-01-01T00:00:00",
            }, f)

        result = LicenseManager(license_file=path).validate_license()

        if not result.get("valid"):
            print(f"❌ Blocked by a foreign/expired license: {result.get('message')}")
            return False

        print("✅ Expired, device-locked license does not block anyone")
        return True
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_no_server_required():
    """Validation must not depend on (or wait for) the license server."""
    print("\n📡 Testing Offline Operation...")

    # Point at a host that cannot answer; this must still return fast and valid.
    manager = EnhancedLicenseManager(server_url="http://127.0.0.1:9")

    result = manager.validate_license_hybrid()
    if not result.get("valid"):
        print(f"❌ Blocked when the server is unreachable: {result.get('message')}")
        return False
    print("✅ Valid with an unreachable license server")

    activation = manager.activate_license_hybrid()
    if not activation.get("success"):
        print(f"❌ Activation failed offline: {activation.get('message')}")
        return False
    print("✅ Activation is a no-op and always succeeds")

    return True


def test_apps_open_unlocked():
    """Every app variant must boot straight into its main UI, paywall-free."""
    print("\n🖥️  Testing App Variants Open Unlocked...")

    try:
        import tkinter as tk
        tk.Tk().destroy()
    except Exception as e:
        print(f"⏭️  Skipped — no display available ({e})")
        return True

    ok = True
    for mod_name, cls_name in APP_VARIANTS:
        try:
            import tkinter as tk
            mod = importlib.import_module(mod_name)
            root = tk.Tk()
            try:
                getattr(mod, cls_name)(root)
                root.update()

                shown = []

                def walk(widget):
                    try:
                        text = widget.cget("text")
                        if text:
                            shown.append(str(text))
                    except Exception:
                        pass
                    for child in widget.winfo_children():
                        walk(child)

                walk(root)
                blob = " | ".join(shown)
                blocked = [t for t in BLOCKING_TERMS if t in blob]

                if blocked:
                    print(f"❌ {mod_name}: still shows {blocked}")
                    ok = False
                else:
                    print(f"✅ {mod_name}: opens unlocked")
            finally:
                root.destroy()
        except Exception as e:
            print(f"❌ {mod_name}: failed to open ({e})")
            ok = False

    return ok


def main():
    """Run all tests"""
    print("🚀 Starting AriTyper Open Access Tests\n")
    print("=" * 50)

    tests = [
        ("Device ID Generation",       test_device_id_generation),
        ("No License File",            test_validation_without_license_file),
        ("Foreign/Expired License",    test_validation_with_foreign_license),
        ("Offline Operation",          test_no_server_required),
        ("App Variants Open Unlocked", test_apps_open_unlocked),
    ]

    passed = 0
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

    print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 All tests passed! AriTyper is open and unrestricted.")
        return 0

    print("⚠️  Some tests failed. Please review the issues above.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
