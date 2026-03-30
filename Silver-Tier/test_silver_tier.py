"""
Silver Tier - Comprehensive Test Suite
Tests all Silver Tier components to verify complete functionality.
"""

import sys
import subprocess
from pathlib import Path
import time

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_result(test_name, passed, message=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if message:
        print(f"     {message}")


def test_dependencies():
    """Test that all required dependencies are installed"""
    print_header("TEST 1: Dependencies")
    
    tests = [
        ("schedule", "import schedule"),
        ("playwright", "from playwright.sync_api import sync_playwright"),
        ("yaml", "import yaml"),
        ("google-api", "from google.auth.transport.requests import Request"),
    ]
    
    all_passed = True
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print_result(f"{name} installed", True)
        except ImportError as e:
            print_result(f"{name} installed", False, str(e))
            all_passed = False
    
    return all_passed


def test_folder_structure():
    """Test that all required folders exist"""
    print_header("TEST 2: Folder Structure")
    
    folders = [
        "Needs_Action",
        "Pending_Approval",
        "Approved",
        "Done",
        "Plans",
        "Briefings",
        "Logs",
        "Skills",
        "Watchers",
        "schedulers"
    ]
    
    all_passed = True
    for folder in folders:
        path = Path(folder)
        exists = path.exists() and path.is_dir()
        print_result(f"Folder: {folder}", exists)
        if not exists:
            all_passed = False
    
    return all_passed


def test_files_exist():
    """Test that all Silver Tier files exist"""
    print_header("TEST 3: Silver Tier Files")
    
    files = [
        "Skills/00_MAIN_ORCHESTRATOR.md",
        "Skills/08_LINKEDIN_POST_GENERATOR.md",
        "Skills/09_WHATSAPP_PROCESSOR.md",
        "Watchers/gmail_watcher.py",
        "Watchers/whatsapp_watcher.py",
        "Watchers/linkedin_poster.py",
        "Watchers/approved_watcher.py",
        "Watchers/base_watcher.py",
        "schedulers/daily_runner.py",
        "run_all_watchers.py",
    ]
    
    all_passed = True
    for file in files:
        path = Path(file)
        exists = path.exists() and path.is_file()
        print_result(f"File: {file}", exists)
        if not exists:
            all_passed = False
    
    return all_passed


def test_linkedin_post_generator():
    """Test LinkedIn post generator"""
    print_header("TEST 4: LinkedIn Post Generator")
    
    try:
        # Run the generator
        result = subprocess.run(
            [sys.executable, '-c', """
import sys
sys.path.insert(0, '.')
with open('Skills/08_LINKEDIN_POST_GENERATOR.md', 'r', encoding='utf-8') as f:
    content = f.read()
import re
code_blocks = re.findall(r'```python\\n(.*?)\\n```', content, re.DOTALL)
if code_blocks:
    exec(code_blocks[0])
"""],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Check if post was created
        pending_files = list(Path("Pending_Approval").glob("linkedin_post_*.md"))
        
        if pending_files:
            print_result("LinkedIn post generated", True, f"Created: {pending_files[-1].name}")
            
            # Read and verify content
            with open(pending_files[-1], 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_frontmatter = content.startswith('---')
            has_post_text = '## Post Text' in content
            has_hashtags = '#' in content
            
            print_result("Post has frontmatter", has_frontmatter)
            print_result("Post has text section", has_post_text)
            print_result("Post has hashtags", has_hashtags)
            
            return has_frontmatter and has_post_text and has_hashtags
        else:
            print_result("LinkedIn post generated", False, "No file created")
            return False
            
    except Exception as e:
        print_result("LinkedIn post generator", False, str(e))
        return False


def test_linkedin_session():
    """Test if LinkedIn session exists"""
    print_header("TEST 5: LinkedIn Session")
    
    session_dir = Path("Watchers/linkedin_session")
    
    if session_dir.exists():
        files = list(session_dir.glob("*"))
        print_result("LinkedIn session exists", True, f"{len(files)} files")
        return True
    else:
        print_result("LinkedIn session exists", False, "Run: python Watchers/linkedin_poster.py")
        return False


def test_gitignore():
    """Test that sensitive folders are in .gitignore"""
    print_header("TEST 6: .gitignore Configuration")
    
    try:
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
        
        checks = [
            ("linkedin_session/", "linkedin_session/" in gitignore_content),
            ("whatsapp_session/", "whatsapp_session/" in gitignore_content),
            ("token.json", "token.json" in gitignore_content),
            ("credentials.json", "credentials.json" in gitignore_content),
        ]
        
        all_passed = True
        for name, check in checks:
            print_result(f"Ignoring: {name}", check)
            if not check:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_result(".gitignore check", False, str(e))
        return False


def test_scheduler_functions():
    """Test scheduler functions"""
    print_header("TEST 7: Scheduler Functions")
    
    try:
        sys.path.insert(0, '.')
        from schedulers.daily_runner import generate_weekly_briefing
        
        # Test briefing generation
        result = generate_weekly_briefing()
        
        # Check if briefing was created
        briefing_files = list(Path("Briefings").glob("briefing_*.md"))
        
        if briefing_files:
            print_result("Weekly briefing generated", True, f"Created: {briefing_files[-1].name}")
            return True
        else:
            print_result("Weekly briefing generated", False, "No file created")
            return False
            
    except Exception as e:
        print_result("Scheduler functions", False, str(e))
        return False


def test_approved_watcher_logic():
    """Test approved watcher file detection logic"""
    print_header("TEST 8: Approved Watcher Logic")
    
    try:
        sys.path.insert(0, '.')
        from Watchers.approved_watcher import ApprovedWatcher
        
        # Create watcher instance
        watcher = ApprovedWatcher(interval=30)
        
        print_result("Approved watcher instantiated", True)
        
        # Test file type detection
        test_cases = [
            ("linkedin_post_test.md", "linkedin_post"),
            ("REPLY_email_test.md", "email_reply"),
            ("REPLY_whatsapp_test.md", "whatsapp_reply"),
        ]
        
        all_passed = True
        for filename, expected_type in test_cases:
            # Create test file
            test_path = Path("Approved") / filename
            test_path.write_text(f'---\ntype: "{expected_type}"\n---\nTest content')
            
            detected_type = watcher._determine_file_type(test_path)
            passed = detected_type == expected_type
            
            print_result(f"Detect {expected_type}", passed, f"Got: {detected_type}")
            
            # Cleanup
            test_path.unlink()
            
            if not passed:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_result("Approved watcher logic", False, str(e))
        return False


def print_summary(results):
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print()
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Silver Tier is ready!")
        print()
        print("Next steps:")
        print("1. Setup LinkedIn: python Watchers/linkedin_poster.py")
        print("2. Start watchers: python run_all_watchers.py")
        print("3. Check START_HERE.md for full guide")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print()
        print("Failed tests:")
        for test_name, passed in results.items():
            if not passed:
                print(f"  - {test_name}")
    
    print()
    return failed == 0


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  SILVER TIER - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print("\nThis will test all Silver Tier components...")
    print()
    
    results = {}
    
    # Run all tests
    results["Dependencies"] = test_dependencies()
    results["Folder Structure"] = test_folder_structure()
    results["Files Exist"] = test_files_exist()
    results["LinkedIn Post Generator"] = test_linkedin_post_generator()
    results["LinkedIn Session"] = test_linkedin_session()
    results[".gitignore"] = test_gitignore()
    results["Scheduler Functions"] = test_scheduler_functions()
    results["Approved Watcher Logic"] = test_approved_watcher_logic()
    
    # Print summary
    all_passed = print_summary(results)
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
