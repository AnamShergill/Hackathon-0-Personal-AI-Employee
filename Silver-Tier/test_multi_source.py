"""
Test script for Silver Tier Multi-Source System
Tests the orchestrator and processors with sample messages
"""

import subprocess
import sys
from pathlib import Path

def run_skill(skill_name):
    """Run a skill and return success status"""
    print(f"\n{'='*80}")
    print(f"Running: {skill_name}")
    print('='*80)
    
    try:
        # Run the skill
        result = subprocess.run(
            [sys.executable, '-c', f"""
import sys
sys.path.insert(0, '.')

# Read and execute the skill
with open('Skills/{skill_name}.md', 'r', encoding='utf-8') as f:
    content = f.read()
    
# Extract Python code from markdown
import re
code_blocks = re.findall(r'```python\\n(.*?)\\n```', content, re.DOTALL)
if code_blocks:
    exec(code_blocks[0])
else:
    print('No Python code found in skill')
"""],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running {skill_name}: {e}")
        return False


def test_multi_source_system():
    """Test the complete multi-source system"""
    
    print("="*80)
    print("SILVER TIER MULTI-SOURCE SYSTEM TEST")
    print("="*80)
    print()
    
    # Check if we have files to process
    needs_action = Path("Needs_Action")
    files = list(needs_action.glob("*.md"))
    
    if not files:
        print("⚠️  No files in Needs_Action/ to test with")
        print("   Please ensure you have:")
        print("   - At least one email file (from Gmail watcher)")
        print("   - At least one WhatsApp file (from WhatsApp watcher)")
        print()
        return False
    
    print(f"📋 Found {len(files)} files in Needs_Action/:")
    for f in files:
        print(f"   - {f.name}")
    print()
    
    # Count by source
    gmail_count = len([f for f in files if f.name.startswith('email_')])
    whatsapp_count = len([f for f in files if f.name.startswith('whatsapp_')])
    other_count = len(files) - gmail_count - whatsapp_count
    
    print(f"📊 Breakdown:")
    print(f"   Gmail: {gmail_count}")
    print(f"   WhatsApp: {whatsapp_count}")
    print(f"   Other: {other_count}")
    print()
    
    # Step 1: Run Main Orchestrator
    print("\n" + "="*80)
    print("STEP 1: Main Orchestrator (Routing)")
    print("="*80)
    success = run_skill("00_MAIN_ORCHESTRATOR")
    if not success:
        print("❌ Orchestrator failed")
        return False
    print("✅ Orchestrator completed")
    
    # Step 2: Run Email Processor if we have Gmail messages
    if gmail_count > 0:
        print("\n" + "="*80)
        print("STEP 2: Email Processor")
        print("="*80)
        success = run_skill("01_EMAIL_PROCESSOR")
        if not success:
            print("⚠️  Email processor had issues")
        else:
            print("✅ Email processor completed")
    
    # Step 3: Run WhatsApp Processor if we have WhatsApp messages
    if whatsapp_count > 0:
        print("\n" + "="*80)
        print("STEP 3: WhatsApp Processor")
        print("="*80)
        success = run_skill("09_WHATSAPP_PROCESSOR")
        if not success:
            print("⚠️  WhatsApp processor had issues")
        else:
            print("✅ WhatsApp processor completed")
    
    # Check results
    print("\n" + "="*80)
    print("TEST RESULTS")
    print("="*80)
    
    # Check Needs_Action is empty
    remaining = list(needs_action.glob("*.md"))
    print(f"\n📋 Needs_Action/ status: {len(remaining)} files remaining")
    
    # Check Plans created
    plans = list(Path("Plans").glob("*.md"))
    print(f"📝 Plans/ status: {len(plans)} plans/drafts created")
    
    # Check Done folder
    done = list(Path("Done").glob("*.md"))
    print(f"✅ Done/ status: {len(done)} files completed")
    
    print()
    if len(remaining) == 0:
        print("🎉 SUCCESS! All files processed and moved to Done/")
        return True
    else:
        print("⚠️  Some files remain in Needs_Action/ - check logs")
        for f in remaining:
            print(f"   - {f.name}")
        return False


if __name__ == "__main__":
    print("\n")
    success = test_multi_source_system()
    print("\n")
    
    if success:
        print("✅ Multi-source system test PASSED")
        sys.exit(0)
    else:
        print("⚠️  Multi-source system test completed with warnings")
        sys.exit(1)
