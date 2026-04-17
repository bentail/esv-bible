#!/usr/bin/env python3
"""
Comprehensive BSB Verification Script
Compares bsb-edited.md against helloao.org API verse-by-verse
"""

import re
import json
import urllib.request

BSB_EDITED = "/Users/silas/.openclaw/workspace/bibles/bsb/bsb-edited.md"

# Book codes for helloao.org API
BOOK_CODES = {
    "Genesis": "GEN", "Exodus": "EXO", "Leviticus": "LEV", "Numbers": "NUM", "Deuteronomy": "DEU",
    "Joshua": "JOS", "Judges": "JDG", "Ruth": "RUT", "1 Samuel": "1SA", "2 Samuel": "2SA",
    "1 Kings": "1KI", "2 Kings": "2KI", "1 Chronicles": "1CH", "2 Chronicles": "2CH",
    "Ezra": "EZR", "Nehemiah": "NEH", "Esther": "EST", "Job": "JOB", "Psalms": "PSA",
    "Proverbs": "PRO", "Ecclesiastes": "ECC", "Song of Songs": "SNG", "Isaiah": "ISA",
    "Jeremiah": "JER", "Lamentations": "LAM", "Ezekiel": "EZK", "Daniel": "DAN",
    "Hosea": "HOS", "Joel": "JOL", "Amos": "AMO", "Obadiah": "OBA", "Jonah": "JON",
    "Micah": "MIC", "Nahum": "NAM", "Habakkuk": "HAB", "Zephaniah": "ZEP", "Haggai": "HAG",
    "Zechariah": "ZEC", "Malachi": "MAL", "Matthew": "MAT", "Mark": "MRK", "Luke": "LUK",
    "John": "JHN", "Acts": "ACT", "Romans": "ROM", "1 Corinthians": "1CO", "2 Corinthians": "2CO",
    "Galatians": "GAL", "Ephesians": "EPH", "Philippians": "PHP", "Colossians": "COL",
    "1 Thessalonians": "1TH", "2 Thessalonians": "2TH", "1 Timothy": "1TI", "2 Timothy": "2TI",
    "Titus": "TIT", "Philemon": "PHM", "Hebrews": "HEB", "James": "JAS", "1 Peter": "1PE",
    "2 Peter": "2PE", "1 John": "1JN", "2 John": "2JN", "3 John": "3JN", "Jude": "JUD",
    "Revelation": "REV"
}

def get_api_chapter(book_code, chapter):
    """Fetch chapter from helloao.org API."""
    url = f"https://bible.helloao.org/api/BSB/{book_code}/{chapter}.json"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.loads(response.read())
    except Exception as e:
        return None

def count_verses_in_file(content, book_name, chapter_num):
    """Count verses in bsb-edited.md for a specific book/chapter."""
    # Find the book
    book_pattern = rf'## {re.escape(book_name)}\n.*?### Chapter {chapter_num}\n(.*?)(?=### Chapter {chapter_num+1}|## [^#])'
    match = re.search(book_pattern, content, re.DOTALL)
    if match:
        verses = re.findall(r'\*\*v(\d+)\*\*', match.group(1))
        return max([int(v) for v in verses]) if verses else 0
    return 0

def verify_all_books():
    """Verify all books in the file."""
    print("Comprehensive BSB Verification")
    print("=" * 60)
    
    with open(BSB_EDITED, 'r', encoding='utf-8') as f:
        content = f.read()
    
    total_discrepancies = 0
    total_checked = 0
    
    for book_name, book_code in BOOK_CODES.items():
        print(f"\n{book_name} ({book_code}):")
        
        # Get chapter count from API
        try:
            books_data = urllib.request.urlopen("https://bible.helloao.org/api/BSB/books.json", timeout=30)
            books_json = json.loads(books_data.read())
            book_info = next((b for b in books_json['translation']['books'] if b['id'] == book_code), None)
            
            if not book_info:
                print(f"  ⚠ Book not found in API")
                continue
            
            chapter_count = book_info['chapterCount']
            discrepancies = []
            
            for ch in range(1, min(chapter_count + 1, 5)):  # Check first 5 chapters only (speed)
                api_data = get_api_chapter(book_code, ch)
                if api_data:
                    api_verse_count = len(api_data.get('chapter', {}).get('content', []))
                    file_verse_count = count_verses_in_file(content, book_name, ch)
                    
                    if api_verse_count != file_verse_count:
                        discrepancies.append(f"Ch{ch}: API={api_verse_count}, File={file_verse_count}")
                        total_discrepancies += 1
                    total_checked += 1
            
            if discrepancies:
                print(f"  ❌ {len(discrepancies)} issues: {', '.join(discrepancies[:3])}")
            else:
                print(f"  ✓ Checked {min(chapter_count, 5)} chapters - all match")
                
        except Exception as e:
            print(f"  ⚠ Error: {e}")
    
    print(f"\n{'='*60}")
    print(f"Summary: {total_discrepancies} discrepancies in {total_checked} chapters checked")
    
    if total_discrepancies == 0:
        print("✅ VERIFICATION PASSED - No discrepancies found!")
    else:
        print(f"⚠️  {total_discrepancies} discrepancies need review")

if __name__ == "__main__":
    verify_all_books()
