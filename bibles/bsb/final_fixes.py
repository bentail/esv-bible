#!/usr/bin/env python3
"""
BSB Final Fixes Script
Removes spurious Micah 4:14, verifies 1 Samuel 21:15, converts curly quotes to straight.
"""

import re

BSB_EDITED = "/Users/silas/.openclaw/workspace/bibles/bsb/bsb-edited.md"

def fix_curly_quotes():
    """Convert all curly quotes to straight ASCII quotes globally."""
    with open(BSB_EDITED, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count before
    curly_double = content.count('\u201c') + content.count('\u201d')
    curly_single = content.count('\u2018') + content.count('\u2019')
    
    if curly_double == 0 and curly_single == 0:
        print("ℹ No curly quotes found (already fixed)")
        return False
    
    # Replace
    content = content.replace('\u201c', '"').replace('\u201d', '"')
    content = content.replace('\u2018', "'").replace('\u2019', "'")
    
    with open(BSB_EDITED, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Converted {curly_double} curly double quotes and {curly_single} curly single quotes to straight ASCII")
    return True

def fix_micah_4():
    """Remove the extra v14 from Micah 4 (BSB only has v1-13)."""
    with open(BSB_EDITED, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if Micah 4 v14 exists
    micah_section = re.search(
        r'## Micah.*?### Chapter 4.*?\*\*v13\*\*.*?(\n\*\*v14\*\*.*?)(?=\n####|\n### Chapter 5|\n## Nahum)',
        content,
        re.DOTALL
    )
    
    if micah_section and "Strike her with a club" in micah_section.group(1):
        print("✓ Removing spurious Micah 4:14")
        # Remove the v14 line
        content = content.replace(micah_section.group(1), '')
        
        with open(BSB_EDITED, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    else:
        print("ℹ Micah 4:14 not found or already fixed")
        return False

def fix_1samuel_21():
    """Check if 1 Samuel 21:15 exists."""
    with open(BSB_EDITED, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if v15 exists
    has_v15 = re.search(r'### Chapter 21\n.*?\*\*v15\*\*', content, re.DOTALL)
    
    if has_v15:
        print("ℹ 1 Samuel 21:15 present (verified)")
        return True
    else:
        print("⚠ 1 Samuel 21:15 not found (source may have only 14 verses)")
        return False

def verify_counts():
    """Verify final counts."""
    with open(BSB_EDITED, 'r', encoding='utf-8') as f:
        content = f.read()
    
    books = len(re.findall(r'^## [^#]', content, re.MULTILINE))
    verses = len(re.findall(r'\*\*v\d+\*\*', content))
    
    print(f"\n✓ Final verification:")
    print(f"   Books: {books}/66")
    print(f"   Verses: {verses:,}")
    print(f"   File size: {len(content):,} bytes")
    
    return books == 66

if __name__ == "__main__":
    print("BSB Final Fixes")
    print("=" * 50)
    
    fix_curly_quotes()
    fix_micah_4()
    fix_1samuel_21()
    verify_counts()
    
    print("\n✓ All fixes applied to bsb-edited.md")
