#!/usr/bin/env python3
"""More efficient BSB verification - streaming approach."""

import re
import json
import urllib.request

BOOKS_INFO = [
    ("Genesis", "GEN", 50, 1533),
    ("Exodus", "EXO", 40, 1213),
    ("Leviticus", "LEV", 27, 859),
    ("Numbers", "NUM", 36, 1288),
    ("Deuteronomy", "DEU", 34, 959),
    ("Joshua", "JOS", 24, 659),
    ("Judges", "JDG", 21, 618),
    ("Ruth", "RUT", 4, 85),
    ("1 Samuel", "1SA", 31, 810),
    ("2 Samuel", "2SA", 24, 695),
    ("1 Kings", "1KI", 22, 816),
    ("2 Kings", "2KI", 25, 719),
    ("1 Chronicles", "1CH", 29, 942),
    ("2 Chronicles", "2CH", 36, 822),
    ("Ezra", "EZR", 10, 280),
    ("Nehemiah", "NEH", 13, 406),
    ("Esther", "EST", 10, 167),
]

def fetch_api_verse_counts(api_code, max_chapter):
    """Fetch verse counts for all chapters in a book."""
    url = f"https://bible.helloao.org/api/BSB/{api_code}/1.json"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        total_verses_api = data["book"]["totalNumberOfVerses"]
        return total_verses_api
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

def get_file_verse_counts():
    """Extract verse counts per chapter from file using streaming."""
    with open("bsb-edited.md", "r") as f:
        content = f.read()
    
    lines = content.split('\n')
    
    book_chapters = {}  # book_name -> {chapter_num: verse_count}
    current_book = None
    current_chapter = None
    current_max_verse = 0
    
    for line in lines:
        # New book
        m = re.match(r'^## ([^\s].+)', line)
        if m:
            if current_book and current_chapter:
                book_chapters[current_book][current_chapter] = current_max_verse
            current_book = m.group(1).strip()
            current_chapter = None
            current_max_verse = 0
            book_chapters[current_book] = {}
            continue
        
        # New chapter
        m = re.match(r'^### Chapter (\d+)', line)
        if m:
            if current_chapter is not None:
                book_chapters[current_book][current_chapter] = current_max_verse
            current_chapter = int(m.group(1))
            current_max_verse = 0
            continue
        
        # Verse
        m = re.findall(r'\*\*v(\d+)\*\*', line)
        for v in m:
            v_num = int(v)
            if v_num > current_max_verse:
                current_max_verse = v_num
    
    # Last chapter
    if current_book and current_chapter:
        book_chapters[current_book][current_chapter] = current_max_verse
    
    return book_chapters

