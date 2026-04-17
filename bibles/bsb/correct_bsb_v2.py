#!/usr/bin/env python3
"""
BSB Bible Correction Script - Clean Rewrite
Processes the entire BSB file and creates a corrected version.
"""

import re
import sys

MD_PATH = "/Users/silas/.openclaw/workspace/bibles/bsb/bsb.md"
OUTPUT_PATH = "/Users/silas/.openclaw/workspace/bibles/bsb/bsb-edited.md"

# Books to process in order
BOOKS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
    "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra",
    "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
    "Ecclesiastes", "Song of Songs", "Isaiah", "Jeremiah", "Lamentations",
    "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk",
    "Zephaniah", "Haggai", "Zechariah", "Malachi",
    "Matthew", "Mark", "Luke", "John", "Acts",
    "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians", "1 Timothy",
    "2 Timothy", "Titus", "Philemon", "Hebrews", "James",
    "1 Peter", "2 Peter", "1 John", "2 John", "3 John",
    "Jude", "Revelation"
]

# Known verse counts for books with issues
VERSE_COUNTS = {
    "Genesis": {1:31,2:25,3:24,4:26,5:32,6:22,7:24,8:22,9:29,10:32,11:32,12:20,13:18,14:24,15:21,16:16,17:27,18:32,19:38,20:18,21:34,22:24,23:20,24:67,25:34,26:35,27:46,28:22,29:30,30:43,31:55,32:25,33:20,34:31,35:29,36:43,37:36,38:30,39:23,40:23,41:57,42:38,43:34,44:34,45:28,46:34,47:31,48:22,49:33,50:26},
    "Exodus": {1:22,2:25,3:22,4:31,5:23,6:30,7:25,8:32,9:35,10:29,11:10,12:51,13:22,14:31,15:27,16:36,17:16,18:27,19:25,20:26,21:36,22:31,23:33,24:18,25:40,26:37,27:21,28:43,29:46,30:38,31:18,32:35,33:23,34:35,35:35,36:38,37:29,38:31,39:43,40:38},
    "1 Samuel": {1:28,2:36,3:21,4:22,5:12,6:21,7:17,8:22,9:27,10:27,11:15,12:25,13:23,14:52,15:35,16:23,17:58,18:30,19:24,20:42,21:16,22:23,23:29,24:23,25:44,26:25,27:12,28:25,29:11,30:31,31:13},
    "2 Chronicles": {1:18,2:17,3:17,4:22,5:14,6:42,7:22,8:18,9:31,10:19,11:23,12:16,13:23,14:15,15:19,16:14,17:19,18:34,19:11,20:37,21:20,22:12,23:21,24:27,25:28,26:23,27:9,28:27,29:36,30:27,31:21,32:33,33:25,34:33,35:27,36:23},
    "Nehemiah": {1:11,2:20,3:38,4:23,5:19,6:19,7:73,8:18,9:38,10:39,11:36,12:47,13:31},
    "Isaiah": {1:31,2:22,3:26,4:6,5:30,6:13,7:25,8:23,9:21,10:34,11:16,12:6,13:22,14:32,15:9,16:14,17:14,18:7,19:25,20:6,21:17,22:25,23:18,24:23,25:12,26:21,27:13,28:29,29:24,30:33,31:9,32:20,33:24,34:17,35:10,36:22,37:38,38:22,39:8,40:31,41:29,42:25,43:28,44:28,45:25,46:13,47:15,48:22,49:26,50:11,51:23,52:15,53:12,54:17,55:13,56:12,57:21,58:14,59:21,60:22,61:11,62:12,63:19,64:12,65:25,66:24},
    "Micah": {1:16,2:13,3:12,4:14,5:15,6:16,7:20},
}

def fix_curly_quotes(text):
    """Convert curly quotes to straight ASCII quotes."""
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    return text

def process_bsb():
    """Process the entire BSB file and create corrected version."""
    print("BSB Bible Correction Script v2")
    print("=" * 50)
    
    # Read entire file
    print("\n1. Reading source file...")
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"   File size: {len(content):,} characters")
    
    # Fix curly quotes globally
    print("\n2. Converting curly quotes to straight quotes...")
    content = fix_curly_quotes(content)
    
    # Split into lines
    lines = content.split('\n')
    print(f"   Total lines: {len(lines):,}")
    
    # Process book by book
    print("\n3. Processing books...")
    output_lines = []
    current_book = None
    current_chapter = None
    verse_count = 0
    
    book_pattern = re.compile(r'^## (.+)$')
    chapter_pattern = re.compile(r'^### Chapter (\d+)$')
    verse_pattern = re.compile(r'^\*\*v(\d+)\*\*')
    
    for line_num, line in enumerate(lines, 1):
        # Book header
        bm = book_pattern.match(line)
        if bm:
            book_name = bm.group(1)
            if book_name in BOOKS:
                current_book = book_name
                current_chapter = None
                verse_count = 0
                output_lines.append(line)
            continue
        
        # Chapter header
        cm = chapter_pattern.match(line)
        if cm and current_book:
            ch_num = int(cm.group(1))
            current_chapter = ch_num
            verse_count = 0
            output_lines.append(line)
            continue
        
        # Verse line
        vm = verse_pattern.match(line)
        if vm and current_book and current_chapter:
            vnum = int(vm.group(1))
            
            # Check if this verse should exist
            max_verses = VERSE_COUNTS.get(current_book, {}).get(current_chapter, 999)
            
            if vnum > max_verses:
                # Skip this extra verse
                print(f"   Removing extra: {current_book} {current_chapter}:{vnum}")
                continue
            
            # Renumber verses sequentially if needed
            verse_count += 1
            if vnum != verse_count:
                line = re.sub(r'^\*\*v\d+\*\*', f'**v{verse_count}**', line)
            
            output_lines.append(line)
            continue
        
        # Other lines (section headers, footnotes, blank lines)
        output_lines.append(line)
    
    # Write output
    print(f"\n4. Writing corrected file...")
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    # Get stats
    final_size = len('\n'.join(output_lines))
    print(f"   Output size: {final_size:,} characters")
    print(f"   Size change: {final_size - len(content):,} characters")
    
    print(f"\n5. Corrected file saved to:")
    print(f"   {OUTPUT_PATH}")
    print("\n✓ Correction complete!")

if __name__ == "__main__":
    process_bsb()
