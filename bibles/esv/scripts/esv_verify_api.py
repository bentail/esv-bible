#!/usr/bin/env python3
"""
Verify and fix esv.md verses against ESV.org REST API.
Uses API as ground truth, fixes missing/wrong verses.
"""

import re, sys, json, urllib.request, urllib.parse, time

MD_PATH = "/Users/silas/.openclaw/workspace/bibles/esv/esv.md"
API_KEY = "9480e52697feb72baa1453cbd76b9d976ed1c5e3"
API_BASE = "https://api.esv.org/v3/passage/text/"
REQUEST_DELAY = 1.1  # stay under 60/min rate limit


def api_get(passage):
    params = {
        "q": passage,
        "include-passage-references": "false",
        "include-first-verse-number": "false",
        "include-verse-numbers": "true",
        "include-footnotes": "false",
        "include-headings": "false",
        "include-surrounding-chapters": "false",
    }
    url = API_BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Token {API_KEY}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data.get("passages", [])
    except Exception as e:
        print(f"  API ERROR: {e}")
        return []


def norm(s):
    """Normalize text for comparison."""
    if not s:
        return ""
    s = s.strip()
    s = s.replace('\u2019', "'").replace('\u2018', "'")
    s = s.replace('\u201c', '"').replace('\u201d', '"')
    s = s.replace('\u2014', ' ').replace('\u2013', ' ')
    # Remove parenthetical notes like (ESV)
    s = re.sub(r'\s*\(ESV\)\s*$', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s


def parse_api_verses(api_text):
    """Parse API text into {verse_num: verse_text} dict.
    API format: [1] verse one text [2] verse two text [3] verse three
    """
    verses = {}
    # Find all [n] markers and their positions
    parts = re.split(r'(\[(\d+)\])', api_text)
    # parts alternates: [text, '[n]', 'n', text, '[m]', 'm', ...]
    for i in range(1, len(parts), 3):
        if i+1 < len(parts):
            vnum = int(parts[i+1])
            vtext = parts[i+2].strip() if i+2 < len(parts) else ""
            verses[vnum] = vtext
    return verses


def get_md_books_and_lines():
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    books = []
    for i, line in enumerate(lines):
        m = re.match(r'^## ([^\n]+)$', line)
        if m:
            books.append((m.group(1), i))
    return books, lines


def get_chapters_in_book(lines, book_start, book_end):
    chapters = set()
    for i in range(book_start, book_end):
        m = re.match(r'^### Chapter (\d+)$', lines[i].strip())
        if m:
            chapters.add(int(m.group(1)))
    return sorted(chapters)


def get_md_verses(lines, book_start, book_end, chapter):
    """Get {verse_num: verse_text} for a specific chapter."""
    verses = {}
    current_chapter = None
    for i in range(book_start, book_end):
        line = lines[i]
        cm = re.match(r'^### Chapter (\d+)$', line.strip())
        if cm:
            current_chapter = int(cm.group(1))
            continue
        if current_chapter != chapter:
            continue
        vm = re.match(r'^\*\*v(\d+)\*\*(.*?)(?=\*\*v\d+\*\*|$)', line, re.DOTALL)
        if vm:
            vnum = int(vm.group(1))
            text = re.sub(r'\s+', ' ', vm.group(2).strip())
            verses[vnum] = text
    return verses


def replace_verse(lines, book_start, book_end, chapter, verse_num, new_text):
    """Replace a specific verse in the lines list (in-place)."""
    current_chapter = None
    for i in range(book_start, book_end):
        if re.match(r'^### Chapter \d+$', lines[i].strip()):
            current_chapter = int(re.match(r'^### Chapter (\d+)$', lines[i].strip()).group(1))
            continue
        if current_chapter != chapter:
            continue
        vm = re.match(r'^(\*\*v)(\d+)(\*\*.*)$', lines[i])
        if vm and int(vm.group(2)) == verse_num:
            lines[i] = f"**v{verse_num}** {new_text}\n"
            return True
    return False


def insert_missing_verses(lines, book_start, book_end, chapter, missing, api_verses):
    """Insert missing verses into lines list (in-place).
    Finds the position after the last verse of the given chapter."""
    if not missing:
        return 0
    
    # Find the chapter start and end
    ch_start = ch_end = None
    for i in range(book_start, book_end):
        cm = re.match(r'^### Chapter (\d+)$', lines[i].strip())
        if cm:
            cn = int(cm.group(1))
            if cn == chapter:
                ch_start = i
            elif ch_start is not None:
                ch_end = i
                break
    
    if ch_start is None:
        print(f"    Chapter {chapter} not found")
        return 0
    
    if ch_end is None:
        ch_end = book_end
    
    # Find the last verse line within this chapter
    last_v_idx = None
    for i in range(ch_start, ch_end):
        if re.match(r'^\*\*v(\d+)\*\*', lines[i]):
            last_v_idx = i
    
    if last_v_idx is None:
        print(f"    No verse lines found in chapter {chapter}")
        return 0
    
    # Insert after last verse line
    insert_idx = last_v_idx + 1
    
    # Verify we're not inserting in the middle of verse text
    # (if next line looks like continuation, skip to after it)
    while insert_idx < ch_end:
        next_line = lines[insert_idx].strip()
        # If next line is empty, a section header, next chapter, or another verse, stop
        if not next_line:
            insert_idx += 1
            continue
        if re.match(r'^### Chapter ', next_line):
            break
        if re.match(r'^## ', next_line):
            break
        if re.match(r'^\*\*v\d+\*\*', next_line):
            break
        # It's verse text continuation - skip
        insert_idx += 1
    
    new_lines = []
    for vnum in sorted(missing):
        if vnum in api_verses:
            new_lines.append(f"**v{vnum}** {api_verses[vnum]}\n")
    
    if new_lines:
        lines[insert_idx:insert_idx] = new_lines
        return len(new_lines)
    return 0


def process_book(book_name):
    books, lines = get_md_books_and_lines()
    
    # Find book
    book_info = None
    for bn, bstart in books:
        if bn == book_name:
            book_info = (bn, bstart)
            break
    if not book_info:
        print(f"Book '{book_name}' not found!")
        return 0, 0, 0
    
    _, book_start = book_info
    book_end = None
    for bn, bstart in books:
        if bstart > book_start:
            book_end = bstart
            break
    if book_end is None:
        book_end = len(lines)
    
    chapters = get_chapters_in_book(lines, book_start, book_end)
    if not chapters:
        return 0, 0, 0
    
    fixed = 0
    missing = 0
    
    for ch in chapters:
        # Get MD verses
        md_verses = get_md_verses(lines, book_start, book_end, ch)
        
        # Get API max verse
        time.sleep(REQUEST_DELAY)
        passage = f"{book_name} {ch}:1-{ch}:999"
        passages = api_get(passage)
        if not passages:
            print(f"  Ch {ch}: API error")
            continue
        
        api_verses = parse_api_verses(passages[0])
        if not api_verses:
            print(f"  Ch {ch}: no API verses parsed")
            continue
        
        max_api = max(api_verses.keys())
        max_md = max(md_verses.keys()) if md_verses else 0
        
        # Compare and fix existing verses
        for vnum in sorted(md_verses.keys()):
            if vnum not in api_verses:
                # Verse exists in MD but not in API - mark as issue
                print(f"  Ch {ch} v{vnum}: extra in MD (no API match)")
                continue
            
            md_norm = norm(md_verses[vnum])
            api_norm = norm(api_verses[vnum])
            
            if md_norm != api_norm:
                # Fix the verse
                ok = replace_verse(lines, book_start, book_end, ch, vnum, api_verses[vnum])
                if ok:
                    fixed += 1
                    print(f"  Ch {ch} v{vnum}: fixed")
        
        # Check for missing verses
        missing_in_md = [v for v in range(1, max_api + 1) if v not in md_verses]
        if missing_in_md:
            print(f"  Ch {ch}: missing {missing_in_md}")
            n_inserted = insert_missing_verses(lines, book_start, book_end, ch, missing_in_md, api_verses)
            missing += len(missing_in_md)
    
    # Write back
    with open(MD_PATH, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    return fixed, missing


if __name__ == "__main__":
    book = sys.argv[1] if len(sys.argv) > 1 else None
    if not book:
        print("Usage: python3 esv_verify_api.py <book_name>")
        sys.exit(1)
    
    fixed, missing = process_book(book)
    print(f"\n{book}: {fixed} fixed, {missing} inserted")