def main():
    print("Extracting verse counts from file...")
    file_counts = get_file_verse_counts()
    
    discrepancies = []
    
    for book_name, api_code, expected_chapters, expected_total in BOOKS_INFO:
        print(f"\n{'='*50}")
        print(f"CHECKING: {book_name} ({api_code})")
        print(f"{'='*50}")
        
        if book_name not in file_counts:
            print(f"  ERROR: Book not found in file!")
            discrepancies.append(f"{book_name}: BOOK NOT FOUND IN FILE")
            continue
        
        file_chapters = file_counts[book_name]
        file_total = sum(file_chapters.values())
        
        # Get API total
        api_total = fetch_api_verse_counts(api_code, expected_chapters)
        
        print(f"  File chapters: {len(file_chapters)}, verses: {file_total}")
        print(f"  API total verses: {api_total}")
        print(f"  Expected: {expected_chapters} chapters, {expected_total} verses")
        
        # Check chapter count
        if len(file_chapters) != expected_chapters:
            discrepancies.append(f"{book_name}: Chapter count mismatch - file={len(file_chapters)}, expected={expected_chapters}")
            print(f"  ⚠️ Chapter count mismatch!")
        
        # Check total verse count
        if api_total is not None:
            diff = file_total - api_total
            if diff != 0:
                print(f"  ⚠️ Total verse diff vs API: {diff:+d}")
                discrepancies.append(f"{book_name}: Verse total mismatch - file={file_total}, api={api_total}, diff={diff:+d}")
            else:
                print(f"  ✅ Total verses match API")
        
        # Check specific chapters (spot check first 3, last 1, and any with issues)
        chapters_to_check = []
        if expected_chapters >= 1:
            chapters_to_check.extend([1, 2, expected_chapters])
        if expected_chapters > 3:
            chapters_to_check.append(expected_chapters // 2)
        
        for ch in set(chapters_to_check):
            if ch in file_chapters:
                print(f"  Chapter {ch}: file_max={file_chapters[ch]}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total discrepancies: {len(discrepancies)}")
    for d in discrepancies:
        print(f"  - {d}")
    
    # Write report
    report = []
    report.append("# BSB Verification Report: Torah + History (17 Books)")
    report.append("")
    report.append("**Generated:** 2026-04-08 03:10 EDT")
    report.append("**Source:** `bsb-edited.md` vs `helloao.org` API (Berean Standard Bible)")
    report.append("")
    report.append("## Methodology")
    report.append("")
    report.append("1. Parsed `bsb-edited.md` to count **max verse number** per chapter (using `**v{N}**` pattern)")
    report.append("2. Fetched total verse counts from `https://bible.helloao.org/api/BSB/{code}/1.json`")
    report.append("3. Compared total verse counts per book and spot-checked chapter max verses")
    report.append("")
    report.append("## Expected Differences")
    report.append("")
    report.append("The original BSB was missing two verses that were added to `bsb-edited.md`:")
    report.append("- **2 Chronicles 1:18** — \"And the greatness of Solomon's wealth and wisdom surpassed all the kings of the earth.\"")
    report.append("- **2 Chronicles 13:23** — \"And Abijah rested with his fathers and was buried in the City of David, and his son Asa reigned in his place.\"")
    report.append("")
    report.append("This means the file should have **2 more verses** than the API reports.")
    report.append("")
    report.append("## Results")
    report.append("")
    report.append(f"| Book | File Verses | API Verses | Difference | Status |")
    report.append("|------|-------------|------------|-----------|--------|")
    
    total_file = 0
    total_api = 0
    for book_name, api_code, expected_chapters, expected_total in BOOKS_INFO:
        if book_name in file_counts:
            fv = sum(file_counts[book_name].values())
            total_file += fv
        else:
            fv = "N/A"
        api_t = fetch_api_verse_counts(api_code, expected_chapters)
        if api_t:
            total_api += api_t
            diff = fv - api_t if isinstance(fv, int) else "?"
            status = "✅" if (isinstance(diff, int) and diff == (2 if book_name == "2 Chronicles" else 0)) else "⚠️"
            report.append(f"| {book_name} | {fv} | {api_t} | {diff:+d if isinstance(diff, int) else diff} | {status} |")
        else:
            report.append(f"| {book_name} | {fv} | ERROR | ? | ⚠️ |")
    
    report.append(f"| **TOTAL** | **{total_file}** | **{total_api}** | **{total_file - total_api:+d}** | {'✅' if total_file - total_api == 2 else '⚠️'} |")
    report.append("")
    report.append("## Expected vs Actual Difference")
    report.append("")
    report.append(f"- Expected difference: **+2** (the 2 added verses)")
    report.append(f"- Actual difference: **{total_file - total_api:+d}**")
    report.append("")
    
    if total_file - total_api == 2:
        report.append("✅ **PASS** — Difference matches expected (only the 2 added verses)")
    elif total_file - total_api == 0:
        report.append("⚠️ **NOTE** — No difference detected. This could mean the API also has these verses,")
        report.append("   or the API's total verse count is computed differently.")
    else:
        report.append(f"⚠️ **CHECK NEEDED** — Unexpected difference of {total_file - total_api} verses.")
        report.append("")
        report.append("### Discrepancies")
        for d in discrepancies:
            report.append(f"- {d}")
    
    report_text = "\n".join(report)
    print(report_text)
    
    with open("/Users/silas/.openclaw/workspace/bibles/bsb/verification_torah_history.md", "w") as f:
        f.write(report_text)
    print(f"\nReport written.")

if __name__ == "__main__":
    main()
