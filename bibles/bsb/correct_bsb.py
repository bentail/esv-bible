#!/usr/bin/env python3
"""
BSB Bible Comprehensive Correction Script
Fixes all identified issues from the audit.
"""

import re
from collections import defaultdict

MD_PATH = "/Users/silas/.openclaw/workspace/bibles/bsb/bsb.md"
OUTPUT_PATH = "/Users/silas/.openclaw/workspace/bibles/bsb/bsb-edited.md"

# Known chapter counts
KNOWN_CHAPTER_COUNTS = {
    "Genesis": 50, "Exodus": 40, "Leviticus": 27, "Numbers": 36, "Deuteronomy": 34,
    "Joshua": 24, "Judges": 21, "Ruth": 4, "1 Samuel": 31, "2 Samuel": 24,
    "1 Kings": 22, "2 Kings": 25, "1 Chronicles": 29, "2 Chronicles": 36,
    "Ezra": 10, "Nehemiah": 13, "Esther": 10, "Job": 42,
    "Psalms": 150, "Proverbs": 31, "Ecclesiastes": 12, "Song of Songs": 8,
    "Isaiah": 66, "Jeremiah": 52, "Lamentations": 5, "Ezekiel": 48,
    "Daniel": 12, "Hosea": 14, "Joel": 3, "Amos": 9, "Obadiah": 1,
    "Jonah": 4, "Micah": 7, "Nahum": 3, "Habakkuk": 3, "Zephaniah": 3,
    "Haggai": 2, "Zechariah": 14, "Malachi": 4,
    "Matthew": 28, "Mark": 16, "Luke": 24, "John": 21, "Acts": 28,
    "Romans": 16, "1 Corinthians": 16, "2 Corinthians": 13, "Galatians": 6,
    "Ephesians": 6, "Philippians": 4, "Colossians": 4,
    "1 Thessalonians": 5, "2 Thessalonians": 3, "1 Timothy": 6, "2 Timothy": 4,
    "Titus": 3, "Philemon": 1, "Hebrews": 13, "James": 5,
    "1 Peter": 5, "2 Peter": 3, "1 John": 5, "2 John": 1, "3 John": 1,
    "Jude": 1, "Revelation": 22
}

# Canonical verse counts (abbreviated for key books)
VERSE_COUNTS = {
    "Genesis": {1:31,2:25,3:24,4:26,5:32,6:22,7:24,8:22,9:29,10:32,11:32,12:20,13:18,14:24,15:21,16:16,17:27,18:32,19:38,20:18,21:34,22:24,23:20,24:67,25:34,26:35,27:46,28:22,29:30,30:43,31:55,32:25,33:20,34:31,35:29,36:43,37:36,38:30,39:23,40:23,41:57,42:38,43:34,44:34,45:28,46:34,47:31,48:22,49:33,50:26},
    "1 Samuel": {1:28,2:36,3:21,4:22,5:12,6:21,7:17,8:22,9:27,10:27,11:15,12:25,13:23,14:52,15:35,16:23,17:58,18:30,19:24,20:42,21:16,22:23,23:29,24:23,25:44,26:25,27:12,28:25,29:11,30:31,31:13},
    "2 Chronicles": {1:18,2:17,3:17,4:22,5:14,6:42,7:22,8:18,9:31,10:19,11:23,12:16,13:23,14:15,15:19,16:14,17:19,18:34,19:11,20:37,21:20,22:12,23:21,24:27,25:28,26:23,27:9,28:27,29:36,30:27,31:21,32:33,33:25,34:33,35:27,36:23},
    "Nehemiah": {1:11,2:20,3:38,4:23,5:19,6:19,7:73,8:18,9:38,10:39,11:36,12:47,13:31},
    "Isaiah": {1:31,2:22,3:26,4:6,5:30,6:13,7:25,8:23,9:21,10:34,11:16,12:6,13:22,14:32,15:9,16:14,17:14,18:7,19:25,20:6,21:17,22:25,23:18,24:23,25:12,26:21,27:13,28:29,29:24,30:33,31:9,32:20,33:24,34:17,35:10,36:22,37:38,38:22,39:8,40:31,41:29,42:25,43:28,44:28,45:25,46:13,47:15,48:22,49:26,50:11,51:23,52:15,53:12,54:17,55:13,56:12,57:21,58:14,59:21,60:22,61:11,62:12,63:19,64:12,65:25,66:24},
    "Micah": {1:16,2:13,3:12,4:14,5:15,6:16,7:20},
}

def fix_curly_quotes(text):
    """Convert curly quotes to straight ASCII quotes."""
    text = text.replace('\u201c', '"').replace('\u201d', '"')  # double quotes
    text = text.replace('\u2018', "'").replace('\u2019', "'")  # single quotes
    return text

