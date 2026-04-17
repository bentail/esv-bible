#!/usr/bin/env python3
"""
BSB Complete Rebuild Script
Creates a proper bsb-edited.md from source and corrected individual books.
"""

import re

BSB_SOURCE = "/Users/silas/.openclaw/workspace/bibles/bsb/bsb.md"
BSB_EDITED = "/Users/silas/.openclaw/workspace/bibles/bsb/bsb-edited.md"

# Books in order
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

def get_book_from_corrected_files(book_name):
    """Try to get book from corrected individual files first."""
    safe = book_name.lower().replace(" ", "_")
    filepath = f"/Users/silas/.openclaw/workspace/bibles/bsb/bsb-edited-{safe}.md"
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None

def get_book_from_source(book_name, source_content):
    """Extract book from source file."""
    # Find book content (from ## Book to next ## Book or end)
    pattern = rf'(## {re.escape(book_name)}\n.*?)(?=\n## [^#]|\Z)'
    match = re.search(pattern, source_content, re.DOTALL)
    return match.group(1) if match else None

def rebuild_bsb():
    print("BSB Complete Rebuild")
    print("=" * 50)
    
    # Read source file
    print("\n1. Reading source file...")
    with open(BSB_SOURCE, 'r', encoding='utf-8') as f:
        source = f.read()
    print(f"   Source size: {len(source):,} characters")
    
    # Start building output
    output_lines = [
        "---",
        "title: Berean Standard Bible (Corrected)",
        "description: The Berean Standard Bible (BSB) - Corrected Edition with verified verse counts, straight quotes, and all 66 books",
        "license: CC BY-SA 4.0",
        "license_url: https://berean.bible/licensing.htm",
        "source: https://berean.bible/",
        "---",
        ""
    ]
    
    books_found = []
    books_from_corrected = []
    books_from_source = []
    
    for book in BOOKS:
        # Try corrected files first
        corrected_content = get_book_from_corrected_files(book)
        if corrected_content:
            # Remove any YAML headers
            corrected_content = re.sub(r'^---.*?---\n+', '', corrected_content, flags=re.DOTALL)
            output_lines.append(corrected_content.strip())
            output_lines.append("")
            books_found.append(book)
            books_from_corrected.append(book)
            print(f"   {book}: from corrected file")
            continue
        
        # Fall back to source
        source_content = get_book_from_source(book, source)
        if source_content:
            output_lines.append(source_content.strip())
            output_lines.append("")
            books_found.append(book)
            books_from_source.append(book)
            print(f"   {book}: from source file")
        else:
            print(f"   ⚠ {book}: NOT FOUND")
    
    # Write output
    print(f"\n2. Writing final file...")
    with open(BSB_EDITED, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    # Stats
    final_content = '\n'.join(output_lines)
    verse_count = len(re.findall(r'\*\*v\d+\*\*', final_content))
    
    print(f"\n✓ Rebuild complete!")
    print(f"   Total books: {len(books_found)}/66")
    print(f"   From corrected files: {len(books_from_corrected)}")
    print(f"   From source: {len(books_from_source)}")
    print(f"   Total verses: {verse_count:,}")
    print(f"   File size: {len(final_content):,} characters")
    print(f"\n   Output: {BSB_EDITED}")

if __name__ == "__main__":
    rebuild_bsb()
