#!/usr/bin/env python3
"""
Replace esv.md chapters with API-verified text (one book at a time).
With retry logic for rate limiting (429 errors).
"""

import re, sys, json, urllib.request, urllib.parse, time

MD_PATH = "/Users/silas/.openclaw/workspace/bibles/esv/esv.md"
API_KEY = "9480e52697feb72baa1453cbd76b9d976ed1c5e3"
API_BASE = "https://api.esv.org/v3/passage/text/"
REQUEST_DELAY = 1.05
MAX_RETRIES = 5


def api_get(passage):
    """Fetch from API with retry logic for rate limiting."""
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
    
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                return data.get("passages", [])
        except urllib.error.HTTPError as e:
            if e.code == 429:
                # Rate limited - wait and retry with exponential backoff
                wait_time = (2 ** attempt) + 1  # 1, 3, 9, 17, 33 seconds
                print(f"  Ch {passage}: Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                print(f"  API ERROR: {e}")
                return []
        except Exception as e:
            print(f"  API ERROR: {e}")
            return []
    
    print(f"  Ch {passage}: Max retries exceeded")
    return []


def parse_api_chapter(api_text):
    parts = re.split(r'(\[(\d+)\])', api_text)
    verses = []
    for i in range(1, len(parts), 3):
        if i+2 < len(parts):
            verses.append((int(parts[i+1]), parts[i+2].strip()))
    return verses


def load_books_and_lines():
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    books = []
    for i, line in enumerate(lines):
        m = re.match(r'^## ([^\n]+)$', line)
        if m:
            books.append((m.group(1), i))
    return books, lines


def process_book(book_name):
    books, lines = load_books_and_lines()
    
    # Find book range
    book_info = None
    for bn, bs in books:
        if bn == book_name:
            book_info = (bn, bs)
            break
    if not book_info:
        print(f"Book '{book_name}' not found!")
        return 0
    
    _, book_start = book_info
    book_end = len(lines)
    for bn, bs in books:
        if bs > book_start:
            book_end = bs
            break
    
    # Find chapters
    chapters = []
    for i in range(book_start, book_end):
        m = re.match(r'^### Chapter (\d+)$', lines[i].strip())
        if m:
            chapters.append((int(m.group(1)), i))
    
    if not chapters:
        print(f"No chapters found for '{book_name}'")
        return 0
    
    replaced = 0
    # Process in REVERSE so earlier positions stay valid
    for ch_num, ch_start in reversed(chapters):
        # Find ch_end (next chapter header or book end)
        ch_end = book_end
        for i in range(ch_start + 1, book_end):
            if re.match(r'^### Chapter \d+$', lines[i].strip()):
                ch_end = i
                break
        
        # Fetch from API
        time.sleep(REQUEST_DELAY)
        result = api_get(f"{book_name} {ch_num}")
        if not result:
            print(f"  Ch {ch_num}: API error")
            continue
        
        verses = parse_api_chapter(result[0])
        if not verses:
            print(f"  Ch {ch_num}: no verses parsed")
            continue
        
        # Build replacement
        new_ch = [f"### Chapter {ch_num}\n"]
        for vnum, vtext in verses:
            new_ch.append(f"**v{vnum}** {vtext}\n")
        
        lines[ch_start:ch_end] = new_ch
        # Adjust book_end since lines list changed
        delta = len(new_ch) - (ch_end - ch_start)
        book_end += delta
        
        replaced += 1
        print(f"  Ch {ch_num}: {len(verses)} verses")
    
    with open(MD_PATH, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    return replaced


if __name__ == "__main__":
    book = sys.argv[1] if len(sys.argv) > 1 else None
    if not book:
        print("Usage: python3 esv_replace_chapters.py <book_name>")
        sys.exit(1)
    
    n = process_book(book)
    print(f"\n{book}: {n} chapters replaced")
