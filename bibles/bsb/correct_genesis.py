#!/usr/bin/env python3
"""
BSB Genesis Correction Script
Processes Genesis and creates a corrected version.
"""

import re

MD_PATH = "/Users/silas/.openclaw/workspace/bibles/bsb/bsb.md"
OUTPUT_PATH = "/Users/silas/.openclaw/workspace/bibles/bsb/bsb-edited-genesis.md"

# Genesis verse counts
GENESIS_COUNTS = {
    1:31, 2:25, 3:24, 4:26, 5:32, 6:22, 7:24, 8:22, 9:29, 10:32,
    11:32, 12:20, 13:18, 14:24, 15:21, 16:16, 17:27, 18:32, 19:38, 20:18,
    21:34, 22:24, 23:20, 24:67, 25:34, 26:35, 27:46, 28:22, 29:30, 30:43,
    31:55, 32:25, 33:20, 34:31, 35:29, 36:43, 37:36, 38:30, 39:23, 40:23,
    41:57, 42:38, 43:34, 44:34, 45:28, 46:34, 47:31, 48:22, 49:33, 50:26
}

def fix_curly_quotes(text):
    """Convert curly quotes to straight ASCII quotes."""
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    return text

def process_genesis():
    """Process Genesis book."""
    print("BSB Genesis Correction Script")
    print("=" * 50)
    
    # Read entire file
    print("\n1. Reading source file...")
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix curly quotes globally
    print("\n2. Converting curly quotes to straight quotes...")
    content = fix_curly_quotes(content)
    
    # Find Genesis section
    print("\n3. Extracting Genesis...")
    genesis_match = re.search(r'## Genesis\n(.*?)(?=\n## Exodus|\Z)', content, re.DOTALL)
    if not genesis_match:
        print("   ERROR: Could not find Genesis section")
        return
    
    genesis_text = genesis_match.group(0)
    lines = genesis_text.split('\n')
    
    # Process
    print("\n4. Processing chapters...")
    output_lines = ["## Genesis", ""]
    current_chapter = None
    verse_count = 0
    removed_extra = 0
    
    chapter_pattern = re.compile(r'^### Chapter (\d+)$')
    verse_pattern = re.compile(r'^\*\*v(\d+)\*\*')
    
    for line in lines[2:]:  # Skip "## Genesis" and blank line
        # Chapter header
        cm = chapter_pattern.match(line)
        if cm:
            ch_num = int(cm.group(1))
            current_chapter = ch_num
            verse_count = 0
            output_lines.append(line)
            continue
        
        # Verse line
        vm = verse_pattern.match(line)
        if vm and current_chapter:
            vnum = int(vm.group(1))
            max_verses = GENESIS_COUNTS.get(current_chapter, 999)
            
            if vnum > max_verses:
                # Skip extra verse
                removed_extra += 1
                print(f"   Removing extra: Genesis {current_chapter}:{vnum}")
                continue
            
            # Renumber if needed
            verse_count += 1
            if vnum != verse_count:
                line = re.sub(r'^\*\*v\d+\*\*', f'**v{verse_count}**', line)
            
            output_lines.append(line)
            continue
        
        # Other lines
        output_lines.append(line)
    
    # Write output
    print(f"\n5. Writing corrected Genesis...")
    print(f"   Removed {removed_extra} extra verses")
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"\n✓ Genesis correction complete!")
    print(f"   Output: {OUTPUT_PATH}")

if __name__ == "__main__":
    process_genesis()
