#!/usr/bin/env python3
"""
BSB Bible Audit Script - Comprehensive Error Check
Analyzes the BSB markdown file for structural issues, missing verses, duplicates, etc.
"""

import re
from collections import defaultdict

MD_PATH = "/Users/silas/.openclaw/workspace/bibles/bsb/bsb.md"

# Known chapter counts for all 66 books
KNOWN_CHAPTER_COUNTS = {
    "Genesis": 50, "Exodus": 40, "Leviticus": 27, "Numbers": 36, "Deuteronomy": 34,
    "Joshua": 24, "Judges": 21, "Ruth": 4, "1 Samuel": 31, "2 Samuel": 24,
    "1 Kings": 22, "2 Kings": 25, "1 Chronicles": 29, "2 Chronicles": 36,
    "Ezra": 10, "Nehemiah": 13, "Esther": 10, "Job": 42,
    "Psalms": 150, "Proverbs": 31, "Ecclesiastes": 12, "Song of Solomon": 8,
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

# Known verse counts per chapter (canonical)
VERSE_COUNTS = {
    "Genesis": {1:31,2:25,3:24,4:26,5:32,6:22,7:24,8:22,9:29,10:32,11:32,12:20,13:18,14:24,15:21,16:16,17:27,18:32,19:38,20:18,21:34,22:24,23:20,24:67,25:34,26:35,27:46,28:22,29:30,30:43,31:55,32:25,33:20,34:31,35:29,36:43,37:46,38:30,39:23,40:23,41:57,42:38,43:34,44:34,45:28,46:34,47:31,48:22,49:33,50:26},
    "Exodus": {1:22,2:25,3:22,4:31,5:23,6:30,7:25,8:32,9:35,10:29,11:10,12:51,13:22,14:31,15:27,16:36,17:16,18:27,19:25,20:26,21:36,22:31,23:33,24:18,25:40,26:37,27:21,28:43,29:46,30:38,31:18,32:35,33:23,34:35,35:35,36:38,37:29,38:31,39:43,40:38},
    "Leviticus": {1:17,2:16,3:17,4:35,5:19,6:30,7:38,8:36,9:24,10:20,11:47,12:8,13:59,14:57,15:33,16:34,17:16,18:30,19:37,20:27,21:24,22:33,23:44,24:23,25:55,26:46,27:34},
    "Numbers": {1:54,2:34,3:51,4:49,5:31,6:27,7:89,8:26,9:23,10:36,11:35,12:16,13:33,14:45,15:41,16:50,17:13,18:32,19:22,20:29,21:35,22:41,23:30,24:25,25:18,26:65,27:23,28:31,29:40,30:16,31:54,32:42,33:56,34:29,35:34,36:13},
    "Deuteronomy": {1:46,2:37,3:29,4:49,5:33,6:25,7:26,8:20,9:29,10:22,11:32,12:32,13:18,14:29,15:23,16:22,17:20,18:22,19:21,20:20,21:23,22:30,23:25,24:22,25:19,26:19,27:26,28:68,29:29,30:20,31:30,32:52,33:29,34:12},
    "Joshua": {1:18,2:24,3:17,4:24,5:15,6:27,7:26,8:35,9:27,10:43,11:23,12:24,13:33,14:15,15:63,16:10,17:18,18:28,19:51,20:9,21:45,22:34,23:16,24:33},
    "Judges": {1:36,2:23,3:31,4:24,5:31,6:40,7:25,8:35,9:57,10:18,11:40,12:15,13:25,14:20,15:20,16:31,17:13,18:31,19:30,20:48,21:25},
    "Ruth": {1:22,2:23,3:18,4:22},
    "1 Samuel": {1:28,2:36,3:21,4:22,5:12,6:21,7:17,8:22,9:27,10:27,11:15,12:25,13:23,14:52,15:35,16:23,17:58,18:30,19:24,20:42,21:16,22:23,23:29,24:23,25:44,26:25,27:12,28:25,29:11,30:31,31:13},
    "2 Samuel": {1:27,2:32,3:39,4:12,5:25,6:23,7:29,8:18,9:13,10:19,11:27,12:31,13:39,14:33,15:37,16:23,17:29,18:33,19:43,20:26,21:22,22:51,23:39,24:25},
    "1 Kings": {1:53,2:46,3:28,4:34,5:18,6:38,7:51,8:66,9:28,10:29,11:43,12:33,13:34,14:31,15:34,16:34,17:24,18:46,19:21,20:43,21:29,22:53},
    "2 Kings": {1:18,2:25,3:27,4:44,5:27,6:33,7:20,8:29,9:37,10:36,11:21,12:21,13:25,14:29,15:38,16:20,17:41,18:37,19:37,20:21,21:26,22:20,23:37,24:20,25:30},
    "1 Chronicles": {1:54,2:55,3:24,4:43,5:26,6:81,7:40,8:40,9:44,10:14,11:47,12:40,13:14,14:17,15:29,16:43,17:27,18:17,19:19,20:8,21:30,22:19,23:32,24:31,25:31,26:32,27:34,28:21,29:30},
    "2 Chronicles": {1:18,2:17,3:17,4:22,5:14,6:42,7:22,8:18,9:31,10:19,11:23,12:16,13:23,14:15,15:19,16:14,17:19,18:34,19:11,20:37,21:20,22:12,23:21,24:27,25:28,26:23,27:9,28:27,29:36,30:27,31:21,32:33,33:25,34:33,35:27,36:23},
    "Ezra": {1:11,2:70,3:13,4:24,5:17,6:22,7:28,8:36,9:15,10:44},
    "Nehemiah": {1:11,2:20,3:38,4:23,5:19,6:19,7:73,8:18,9:38,10:39,11:36,12:47,13:31},
    "Esther": {1:22,2:23,3:15,4:17,5:14,6:14,7:10,8:17,9:32,10:3},
    "Job": {1:22,2:13,3:26,4:21,5:27,6:30,7:21,8:22,9:35,10:22,11:20,12:25,13:28,14:22,15:35,16:22,17:16,18:21,19:29,20:29,21:34,22:30,23:17,24:25,25:6,26:14,27:23,28:28,29:25,30:31,31:40,32:22,33:33,34:37,35:16,36:33,37:24,38:41,39:30,40:24,41:34,42:17},
    "Psalms": {1:6,2:12,3:8,4:8,5:12,6:10,7:17,8:9,9:20,10:18,11:7,12:8,13:6,14:7,15:5,16:11,17:15,18:50,19:14,20:9,21:13,22:31,23:6,24:10,25:22,26:12,27:14,28:9,29:11,30:12,31:24,32:11,33:22,34:22,35:28,36:12,37:40,38:22,39:13,40:17,41:13,42:11,43:5,44:26,45:17,46:11,47:9,48:14,49:20,50:23,51:19,52:9,53:6,54:7,55:23,56:13,57:11,58:11,59:17,60:12,61:8,62:12,63:11,64:10,65:13,66:20,67:7,68:35,69:36,70:5,71:24,72:20,73:28,74:23,75:10,76:12,77:20,78:72,79:13,80:19,81:16,82:8,83:18,84:12,85:13,86:17,87:7,88:18,89:52,90:17,91:16,92:15,93:5,94:23,95:11,96:13,97:12,98:9,99:9,100:5,101:8,102:28,103:22,104:35,105:45,106:48,107:43,108:13,109:31,110:7,111:10,112:10,113:9,114:8,115:18,116:19,117:2,118:29,119:176,120:7,121:8,122:9,123:4,124:8,125:5,126:6,127:5,128:6,129:8,130:8,131:3,132:18,133:3,134:3,135:21,136:26,137:9,138:8,139:24,140:13,141:10,142:7,143:12,144:15,145:21,146:10,147:20,148:14,149:9,150:6},
    "Proverbs": {1:33,2:22,3:35,4:27,5:23,6:35,7:27,8:36,9:18,10:32,11:31,12:28,13:25,14:35,15:33,16:33,17:28,18:24,19:29,20:30,21:31,22:29,23:35,24:34,25:28,26:28,27:27,28:28,29:27,30:33,31:31},
    "Ecclesiastes": {1:18,2:26,3:22,4:16,5:20,6:12,7:29,8:17,9:18,10:20,11:10,12:14},
    "Song of Solomon": {1:17,2:17,3:11,4:16,5:16,6:13,7:13,8:14},
    "Isaiah": {1:31,2:22,3:26,4:6,5:30,6:13,7:25,8:23,9:21,10:34,11:16,12:6,13:22,14:32,15:9,16:14,17:14,18:7,19:25,20:6,21:17,22:25,23:18,24:23,25:12,26:21,27:13,28:29,29:24,30:33,31:9,32:20,33:24,34:17,35:10,36:22,37:38,38:22,39:8,40:31,41:29,42:25,43:28,44:28,45:25,46:13,47:15,48:22,49:26,50:11,51:23,52:15,53:12,54:17,55:13,56:12,57:21,58:14,59:21,60:22,61:11,62:12,63:19,64:12,65:25,66:24},
    "Jeremiah": {1:19,2:37,3:25,4:31,5:31,6:30,7:34,8:22,9:26,10:25,11:23,12:17,13:27,14:22,15:21,16:21,17:27,18:23,19:15,20:18,21:14,22:30,23:40,24:10,25:38,26:24,27:22,28:17,29:32,30:24,31:40,32:44,33:26,34:22,35:19,36:32,37:21,38:28,39:18,40:16,41:18,42:22,43:13,44:30,45:5,46:28,47:7,48:47,49:39,50:46,51:64,52:34},
    "Lamentations": {1:22,2:22,3:66,4:22,5:22},
    "Ezekiel": {1:28,2:10,3:27,4:17,5:17,6:14,7:27,8:18,9:11,10:22,11:25,12:28,13:23,14:23,15:8,16:63,17:24,18:32,19:14,20:49,21:32,22:31,23:49,24:27,25:17,26:21,27:36,28:26,29:21,30:26,31:18,32:32,33:33,34:31,35:15,36:38,37:28,38:23,39:29,40:49,41:26,42:20,43:27,44:31,45:25,46:24,47:23,48:35},
    "Daniel": {1:21,2:49,3:30,4:37,5:31,6:28,7:28,8:27,9:27,10:21,11:45,12:13},
    "Hosea": {1:11,2:23,3:5,4:19,5:15,6:11,7:16,8:14,9:17,10:15,11:12,12:14,13:16,14:9},
    "Joel": {1:20,2:32,3:21},
    "Amos": {1:15,2:16,3:15,4:13,5:27,6:14,7:17,8:14,9:15},
    "Obadiah": {1:21},
    "Jonah": {1:17,2:10,3:10,4:11},
    "Micah": {1:16,2:13,3:12,4:14,5:15,6:16,7:20},
    "Nahum": {1:15,2:13,3:19},
    "Habakkuk": {1:17,2:20,3:19},
    "Zephaniah": {1:18,2:15,3:20},
    "Haggai": {1:15,2:23},
    "Zechariah": {1:21,2:13,3:10,4:14,5:11,6:15,7:14,8:23,9:17,10:12,11:17,12:14,13:9,14:21},
    "Malachi": {1:14,2:17,3:18,4:6},
    "Matthew": {1:25,2:23,3:17,4:25,5:48,6:34,7:29,8:34,9:38,10:42,11:30,12:50,13:58,14:36,15:39,16:28,17:27,18:35,19:30,20:34,21:46,22:46,23:39,24:51,25:46,26:75,27:66,28:20},
    "Mark": {1:45,2:28,3:35,4:41,5:43,6:56,7:37,8:38,9:50,10:52,11:33,12:44,13:37,14:72,15:47,16:20},
    "Luke": {1:80,2:52,3:38,4:44,5:39,6:49,7:50,8:56,9:62,10:42,11:54,12:59,13:35,14:35,15:32,16:31,17:37,18:43,19:48,20:47,21:38,22:71,23:56,24:53},
    "John": {1:51,2:25,3:36,4:54,5:47,6:71,7:53,8:59,9:41,10:42,11:57,12:50,13:38,14:31,15:27,16:33,17:26,18:40,19:42,20:31,21:25},
    "Acts": {1:26,2:47,3:26,4:37,5:42,6:15,7:60,8:40,9:43,10:48,11:30,12:25,13:52,14:28,15:41,16:40,17:34,18:28,19:41,20:38,21:40,22:30,23:35,24:27,25:27,26:32,27:44,28:31},
    "Romans": {1:32,2:29,3:31,4:25,5:21,6:23,7:25,8:39,9:33,10:21,11:36,12:21,13:14,14:23,15:33,16:27},
    "1 Corinthians": {1:31,2:16,3:23,4:21,5:13,6:20,7:40,8:13,9:27,10:33,11:34,12:31,13:13,14:40,15:58,16:24},
    "2 Corinthians": {1:24,2:17,3:18,4:18,5:21,6:18,7:16,8:24,9:15,10:18,11:33,12:21,13:14},
    "Galatians": {1:24,2:21,3:29,4:31,5:26,6:18},
    "Ephesians": {1:23,2:22,3:21,4:32,5:33,6:24},
    "Philippians": {1:30,2:30,3:21,4:23},
    "Colossians": {1:29,2:23,3:25,4:18},
    "1 Thessalonians": {1:10,2:20,3:13,4:18,5:28},
    "2 Thessalonians": {1:12,2:17,3:18},
    "1 Timothy": {1:20,2:15,3:16,4:16,5:25,6:21},
    "2 Timothy": {1:18,2:26,3:17,4:22},
    "Titus": {1:16,2:15,3:15},
    "Philemon": {1:25},
    "Hebrews": {1:14,2:18,3:19,4:16,5:14,6:20,7:28,8:13,9:28,10:39,11:40,12:29,13:25},
    "James": {1:27,2:26,3:18,4:17,5:20},
    "1 Peter": {1:25,2:25,3:22,4:19,5:14},
    "2 Peter": {1:21,2:22,3:18},
    "1 John": {1:10,2:29,3:24,4:21,5:21},
    "2 John": {1:13},
    "3 John": {1:14},
    "Jude": {1:25},
    "Revelation": {1:20,2:29,3:22,4:11,5:14,6:17,7:17,8:13,9:21,10:11,11:19,12:17,13:18,14:20,15:8,16:21,17:18,18:24,19:21,20:15,21:27,22:21}
}

def audit_bsb():
    """Run full audit on BSB file."""
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    print(f"File size: {len(content):,} characters, {len(lines):,} lines")
    print("="*70)
    
    # Track structures
    books_found = []
    current_book = None
    current_chapter = None
    book_chapters = defaultdict(set)
    chapter_verses = defaultdict(lambda: defaultdict(list))
    verse_lines = defaultdict(list)
    
    # Issues
    issues = {
        'duplicate_books': [],
        'duplicate_chapters': [],
        'duplicate_verses': [],
        'missing_verse_markers': [],
        'invalid_chapter_numbers': [],
        'verse_number_gaps': [],
        'formatting_issues': [],
        'suspicious_verse_numbers': []
    }
    
    book_header_pattern = re.compile(r'^## (.+)$')
    chapter_pattern = re.compile(r'^### Chapter (\d+)$')
    verse_pattern = re.compile(r'^\*\*v(\d+)\*\*')
    section_header_pattern = re.compile(r'^#### (.+)$')
    footnote_pattern = re.compile(r'^\[\^(\d+)\]:')
    
    for line_num, line in enumerate(lines, 1):
        # Book headers
        bm = book_header_pattern.match(line)
        if bm:
            book_name = bm.group(1)
            if book_name in books_found:
                issues['duplicate_books'].append((line_num, book_name))
            else:
                books_found.append(book_name)
            current_book = book_name
            current_chapter = None
            continue
        
        # Chapter headers
        cm = chapter_pattern.match(line)
        if cm:
            ch_num = int(cm.group(1))
            if current_book:
                if ch_num in book_chapters[current_book]:
                    issues['duplicate_chapters'].append((line_num, current_book, ch_num))
                book_chapters[current_book].add(ch_num)
                
                # Check for invalid chapter numbers
                expected_chapters = KNOWN_CHAPTER_COUNTS.get(current_book)
                if expected_chapters and ch_num > expected_chapters:
                    issues['invalid_chapter_numbers'].append((line_num, current_book, ch_num, expected_chapters))
            current_chapter = ch_num
            continue
        
        # Verse lines
        vm = verse_pattern.match(line)
        if vm and current_book and current_chapter:
            vnum = int(vm.group(1))
            
            # Check for duplicate verses
            if vnum in chapter_verses[current_book][current_chapter]:
                issues['duplicate_verses'].append((line_num, current_book, current_chapter, vnum))
            
            chapter_verses[current_book][current_chapter].append(vnum)
            verse_lines[(current_book, current_chapter, vnum)].append((line_num, line))
            
            # Check for suspicious verse numbers
            expected_verses = VERSE_COUNTS.get(current_book, {}).get(current_chapter, 0)
            if expected_verses and vnum > expected_verses:
                issues['suspicious_verse_numbers'].append((line_num, current_book, current_chapter, vnum, expected_verses))
    
    # Check for verse gaps (missing verses)
    for book, chapters in chapter_verses.items():
        for ch, verses in chapters.items():
            if not verses:
                continue
            max_v = max(verses)
            expected = VERSE_COUNTS.get(book, {}).get(ch, max_v)
            
            # Check for gaps
            expected_set = set(range(1, expected + 1))
            actual_set = set(verses)
            missing = expected_set - actual_set
            
            if missing:
                issues['verse_number_gaps'].append((book, ch, sorted(missing)))
    
    # Print findings
    print(f"\nBOOKS FOUND: {len(books_found)}")
    print(f"Expected: 66 books")
    if len(books_found) != 66:
        print(f"  ❌ MISMATCH: Found {len(books_found)} books, expected 66")
    else:
        print(f"  ✓ Correct book count")
    
    # Check for missing books
    expected_books = set(KNOWN_CHAPTER_COUNTS.keys())
    found_books = set(books_found)
    missing_books = expected_books - found_books
    extra_books = found_books - expected_books
    
    if missing_books:
        print(f"\n  ❌ MISSING BOOKS ({len(missing_books)}):")
        for b in sorted(missing_books):
            print(f"    - {b}")
    
    if extra_books:
        print(f"\n  ❌ EXTRA/UNEXPECTED BOOKS ({len(extra_books)}):")
        for b in sorted(extra_books):
            print(f"    - {b}")
    
    print(f"\nCHAPTERS:")
    total_chapters = sum(len(chs) for chs in book_chapters.values())
    expected_total = sum(KNOWN_CHAPTER_COUNTS.values())
    print(f"  Found: {total_chapters} chapters (expected: {expected_total})")
    
    chapter_issues = []
    for book, expected in KNOWN_CHAPTER_COUNTS.items():
        found = len(book_chapters.get(book, set()))
        if found != expected:
            chapter_issues.append((book, found, expected))
    
    if chapter_issues:
        print(f"  ❌ Chapter count issues in {len(chapter_issues)} books:")
        for book, found, expected in chapter_issues[:20]:
            print(f"    - {book}: found {found}, expected {expected}")
        if len(chapter_issues) > 20:
            print(f"    ... and {len(chapter_issues) - 20} more")
    else:
        print(f"  ✓ All books have correct chapter counts")
    
    print(f"\nVERSES:")
    total_verses = sum(sum(len(vs) for vs in chs.values()) for chs in chapter_verses.values())
    print(f"  Total verse entries found: {total_verses:,}")
    
    # Count expected verses
    expected_verse_total = sum(sum(ch.values()) for ch in VERSE_COUNTS.values())
    print(f"  Expected total verses: {expected_verse_total:,}")
    
    if total_verses != expected_verse_total:
        print(f"  ⚠ Verse count differs by {total_verses - expected_verse_total}")
    
    # Report specific issues
    print(f"\n" + "="*70)
    print("DETAILED ISSUES:")
    print("="*70)
    
    if issues['duplicate_books']:
        print(f"\n❌ DUPLICATE BOOK HEADERS ({len(issues['duplicate_books'])}):")
        for line, book in issues['duplicate_books'][:10]:
            print(f"  Line {line}: {book}")
        if len(issues['duplicate_books']) > 10:
            print(f"  ... and {len(issues['duplicate_books']) - 10} more")
    
    if issues['duplicate_chapters']:
        print(f"\n❌ DUPLICATE CHAPTER HEADERS ({len(issues['duplicate_chapters'])}):")
        for line, book, ch in issues['duplicate_chapters'][:15]:
            print(f"  Line {line}: {book} {ch}")
        if len(issues['duplicate_chapters']) > 15:
            print(f"  ... and {len(issues['duplicate_chapters']) - 15} more")
    
    if issues['duplicate_verses']:
        print(f"\n❌ DUPLICATE VERSE MARKERS ({len(issues['duplicate_verses'])}):")
        for line, book, ch, v in issues['duplicate_verses'][:15]:
            print(f"  Line {line}: {book} {ch}:{v}")
        if len(issues['duplicate_verses']) > 15:
            print(f"  ... and {len(issues['duplicate_verses']) - 15} more")
    
    if issues['invalid_chapter_numbers']:
        print(f"\n❌ INVALID CHAPTER NUMBERS ({len(issues['invalid_chapter_numbers'])}):")
        for line, book, ch, expected in issues['invalid_chapter_numbers'][:15]:
            print(f"  Line {line}: {book} chapter {ch} (max should be {expected})")
        if len(issues['invalid_chapter_numbers']) > 15:
            print(f"  ... and {len(issues['invalid_chapter_numbers']) - 15} more")
    
    if issues['verse_number_gaps']:
        print(f"\n❌ MISSING VERSES ({len(issues['verse_number_gaps'])} chapters affected):")
        for book, ch, missing in issues['verse_number_gaps'][:20]:
            if len(missing) <= 5:
                print(f"  {book} {ch}: missing verses {missing}")
            else:
                print(f"  {book} {ch}: missing {len(missing)} verses ({missing[:5]}...)")
        if len(issues['verse_number_gaps']) > 20:
            print(f"  ... and {len(issues['verse_number_gaps']) - 20} more chapters with gaps")
    
    if issues['suspicious_verse_numbers']:
        print(f"\n⚠ SUSPICIOUSLY HIGH VERSE NUMBERS ({len(issues['suspicious_verse_numbers'])}):")
        for line, book, ch, v, expected in issues['suspicious_verse_numbers'][:15]:
            print(f"  Line {line}: {book} {ch}:{v} (chapter only has {expected} verses)")
        if len(issues['suspicious_verse_numbers']) > 15:
            print(f"  ... and {len(issues['suspicious_verse_numbers']) - 15} more")
    
    # Check formatting issues
    print(f"\nFORMAT ANALYSIS:")
    
    # Check for curly quotes
    curly_single = content.count('\u2019') + content.count('\u2018')
    curly_double = content.count('\u201c') + content.count('\u201d')
    if curly_single or curly_double:
        print(f"  ⚠ Curly quotes found: {curly_single} single, {curly_double} double")
    else:
        print(f"  ✓ No curly quotes (all straight ASCII)")
    
    # Check footnote format
    footnote_count = len(footnote_pattern.findall(content))
    print(f"  Footnotes found: {footnote_count}")
    
    # Check section headers
    section_headers = section_header_pattern.findall(content)
    print(f"  Section headers found: {len(section_headers)}")
    
    # Summary
    print(f"\n" + "="*70)
    print("SUMMARY:")
    total_issues = sum(len(v) for v in issues.values())
    print(f"  Total issues found: {total_issues}")
    
    if total_issues == 0:
        print(f"  ✓✓✓ NO ERRORS FOUND - File appears clean!")
    else:
        print(f"  ⚠ File needs attention (see details above)")
    
    return issues, books_found, book_chapters, chapter_verses

if __name__ == "__main__":
    audit_bsb()
