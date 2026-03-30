#!/usr/bin/env python3
"""
Verify the tier reorganization is complete and correct
"""
from pathlib import Path
import sys

def check_exists(path, description):
    """Check if path exists and report"""
    if Path(path).exists():
        print(f"  ✓ {description}")
        return True
    else:
        print(f"  ✗ MISSING: {description}")
        return False

def verify_structure():
    """Verify the three-tier structure"""
    print("=" * 60)
    print("Verifying Tier Reorganization")
    print("=" * 60)
    
    all_good = True
    
    # Check tier folders exist
    print("\n1. Checking Tier Folders...")
    all_good &= check_exists("Bronze-Tier", "Bronze-Tier/")
    all_good &= check_exists("Silver-Tier", "Silver-Tier/")
    all_good &= check_exists("Gold-Tier", "Gold-Tier/")
    
    # Check root config files
    print("\n2. Checking Root Configuration...")
    all_good &= check_exists(".env", ".env")
    all_good &= check_exists(".env.example", ".env.example")
    all_good &= check_exists(".gitignore", ".gitignore")
    all_good &= check_exists("pyproject.toml", "pyproject.toml")
    all_good &= check_exists("credentials.json", "credentials.json")
    all_good &= check_exists("token.json", "token.json")
    
    # Check Bronze-Tier
    print("\n3. Checking Bronze-Tier...")
    all_good &= check_exists("Bronze-Tier/Watchers/gmail_watcher.py", "Gmail watcher")
    all_good &= check_exists("Bronze-Tier/Watchers/base_watcher.py", "Base watcher")
    all_good &= check_exists("Bronze-Tier/Skills/01_EMAIL_PROCESSOR.md", "Email processor skill")
    all_good &= check_exists("Bronze-Tier/Skills/email_processor.py", "Email processor script")
    all_good &= check_exists("Bronze-Tier/README_TIER.md", "Bronze README")
    
    # Check Silver-Tier
    print("\n4. Checking Silver-Tier...")
    all_good &= check_exists("Silver-Tier/Watchers/whatsapp_watcher.py", "WhatsApp watcher")
    all_good &= check_exists("Silver-Tier/Watchers/linkedin_poster.py", "LinkedIn poster")
    all_good &= check_exists("Silver-Tier/Watchers/base_watcher.py", "Base watcher (copied)")
    all_good &= check_exists("Silver-Tier/Skills/08_LINKEDIN_POST_GENERATOR.md", "LinkedIn skill")
    all_good &= check_exists("Silver-Tier/Skills/09_WHATSAPP_PROCESSOR.md", "WhatsApp skill")
    all_good &= check_exists("Silver-Tier/README.md", "Silver README")
    
    # Check Gold-Tier (most important)
    print("\n5. Checking Gold-Tier (Active Workspace)...")
    
    # Watchers
    print("   Watchers:")
    all_good &= check_exists("Gold-Tier/Watchers/gmail_watcher.py", "   - Gmail watcher")
    all_good &= check_exists("Gold-Tier/Watchers/whatsapp_watcher.py", "   - WhatsApp watcher")
    all_good &= check_exists("Gold-Tier/Watchers/linkedin_poster.py", "   - LinkedIn poster")
    all_good &= check_exists("Gold-Tier/Watchers/approved_watcher.py", "   - Approved watcher")
    all_good &= check_exists("Gold-Tier/Watchers/base_watcher.py", "   - Base watcher")
    all_good &= check_exists("Gold-Tier/Watchers/__init__.py", "   - __init__.py")
    
    # Skills (00-06, 08-10 - no 07)
    print("   Skills:")
    expected_skills = [0, 1, 2, 3, 4, 5, 6, 8, 9, 10]
    for i in expected_skills:
        skill_file = f"Gold-Tier/Skills/{i:02d}_*.md"
        # Check if any file matches pattern
        skill_files = list(Path("Gold-Tier/Skills").glob(f"{i:02d}_*.md"))
        if skill_files:
            print(f"     ✓ Skill {i:02d}")
        else:
            print(f"     ✗ MISSING: Skill {i:02d}")
            all_good = False
    
    all_good &= check_exists("Gold-Tier/Skills/email_processor.py", "   - Email processor script")
    
    # Actions
    print("   Actions:")
    all_good &= check_exists("Gold-Tier/actions/email_sender.py", "   - Email sender")
    
    # Schedulers
    print("   Schedulers:")
    all_good &= check_exists("Gold-Tier/schedulers/daily_runner.py", "   - Daily runner")
    
    # Folders
    print("   Workflow Folders:")
    all_good &= check_exists("Gold-Tier/Pending_Approval", "   - Pending_Approval/")
    all_good &= check_exists("Gold-Tier/Approved", "   - Approved/")
    all_good &= check_exists("Gold-Tier/Approved/Done", "   - Approved/Done/")
    all_good &= check_exists("Gold-Tier/Plans", "   - Plans/")
    all_good &= check_exists("Gold-Tier/Logs", "   - Logs/")
    
    # Shared files
    print("   Shared Files:")
    all_good &= check_exists("Gold-Tier/Dashboard.md", "   - Dashboard")
    all_good &= check_exists("Gold-Tier/Company_Handbook.md", "   - Company Handbook")
    all_good &= check_exists("Gold-Tier/run_all_watchers.py", "   - Run all watchers")
    
    # Documentation
    print("   Documentation:")
    all_good &= check_exists("Gold-Tier/README.md", "   - README")
    all_good &= check_exists("Gold-Tier/TEST_EMAIL_SENDER.md", "   - Test guide")
    all_good &= check_exists("Gold-Tier/GOLD_TIER_AUTO_EMAIL_WORKFLOW.md", "   - Workflow doc")
    
    # Check READMEs
    print("\n6. Checking Documentation...")
    all_good &= check_exists("README_TIERS.md", "Root README")
    all_good &= check_exists("REORGANIZATION_SUMMARY.md", "Reorganization summary")
    all_good &= check_exists("QUICK_START_GOLD_TIER.md", "Quick start guide")
    
    # Test imports
    print("\n7. Testing Imports...")
    try:
        sys.path.insert(0, "Gold-Tier")
        from Watchers.base_watcher import BaseWatcher
        print("  ✓ Gold-Tier imports work")
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        all_good = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_good:
        print("✅ VERIFICATION PASSED")
        print("=" * 60)
        print("\nAll components are in place!")
        print("\nNext steps:")
        print("  1. cd Gold-Tier")
        print("  2. python run_all_watchers.py")
        print("  3. See QUICK_START_GOLD_TIER.md for usage")
        return 0
    else:
        print("❌ VERIFICATION FAILED")
        print("=" * 60)
        print("\nSome components are missing.")
        print("Run: python fix_import_paths.py")
        return 1

if __name__ == "__main__":
    sys.exit(verify_structure())