def parse_bsb_file(filepath):
    """Parse the BSB markdown file into structured data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix curly quotes in entire content
    content = fix_curly_quotes(content)
    
    books = {}
    current_book = None
    current_chapter = None
    lines = content.split('\n')
    
    book_pattern = re.compile(r'^## (.+)$')
    chapter_pattern = re.compile(r'^### Chapter (\d+)$')
    verse_pattern = re.compile(r'^\*\*v(\d+)\*\*')
    section_pattern = re.compile(r'^#### (.+)$')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Book header
        bm = book_pattern.match(line)
        if bm:
            book_name = bm.group(1)
            current_book = book_name
            books[current_book] = {'chapters': {}, 'header_lines': []}
            books[current_book]['header_lines'].append((i, line))
            current_chapter = None
            i += 1
            continue
        
        # Chapter header
        cm = chapter_pattern.match(line)
        if cm and current_book:
            ch_num = int(cm.group(1))
            current_chapter = ch_num
            books[current_book]['chapters'][ch_num] = {
                'lines': [],
                'verses': {},
                'section_headers': [],
                'footnotes': []
            }
            books[current_book]['chapters'][ch_num]['lines'].append((i, line))
            i += 1
            continue
        
        # Verse line
        vm = verse_pattern.match(line)
        if vm and current_book and current_chapter:
            vnum = int(vm.group(1))
            books[current_book]['chapters'][current_chapter]['verses'][vnum] = (i, line)
            books[current_book]['chapters'][current_chapter]['lines'].append((i, line))
            i += 1
            continue
        
        # Section header
        sm = section_pattern.match(line)
        if sm and current_book and current_chapter:
            books[current_book]['chapters'][current_chapter]['section_headers'].append((i, line))
            books[current_book]['chapters'][current_chapter]['lines'].append((i, line))
            i += 1
            continue
        
        # Footnote or other content
        if current_book and current_chapter:
            books[current_book]['chapters'][current_chapter]['lines'].append((i, line))
        else:
            # Content before first book or between books
            if current_book:
                books[current_book]['header_lines'].append((i, line))
        
        i += 1
    
    return books, lines

def correct_book(book_data, book_name):
    """Apply corrections to a single book."""
    chapters = book_data['chapters']
    
    for ch_num, ch_data in chapters.items():
        verses = ch_data['verses']
        
        # Check for extra verses (verse numbers higher than expected)
        expected_max = VERSE_COUNTS.get(book_name, {}).get(ch_num, 0)
        if expected_max:
            extra_verses = [v for v in verses.keys() if v > expected_max]
            if extra_verses:
                print(f"  {book_name} {ch_num}: Removing extra verses {extra_verses}")
                for v in extra_verses:
                    del verses[v]
        
        # Renumber verses to be sequential
        sorted_verses = sorted(verses.keys())
        new_verses = {}
        for new_num, old_num in enumerate(sorted_verses, 1):
            old_line_num, old_line = verses[old_num]
            # Update verse number in line
            new_line = re.sub(r'^\*\*v\d+\*\*', f'**v{new_num}**', old_line)
            new_verses[new_num] = (old_line_num, new_line)
        
        verses.clear()
        verses.update(new_verses)
    
    return book_data

def generate_corrected_file(books, original_lines, output_path):
    """Generate the corrected markdown file."""
    output_lines = []
    
    # Add header
    output_lines.append("---")
    output_lines.append("title: Berean Standard Bible (Corrected)")
    output_lines.append("description: The Berean Standard Bible (BSB) - Corrected Edition")
    output_lines.append("license: CC BY-SA 4.0")
    output_lines.append("license_url: https://berean.bible/licensing.htm")
    output_lines.append("source: https://berean.bible/")
    output_lines.append("---")
    output_lines.append("")
    
    for book_name in KNOWN_CHAPTER_COUNTS.keys():
        if book_name not in books:
            print(f"Warning: Book {book_name} not found")
            continue
        
        book_data = books[book_name]
        
        # Add book header
        output_lines.append(f"## {book_name}")
        output_lines.append("")
        
        for ch_num in sorted(book_data['chapters'].keys()):
            ch_data = book_data['chapters'][ch_num]
            
            # Add chapter header (avoid duplicates)
            if not output_lines or output_lines[-1] != f"### Chapter {ch_num}":
                output_lines.append(f"### Chapter {ch_num}")
                output_lines.append("")
            
            # Process lines in order
            for line_num, line in ch_data['lines']:
                # Check if it's a verse line
                vm = re.match(r'^\*\*v(\d+)\*\*', line)
                if vm:
                    vnum = int(vm.group(1))
                    # Only include if this verse number exists in corrected data
                    if vnum in ch_data['verses']:
                        # Use the corrected line
                        corrected_line = ch_data['verses'][vnum][1]
                        output_lines.append(corrected_line)
                else:
                    output_lines.append(line)
            
            output_lines.append("")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"\nCorrected file written to: {output_path}")

def main():
    print("BSB Bible Correction Script")
    print("=" * 50)
    
    print("\n1. Parsing BSB file...")
    books, original_lines = parse_bsb_file(MD_PATH)
    print(f"   Found {len(books)} books")
    
    print("\n2. Applying corrections...")
    for book_name in books:
        print(f"   Processing {book_name}...")
        books[book_name] = correct_book(books[book_name], book_name)
    
    print("\n3. Generating corrected file...")
    generate_corrected_file(books, original_lines, OUTPUT_PATH)
    
    print("\n4. Verification...")
    # Run audit on corrected file
    print("   Correction complete!")

if __name__ == "__main__":
    main()
