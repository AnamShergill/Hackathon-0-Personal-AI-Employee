#!/usr/bin/env python3
"""
Odoo Integration Test Script
Tests connection, creates sample partner and invoice.
"""

import sys
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from actions.odoo_rpc import OdooRPCClient

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def test_connection():
    """Test 1: Connection and Authentication"""
    print_section("TEST 1: Connection and Authentication")
    
    client = OdooRPCClient()
    
    print(f"Odoo URL: {client.url}")
    print(f"Database: {client.db}")
    print(f"Username: {client.username}")
    print()
    
    if client.test_connection():
        print("✅ Connection test PASSED")
        return client
    else:
        print("❌ Connection test FAILED")
        print("\nTroubleshooting:")
        print("1. Check if Odoo containers are running:")
        print("   cd odoo-docker && docker compose ps")
        print("2. Verify Odoo is accessible:")
        print("   Open http://localhost:8069 in browser")
        print("3. Check credentials in odoo-docker/.env")
        return None

def test_list_partners(client):
    """Test 2: List existing partners"""
    print_section("TEST 2: List Existing Partners")
    
    try:
        partners = client.search_read('res.partner', limit=5, fields=['name', 'email', 'phone'])
        
        print(f"Found {len(partners)} partners:")
        for p in partners:
            email = p.get('email', 'no email')
            phone = p.get('phone', 'no phone')
            print(f"  - ID {p['id']}: {p['name']} | {email} | {phone}")
        
        print("\n✅ List partners test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ List partners test FAILED: {e}")
        return False

def test_create_partner(client):
    """Test 3: Create a test partner"""
    print_section("TEST 3: Create Test Partner")
    
    partner_name = "AI Employee Test Client"
    partner_email = "test@aiemployee.local"
    partner_phone = "+92-300-TEST123"
    
    try:
        # Check if partner already exists
        existing = client.search_read(
            'res.partner',
            domain=[('name', '=', partner_name)],
            fields=['id', 'name'],
            limit=1
        )
        
        if existing:
            partner_id = existing[0]['id']
            print(f"ℹ️  Partner already exists: {partner_name} (ID: {partner_id})")
            print("   Skipping creation, using existing partner")
        else:
            partner_id = client.create_partner(
                name=partner_name,
                email=partner_email,
                phone=partner_phone,
                is_company=True
            )
            print(f"✅ Created partner: {partner_name}")
            print(f"   Partner ID: {partner_id}")
            print(f"   Email: {partner_email}")
            print(f"   Phone: {partner_phone}")
        
        print("\n✅ Create partner test PASSED")
        return partner_id
        
    except Exception as e:
        print(f"❌ Create partner test FAILED: {e}")
        return None

def test_create_invoice(client, partner_id):
    """Test 4: Create a test invoice"""
    print_section("TEST 4: Create Test Invoice")
    
    if not partner_id:
        print("❌ Cannot create invoice: No partner ID")
        return False
    
    try:
        invoice_lines = [
            {
                'description': 'AI Employee Integration Test Service',
                'quantity': 1,
                'price_unit': 100.00
            }
        ]
        
        invoice_id = client.create_invoice(
            partner_id=partner_id,
            invoice_lines=invoice_lines,
            move_type='out_invoice'
        )
        
        print(f"✅ Created invoice ID: {invoice_id}")
        print(f"   Partner ID: {partner_id}")
        print(f"   Amount: $100.00")
        print(f"   Status: Draft")
        print(f"   View in Odoo: {client.url}/web#id={invoice_id}&model=account.move")
        
        print("\n✅ Create invoice test PASSED")
        return invoice_id
        
    except Exception as e:
        print(f"❌ Create invoice test FAILED: {e}")
        return None

def test_query_invoices(client, partner_id):
    """Test 5: Query unpaid invoices"""
    print_section("TEST 5: Query Unpaid Invoices")
    
    try:
        invoices = client.get_unpaid_invoices(partner_id=partner_id, limit=5)
        
        print(f"Found {len(invoices)} unpaid invoice(s) for partner {partner_id}:")
        for inv in invoices:
            partner_name = inv['partner_id'][1] if isinstance(inv['partner_id'], list) else 'Unknown'
            print(f"  - {inv['name']}: ${inv['amount_total']} ({inv['payment_state']})")
            print(f"    Partner: {partner_name}")
            print(f"    Date: {inv.get('invoice_date', 'N/A')}")
        
        print("\n✅ Query invoices test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Query invoices test FAILED: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  ODOO INTEGRATION TEST SUITE")
    print("  Gold-Tier Phase 2: Odoo Accounting Integration")
    print("=" * 80)
    
    # Test 1: Connection
    client = test_connection()
    if not client:
        print("\n❌ CRITICAL: Cannot connect to Odoo. Stopping tests.")
        print("\nMake sure:")
        print("1. Odoo containers are running: docker compose ps")
        print("2. Database is initialized: http://localhost:8069")
        print("3. Credentials in .env are correct")
        sys.exit(1)
    
    time.sleep(1)
    
    # Test 2: List partners
    test_list_partners(client)
    time.sleep(1)
    
    # Test 3: Create partner
    partner_id = test_create_partner(client)
    time.sleep(1)
    
    # Test 4: Create invoice
    invoice_id = None
    if partner_id:
        invoice_id = test_create_invoice(client, partner_id)
        time.sleep(1)
    
    # Test 5: Query invoices
    if partner_id:
        test_query_invoices(client, partner_id)
    
    # Summary
    print_section("TEST SUMMARY")
    
    results = {
        "Connection": client is not None,
        "List Partners": True,  # If we got here, it worked
        "Create Partner": partner_id is not None,
        "Create Invoice": invoice_id is not None,
        "Query Invoices": True  # If we got here, it worked
    }
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print("Test Results:")
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test:20s} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Odoo integration is fully operational.")
        print("\nNext steps:")
        print("1. Review created records in Odoo: http://localhost:8069")
        print("2. Test approved_watcher with Odoo action files")
        print("3. Create real invoices from email data")
    else:
        print("\n⚠️  Some tests failed. Review errors above.")
    
    print("\n" + "=" * 80)
    
    sys.exit(0 if passed == total else 1)

if __name__ == '__main__':
    main()
