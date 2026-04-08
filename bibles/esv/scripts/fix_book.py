#!/usr/bin/env python3
"""
Fix any Bible book using ESV API.
Usage: python3 fix_book.py <BookName>
Example: python3 fix_book.py "Genesis"
"""

import re, json, urllib.request, urllib.parse, time, sys, shutil

MD_PATH = "/Users/silas/.openclaw/workspace/bibles/esv/esv.md"
API_KEY = "9480e52697feb72baa1453cbd76b9d976ed1c5e3"
API_BASE = "https://api.esv.org/v3/passage/text/"
REQUEST_DELAY = 1.05

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
    
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                return data.get("passages", [])
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait_time = (2 ** attempt) + 1
                print(f"    Rate limit - waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            print(f"    API ERROR: {e}")
            return []
        except Exception as e:
            print(f"    API ERROR: {e}")
            return []
    return []

def parse_verses(api_text):
    parts = re.split(r'(\[(\d+)\])', api_text)
    verses = []
    for i in range(1, len(parts), 3):
        if i+2 < len(parts):
            verses.append((int(parts[i+1]), parts[i+2].strip()))
    return verses

def fix_book(book_name):
    print(f"\n{'='*60}")
    print(f"FIXING: {book_name}")
    print(f"{'='*60}")
    
    # Backup
    backup_path = MD_PATH + ".backup"
    shutil.copy(MD_PATH, backup_path)
    
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find book
    book_start = None
    for i, line in enumerate(lines):
        if line.startswith(f"## {book_name}"):
            book_start = i
            print(f"Found {book_name} at line {i+1}")
            break
    
    if book_start is None:
        print(f"ERROR: {book_name} not found!")
        return
    
    # Find chapters
    chapters = []
    for i in range(book_start, len(lines)):
        m = re.match(r'^### Chapter (\d+)$', lines[i].strip())
        if m:
            chapters.append((int(m.group(1)), i))
        elif i > book_start and lines[i].startswith("## ") and book_name not in lines[i]:
            break
    
    print(f"Found {len(chapters)} chapters")
    
    fixed = 0
    checked = 0
    
    # Process each chapter
    for ch_num, ch_idx in chapters:
        # Find chapter content
        ch_end = len(lines)
        for i in range(ch_idx + 1, len(lines)):
            if re.match(r'^### Chapter \d+$', lines[i].strip()):
                ch_end = i
                break
            if i > ch_idx and lines[i].startswith("## "):
                ch_end = i
                break
        
        # Count current verses
        current = []
        for i in range(ch_idx, ch_end):
            m = re.match(r'^\*\*v(\d+)\*\*', lines[i].strip())
            if m:
                current.append(int(m.group(1)))
        
        checked += 1
        
        # Fetch API
        time.sleep(REQUEST_DELAY)
        result = api_get(f"{book_name} {ch_num}")
        
        if not result:
            print(f"  Ch {ch_num}: API failed (had {len(current)} verses)")
            continue
        
        api_verses = parse_verses(result[0])
        api_nums = [v[0] for v in api_verses]
        
        missing = sorted(set(api_nums) - set(current))
        
        if missing:
            print(f"  Ch {ch_num}: FIXED - had {len(current)}, API has {len(api_verses)}, missing {len(missing)} verses")
            
            # Replace chapter
            new_ch = [f"### Chapter {ch_num}\n", "\n"]
            for vnum, vtext in api_verses:
                new_ch.append(f"**v{vnum}** {vtext}\n")
            
            lines[ch_idx:ch_end] = new_ch
            fixed += 1
        else:
            print(f"  Ch {ch_num}: OK ({len(current)} verses)")
    
    # Save
    with open(MD_PATH, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"\n{'='*60}")
    print(f"SUMMARY: {checked} chapters checked, {fixed} chapters fixed")
    print(f"Backup: {backup_path}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 fix_book.py <BookName>")
        print("Example: python3 fix_book.py Genesis")
        sys.exit(1)
    
    book = sys.argv[1]
    fix_book(book)
