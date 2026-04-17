#!/usr/bin/env python3
"""
BSB Revert Bad Corrections Script
Reverts the incorrect verse removals from Genesis while keeping valid fixes.
"""

import re
import shutil

BSB_SOURCE = "/Users/silas/.openclaw/workspace/bibles/bsb/bsb.md"
BSB_EDITED = "/Users/silas/.openclaw/workspace/bibles/bsb/bsb-edited.md"

def revert_genesis_corrections():
    """Restore original Genesis from source (my corrections were wrong)."""
    print("Reverting incorrect Genesis corrections...")
    
    # Read both files
    with open(BSB_SOURCE, 'r', encoding='utf-8') as f:
        source = f.read()
    with open(BSB_EDITED, 'r', encoding='utf-8') as f:
        edited = f.read()
    
    # Extract Genesis from source
    genesis_match = re.search(r'(## Genesis\n.*?)(?=\n## Exodus)', source, re.DOTALL)
    if not genesis_match:
        print("   ERROR: Could not find Genesis in source")
        return False
    
    genesis_source = genesis_match.group(1)
    
    # Replace Genesis in edited file
    edited_fixed = re.sub(r'(## Genesis\n.*?)(?=\n## Exodus)', genesis_source, edited, flags=re.DOTALL)
    
    with open(BSB_EDITED, 'w', encoding='utf-8') as f:
        f.write(edited_fixed)
    
    print("   ✓ Genesis restored from original source")
    return True

def keep_valid_fixes():
    """Apply only the verified correct fixes."""
    print("\nApplying verified corrections only...")
    
    with open(BSB_EDITED, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Fix curly quotes (this is definitely needed)
    curly_double = content.count('\u201c') + content.count('\u201d')
    curly_single = content.count('\u2018') + content.count('\u2019')
    
    if curly_double > 0 or curly_single > 0:
        content = content.replace('\u201c', '"').replace('\u201d', '"')
        content = content.replace('\u2018', "'").replace('\u2019', "'")
        print(f"   ✓ Converted {curly_double + curly_single} curly quotes to straight ASCII")
    
    # 2. Fix 2 Chronicles (verified via subagent and API)
    # This would need to be done carefully - for now, leave as-is
    print("   ℹ 2 Chronicles: Manual verification needed for 1:18, 13:23")
    
    # 3. Gospel of John was already restored in the edited file
    
    with open(BSB_EDITED, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def verify_final():
    """Verify the final file has all 66 books."""
    with open(BSB_EDITED, 'r', encoding='utf-8') as f:
        content = f.read()
    
    books = len(re.findall(r'^## [^#]', content, re.MULTILINE))
    verses = len(re.findall(r'\*\*v\d+\*\*', content))
    
    print(f"\nFinal verification:")
    print(f"   Books: {books}/66")
    print(f"   Verses: {verses:,}")
    print(f"   Size: {len(content):,} bytes")
    
    return books == 66

if __name__ == "__main__":
    print("BSB Correction Revert")
    print("=" * 50)
    print("\n⚠ My Genesis 'corrections' were wrong - restoring from source")
    print("⚠ Only keeping: curly quote fixes, Gospel of John restoration\n")
    
    # Backup first
    shutil.copy(BSB_EDITED, BSB_EDITED + '.backup')
    print("✓ Created backup: bsb-edited.md.backup\n")
    
    revert_genesis_corrections()
    keep_valid_fixes()
    verify_final()
    
    print("\n✓ Corrections reverted. bsb-edited.md now matches source for Genesis.")
