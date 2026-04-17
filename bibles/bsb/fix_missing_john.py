#!/usr/bin/env python3
"""
BSB Fix Missing Gospel of John
The combination script incorrectly matched "John's Inquiry" (Matthew 11) as the book of John.
This script extracts the real Gospel of John from bsb.md and inserts it correctly.
"""

import re

BSB_SOURCE = "/Users/silas/.openclaw/workspace/bibles/bsb/bsb.md"
BSB_EDITED = "/Users/silas/.openclaw/workspace/bibles/bsb/bsb-edited.md"

def fix_missing_john():
    """Extract Gospel of John from source and insert into edited file."""
    print("BSB Fix: Adding Missing Gospel of John")
    print("=" * 50)
    
    # Read the source file to extract John
    print("\n1. Extracting Gospel of John from source...")
    with open(BSB_SOURCE, 'r', encoding='utf-8') as f:
        source = f.read()
    
    # Find the Gospel of John (starts at ## John, ends at ## Acts)
    john_match = re.search(r'(## John\n.*?)(?=\n## Acts)', source, re.DOTALL)
    if not john_match:
        print("   ERROR: Could not find Gospel of John in source")
        return False
    
    john_content = john_match.group(1)
    john_chapters = len(re.findall(r'### Chapter \d+', john_content))
    john_verses = len(re.findall(r'\*\*v\d+\*\*', john_content))
    print(f"   Found: {john_chapters} chapters, {john_verses} verses")
    
    # Read the edited file
    print("\n2. Reading edited file...")
    with open(BSB_EDITED, 'r', encoding='utf-8') as f:
        edited = f.read()
    
    # Find where to insert John (after Luke, before the spurious "John's Inquiry")
    # Look for end of Luke followed by "## John's Inquiry" or "## Acts"
    luke_end_pattern = r'(## Luke.*?\[\^\d+\]:.*?)(\n## John\'s Inquiry|\n## Acts)'
    luke_match = re.search(luke_end_pattern, edited, re.DOTALL)
    
    if not luke_match:
        print("   ERROR: Could not find insertion point after Luke")
        return False
    
    print("   Found insertion point after Luke")
    
    # Check if John already exists
    if "## John\n\n### Chapter 1" in edited and "In the beginning was the Word" in edited:
        print("   Gospel of John already present")
        return False
    
    # Insert John
    print("\n3. Inserting Gospel of John...")
    fixed = edited[:luke_match.end(1)] + '\n\n' + john_content + luke_match.group(2)
    
    # Write back
    with open(BSB_EDITED, 'w', encoding='utf-8') as f:
        f.write(fixed)
    
    print(f"\n✓ Gospel of John inserted successfully!")
    print(f"   Added: {john_chapters} chapters, {john_verses} verses")
    return True

if __name__ == "__main__":
    fix_missing_john()
