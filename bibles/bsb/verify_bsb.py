#!/usr/bin/env python3
"""Verify BSB edited file against helloao.org API."""

import re
import json
import urllib.request

# Book definitions: (name, line_start, line_end, api_code)
BOOKS = [
    ("Genesis", "GEN"),
    ("Exodus", "EXO"),
    ("Leviticus", "LEV"),
    ("Numbers", "NUM"),
    ("Deuteronomy", "DEU"),
    ("Joshua", "JOS"),
    ("Judges", "JDG"),
    ("Ruth", "RUT"),
    ("1 Samuel", "1SA"),
    ("2 Samuel", "2SA"),
    ("1 Kings", "1KI"),
    ("2 Kings", "2KI"),
    ("1 Chronicles", "1CH"),
    ("2 Chronicles", "2CH"),
    ("Ezra", "EZR"),
    ("Nehemiah", "NEH"),
    ("Esther", "EST"),
]

def get_book_line_ranges():
    """Parse the file to find line ranges for each book."""
    with open("bsb-edited.md", "r") as f:
        lines = f.readlines()
    
    book_ranges = {}
    current_book = None
    for i, line in enumerate(lines):
        if line.startswith("## "):
            book_name = line[3:].strip()
            if current_book:
                book_ranges[current_book] = (start_line, i - 1)
            current_book = book_name
            start_line = i
    
    if current_book:
        book_ranges[current_book] = (start_line, len(lines) - 1)
    
    return book_ranges, lines

def count_verses_in_text(text):
    """Count verses (v1, v2, etc.) in text."""
    # Match **v{NUMBER}** pattern
    verses = re.findall(r'\*\*v(\d+)\*\*', text)
    if not verses:
        return {}
    
    max_verse = int(verses[-1])
    verse_set = set(int(v) for v in verses)
    
    # Return dict: verse_number -> True if present
    result = {i: i in verse_set for i in range(1, max_verse + 1)}
    return result

def get_verse_map_for_chapter(lines, chapter_start, chapter_end):
    """Get verse numbers present in a chapter's text block."""
    chapter_text = "".join(lines[chapter_start:chapter_end])
    return count_verses_in_text(chapter_text)

def find_chapters_in_book(lines, book_start, book_end):
    """Find chapter boundaries within a book's lines."""
    chapters = {}  # chapter_num -> (start_line, end_line)
    current_chapter = None
    chapter_start = book_start
    
    for i in range(book_start, book_end + 1):
        line = lines[i]
        m = re.match(r'^### Chapter (\d+)', line)
        if m:
            if current_chapter is not None:
                chapters[current_chapter] = (chapter_start, i - 1)
            current_chapter = int(m.group(1))
            chapter_start = i
    
    if current_chapter is not None:
        chapters[current_chapter] = (chapter_start, book_end)
    
    return chapters

def fetch_api_verses(api_code, chapter):
    """Fetch verse numbers from helloao.org API."""
    url = f"https://bible.helloao.org/api/BSB/{api_code}/{chapter}.json"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        verses = set()
        for item in data.get("chapter", {}).get("content", []):
            if item.get("type") == "verse":
                verses.add(item.get("number"))
        return verses
    except Exception as e:
        print(f"  ERROR fetching {api_code} {chapter}: {e}")
        return None

def verify_book(book_name, api_code, lines, book_start, book_end):
    """Verify a single book against API."""
    print(f"\n{'='*60}")
    print(f"VERIFYING: {book_name} ({api_code})")
    print(f"{'='*60}")
    
    chapters = find_chapters_in_book(lines, book_start, book_end)
    print(f"  Chapters found in file: {sorted(chapters.keys())}")
    
    # Get max chapter from API to know how many chapters to check
    api_chapters_url = f"https://bible.helloao.org/api/BSB/{api_code}/1.json"
    try:
        with urllib.request.urlopen(api_chapters_url, timeout=10) as response:
            data = json.loads(response.read().decode())
        max_chapter = data["book"]["numberOfChapters"]
        print(f"  Chapters according to API: {max_chapter}")
    except:
        max_chapter = max(chapters.keys()) if chapters else 0
    
    discrepancies = []
    
    # Check each chapter
    for ch in range(1, max_chapter + 1):
        if ch in chapters:
            start, end = chapters[ch]
            file_verses = get_verse_map_for_chapter(lines, start, end)
            
            if file_verses:
                file_max = max(file_verses.keys())
            else:
                file_max = 0
            
            api_verses = fetch_api_verses(api_code, ch)
            
            if api_verses is None:
                discrepancies.append(f"  {book_name} Chapter {ch}: Could not fetch API data")
                continue
            
            api_max = max(api_verses) if api_verses else 0
            
            print(f"  Chapter {ch}: file_max={file_max}, api_max={api_max}")
            
            # Compare
            if file_max != api_max:
                discrepancies.append(f"  {book_name} Chapter {ch}: MAX VERSE MISMATCH - file={file_max}, api={api_max}")
            
            # Check for missing/extra verses
            if file_verses and api_verses:
                api_set = set(api_verses)
                file_set = set(file_verses.keys())
                
                missing = api_set - file_set
                extra = file_set - api_set
                
                if missing:
                    discrepancies.append(f"  {book_name} Chapter {ch}: MISSING VERSES: {sorted(missing)}")
                if extra:
                    discrepancies.append(f"  {book_name} Chapter {ch}: EXTRA VERSES: {sorted(extra)}")
        else:
            # Chapter exists in API but not in file
            api_verses = fetch_api_verses(api_code, ch)
            if api_verses:
                discrepancies.append(f"  {book_name} Chapter {ch}: MISSING from file (API has {len(api_verses)} verses)")
    
    return discrepancies

def main():
    book_ranges, lines = get_book_line_ranges()
    
    all_discrepancies = []
    
    for book_name, api_code in BOOKS:
        if book_name in book_ranges:
            book_start, book_end = book_ranges[book_name]
            disc = verify_book(book_name, api_code, lines, book_start, book_end)
            all_discrepancies.extend(disc)
        else:
            print(f"Book not found in file: {book_name}")
            all_discrepancies.append(f"Book not found in file: {book_name}")
    
    # Write report
    report = []
    report.append("# BSB Verification Report: Torah + History (17 Books)")
    report.append("")
    report.append(f"Generated: 2026-04-08")
    report.append(f"Source: bsb-edited.md vs helloao.org API")
    report.append("")
    report.append("## Summary")
    report.append("")
    report.append(f"Total books checked: {len(BOOKS)}")
    report.append(f"Total discrepancies found: {len(all_discrepancies)}")
    report.append("")
    
    if all_discrepancies:
        report.append("## Discrepancies")
        report.append("")
        for d in all_discrepancies:
            report.append(d)
    else:
        report.append("## Result: ✅ ALL CHECKS PASSED")
        report.append("")
        report.append("All 17 books match the helloao.org API verse counts.")
    
    report_text = "\n".join(report)
    print("\n" + "="*60)
    print("FINAL REPORT")
    print("="*60)
    print(report_text)
    
    with open("/Users/silas/.openclaw/workspace/bibles/bsb/verification_torah_history.md", "w") as f:
        f.write(report_text)
    
    print(f"\nReport written to verification_torah_history.md")

if __name__ == "__main__":
    main()
