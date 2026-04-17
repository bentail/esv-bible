#!/usr/bin/env python3
"""
Combine all corrected BSB book files into final bsb-edited.md
"""

import re

# Book order
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

OUTPUT_PATH = "/Users/silas/.openclaw/workspace/bibles/bsb/bsb-edited.md"

def get_book_filename(book_name):
    """Convert book name to filename format."""
    safe = book_name.lower().replace(" ", "_")
    return f"/Users/silas/.openclaw/workspace/bibles/bsb/bsb-edited-{safe}.md"

def combine_books():
    print("BSB Final Combination Script")
    print("=" * 50)
    
    # Start with header
    output_lines = [
        "---",
        "title: Berean Standard Bible (Corrected)",
        "description: The Berean Standard Bible (BSB) - Corrected Edition with verified verse counts and straight quotes",
        "license: CC BY-SA 4.0",
        "license_url: https://berean.bible/licensing.htm",
        "source: https://berean.bible/",
        "---",
        ""
    ]
    
    books_used = []
    books_from_full = []
    
    for book in BOOKS:
        # Try individual book file first
        book_file = get_book_filename(book)
        try:
            with open(book_file, 'r', encoding='utf-8') as f:
                content = f.read()
            # Extract just the book content (remove any YAML header)
            content = re.sub(r'^---.*?---\n+', '', content, flags=re.DOTALL)
            output_lines.append(content)
            books_used.append(f"{book} (individual file)")
        except FileNotFoundError:
            # Fall back to full bible file
            full_file = "/Users/silas/.openclaw/workspace/bibles/bsb/bsb-edited.md"
            try:
                with open(full_file, 'r', encoding='utf-8') as f:
                    full_content = f.read()
                # Find this book in the full content
                pattern = rf'(## {re.escape(book)}.*?)(?=\n## [^#]|\Z)'
                match = re.search(pattern, full_content, re.DOTALL)
                if match:
                    output_lines.append(match.group(1).strip())
                    books_from_full.append(book)
                else:
                    print(f"   Warning: Could not find {book} in full file")
            except FileNotFoundError:
                print(f"   ERROR: Could not find {book} anywhere")
    
    # Write final output
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(output_lines))
    
    print(f"\n✓ Combined file created: {OUTPUT_PATH}")
    print(f"\nBooks from individual files: {len(books_used)}")
    for b in books_used[:5]:
        print(f"  - {b}")
    if len(books_used) > 5:
        print(f"  ... and {len(books_used) - 5} more")
    
    print(f"\nBooks from full file: {len(books_from_full)}")
    if books_from_full:
        print(f"  {', '.join(books_from_full[:10])}")
        if len(books_from_full) > 10:
            print(f"  ... and {len(books_from_full) - 10} more")

if __name__ == "__main__":
    combine_books()