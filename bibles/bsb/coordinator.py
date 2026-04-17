#!/usr/bin/env python3
"""
BSB Bible Correction Coordinator
Spawns subagents to correct each book and combines results.
"""

import subprocess
import json
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

BOOKS = [
    # Old Testament
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
    "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra",
    "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
    "Ecclesiastes", "Song of Songs", "Isaiah", "Jeremiah", "Lamentations",
    "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk",
    "Zephaniah", "Haggai", "Zechariah", "Malachi",
    # New Testament
    "Matthew", "Mark", "Luke", "John", "Acts",
    "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians", "1 Timothy",
    "2 Timothy", "Titus", "Philemon", "Hebrews", "James",
    "1 Peter", "2 Peter", "1 John", "2 John", "3 John",
    "Jude", "Revelation"
]

# Books with known critical issues (priority processing)
PRIORITY_BOOKS = [
    "Genesis",      # Missing 37:37-41, extra verses in 29, 32
    "1 Samuel",     # Missing 21:16, 24:23
    "2 Chronicles", # Missing 1:18, 13:23, extra 2:18
    "Nehemiah",     # Missing 3:33-38
    "Isaiah",       # Missing 8:23
    "Micah"         # Missing 4:14
]

def spawn_book_agent(book_name, model="minimax/MiniMax-M2.7"):
    """Spawn a subagent to correct one book."""
    
    # Map book names for file naming
    safe_name = book_name.lower().replace(" ", "_")
    output_file = f"/Users/silas/.openclaw/workspace/bibles/bsb/bsb-edited-{safe_name}.md"
    
    task = f"""You are correcting the book "{book_name}" from the Berean Standard Bible (BSB).

SOURCE FILE: /Users/silas/.openclaw/workspace/bibles/bsb/bsb.md
OUTPUT FILE: {output_file}

YOUR TASK:
1. Read the entire book "{book_name}" from the source file
2. Review EVERY chapter and verse for errors
3. Fix ALL issues you find:
   - Missing verses (compare against canonical verse counts)
   - Duplicate verse markers
   - Invalid chapter/verse numbers
   - Curly quotes → convert to straight ASCII quotes
   - Ensure proper formatting: ## Book, ### Chapter N, #### Section Headers, **vN** verse text
   - Keep footnotes in proper [^N]: format at chapter end
   - Keep section headers as #### Header (not embedded in verses)

4. Write the COMPLETE corrected book to the output file

VERIFICATION STEPS:
- Count verses in each chapter against canonical counts
- Ensure no verse numbers are duplicated
- Ensure no verses are missing
- Verify all quotes are straight ASCII

Write ONLY the corrected book content to the output file. Start with "## {book_name}" and include all chapters.

DO NOT modify the original bsb.md file.
"""
    
    # Spawn the subagent
    agent_cmd = [
        "sessions_spawn",
        "--runtime", "subagent",
        "--mode", "run",
        "--model", model,
        "--task", task,
        "--label", f"bsb-correct-{safe_name}",
        "--runTimeoutSeconds", "1800"  # 30 min per book
    ]
    
    try:
        result = subprocess.run(agent_cmd, capture_output=True, text=True, timeout=5)
        return {"book": book_name, "status": "spawned", "output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"book": book_name, "status": "error", "error": str(e)}

def check_book_completion(book_name):
    """Check if a book's correction file exists and is complete."""
    safe_name = book_name.lower().replace(" ", "_")
    output_file = f"/Users/silas/.openclaw/workspace/bibles/bsb/bsb-edited-{safe_name}.md"
    
    if not os.path.exists(output_file):
        return False, "File not found"
    
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Basic checks
    has_book_header = f"## {book_name}" in content
    chapter_count = content.count("### Chapter")
    verse_count = content.count("**v")
    
    return has_book_header, f"{chapter_count} chapters, {verse_count} verses"

def combine_books():
    """Combine all corrected book files into bsb-edited.md."""
    output_path = "/Users/silas/.openclaw/workspace/bibles/bsb/bsb-edited.md"
    
    header = """---
title: Berean Standard Bible (Corrected)
description: The Berean Standard Bible (BSB) - Corrected Edition
license: CC BY-SA 4.0
license_url: https://berean.bible/licensing.htm
source: https://berean.bible/
---

"""
    
    with open(output_path, 'w', encoding='utf-8') as outfile:
        outfile.write(header)
        
        for book in BOOKS:
            safe_name = book.lower().replace(" ", "_")
            book_file = f"/Users/silas/.openclaw/workspace/bibles/bsb/bsb-edited-{safe_name}.md"
            
            if os.path.exists(book_file):
                with open(book_file, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
                    outfile.write("\n\n")
            else:
                outfile.write(f"\n\n## {book}\n\n[BOOK NOT YET PROCESSED]\n\n")
    
    return output_path

if __name__ == "__main__":
    print("BSB Bible Correction Coordinator")
    print("=" * 50)
    print(f"Total books to process: {len(BOOKS)}")
    print(f"Priority books (known issues): {', '.join(PRIORITY_BOOKS)}")
    print()
    
    # Process priority books first
    print("Processing priority books...")
    for book in PRIORITY_BOOKS:
        print(f"  Spawning agent for {book}...")
        result = spawn_book_agent(book)
        print(f"    Status: {result['status']}")
        time.sleep(1)  # Rate limiting
    
    print("\nPriority books spawned. Check status with: subagents list")
