#!/usr/bin/env python3
"""
Verse-by-verse comparison: esv_deduped.md vs esv_pdf_full.txt
Uses PDF as ground truth, checks markdown accuracy.
"""

import re, sys

MD_PATH = "/Users/silas/.openclaw/workspace/bibles/esv/esv_deduped.md"
PDF_PATH = "/Users/silas/Downloads/esv_pdf_full.txt"

STOPWORDS = {'of', 'and', 'the', 'to', 'in', 'for', 'on', 'at', 'by'}


def is_section_header(s):
    """Heuristic: is this line a section/chapter header (not verse text)?"""
    s = s.strip()
    if not s or len(s) < 5:
        return False
    # Must start with "The " followed by title-case words
    if not re.match(r'^The [A-Z][a-z]', s):
        return False
    if len(s) > 45:  # Headers are short
        return False
    if s.endswith('.') or s.endswith(',') or s.endswith(':'):
        return False
    # All non-stopword words must be title case
    words = s.split()
    non_stop = [w for w in words if w.lower() not in STOPWORDS]
    for w in non_stop:
        if w[0].islower():
            return False
    return True


def get_md_chapters(book_name):
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    book_re = re.compile(rf'^## {re.escape(book_name)}$')
    ch_re = re.compile(r'^### Chapter (\d+)$')
    book_start = next((i for i, l in enumerate(lines) if book_re.match(l.strip())), None)
    if book_start is None:
        return []
    chapters = []
    for i in range(book_start + 1, len(lines)):
        s = lines[i].strip()
        m = ch_re.match(s)
        if m:
            if chapters:
                chapters[-1][2] = i
            chapters.append([int(m.group(1)), i, len(lines)])
        elif s.startswith('## ') and i > book_start:
            if chapters:
                chapters[-1][2] = i
            break
    if chapters:
        chapters[-1][2] = len(lines)
    return [(c[0], c[1], c[2]) for c in chapters]


def get_md_verses(lines, start, end):
    chunk = ''.join(lines[start:end])
    verses = {}
    for m in re.finditer(r'\*\*v(\d+)\*\*\s*(.+?)(?=\*\*v\d+\*\*|$)', chunk, re.DOTALL):
        verses[int(m.group(1))] = re.sub(r'\s+', ' ', m.group(2).strip())
    return verses


def get_pdf_book_lines(book_name):
    with open(PDF_PATH, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.read().split('\n')

    book_upper = book_name.upper()
    all_books = ['GENESIS', 'EXODUS', 'LEVITICUS', 'NUMBERS', 'DEUTERONOMY',
                  'JOSHUA', 'JUDGES', 'RUTH', '1 SAMUEL', '2 SAMUEL', '1 KINGS',
                  '2 KINGS', '1 CHRONICLES', '2 CHRONICLES', 'EZRA', 'NEHEMIAH',
                  'ESTHER', 'JOB', 'PSALMS', 'PROVERBIES', 'ECCLESIASTES',
                  'SONG OF SOLOMON', 'ISAIAH', 'JEREMIAH', 'LAMENTATIONS',
                  'EZEKIEL', 'DANIEL', 'HOSEA', 'JOEL', 'AMOS', 'OBADIAH',
                  'JONAH', 'MICAH', 'NAHUM', 'HABAKKUK', 'ZEPHANIAH', 'HAGGAI',
                  'ZECHARIAH', 'MALACHI', 'MATTHEW', 'MARK', 'LUKE', 'JOHN',
                  'ACTS', 'ROMANS', '1 CORINTHIANS', '2 CORINTHIANS', 'GALATIANS',
                  'EPHESIANS', 'PHILIPPIANS', 'COLOSSIANS', '1 THESSALONIANS',
                  '2 THESSALONIANS', '1 TIMOTHY', '2 TIMOTHY', 'TITUS',
                  'PHILEMON', 'HEBREWS', 'JAMES', '1 PETER', '2 PETER',
                  '1 JOHN', '2 JOHN', '3 JOHN', 'JUDE', 'REVELATION']

    book_pos = None
    for i, line in enumerate(lines):
        if line.strip() == book_upper:
            for j in range(i + 1, min(i + 10, len(lines))):
                s = lines[j].strip()
                if re.match(r'^Chapter \d+$', s):
                    book_pos = i
                    break
            if book_pos:
                break

    if book_pos is None:
        return None, None, None

    book_end = None
    book_idx = all_books.index(book_upper) if book_upper in all_books else -1
    if book_idx >= 0 and book_idx + 1 < len(all_books):
        next_book = all_books[book_idx + 1]
        for i in range(book_pos + 1, len(lines)):
            if lines[i].strip() == next_book:
                book_end = i
                break

    if book_end is None:
        book_end = len(lines)

    toc_end = book_pos
    for i in range(book_pos + 1, min(book_pos + 300, len(lines))):
        s = lines[i].strip()
        if not re.match(r'^Chapter \d+$', s) and not s.startswith('---'):
            toc_end = i
            break

    content_start = toc_end
    for i in range(toc_end, min(toc_end + 30, len(lines))):
        s = lines[i].strip()
        if s and not s.startswith('---'):
            content_start = i
            break

    return content_start, book_end, lines


def find_chapter_bounds(lines, content_start, book_end, chapter):
    """Find the (start, end) line indices for a chapter in the PDF."""
    header_pos = None
    for i in range(content_start, book_end):
        s = lines[i].strip()
        if is_section_header(s):
            header_pos = i
            break

    if header_pos is None:
        return None, None

    next_header_pos = book_end
    for i in range(header_pos + 1, book_end):
        if is_section_header(lines[i].strip()):
            next_header_pos = i
            break

    return header_pos, next_header_pos


def extract_pdf_verses(lines, start, end):
    """Extract verses from PDF lines[start:end]."""
    verses = {}
    num_pos = [(i, int(lines[i].strip())) for i in range(start, end)
               if re.match(r'^\d+$', lines[i].strip())]

    if not num_pos:
        return verses

    # The chapter marker is the first number.
    # If it has a ':{number}' marker on the next line, that number IS verse 1.
    chapter_marker_line, chapter_num = num_pos[0]

    # Check if chapter marker has ':{num}' on the next line (meaning chapter_num = v1)
    has_v1_marker = any(lines[j].strip() == f":{chapter_num}"
                         for j in range(chapter_marker_line, min(chapter_marker_line + 3, end)))

    if has_v1_marker:
        # Chapter marker IS v1 - extract v1 starting from chapter_marker_line
        text_start = chapter_marker_line + 2  # skip chapter marker and ':N' line
        parts = []
        for j in range(text_start, min(text_start + 30, end)):
            s = lines[j].strip()
            if not s or re.match(r'^\d+$', s) or re.match(r'^\[\d+\]$', s):
                break
            if re.match(r'^--- PAGE \d+ ---$', s):
                continue  # skip page markers
            parts.append(s)
        if parts:
            verse_text = re.sub(r'\s+', ' ', ' '.join(parts)).strip()
            if verse_text:
                verses[chapter_num] = verse_text

        # Rest of verses from num_pos[1:]
        verse_markers = num_pos[1:]
    else:
        # Standard case: first number is chapter marker only, verses start at num_pos[1:]
        verse_markers = num_pos[1:]

    # Process remaining verse markers
    for idx, (v_line_idx, v_num) in enumerate(verse_markers):
        # Skip if same as chapter marker (already processed)
        if v_line_idx == chapter_marker_line:
            continue

        has_colon = any(lines[j].strip() == f":{v_num}"
                        for j in range(v_line_idx, min(v_line_idx + 3, end)))
        text_start = v_line_idx + 2 if has_colon else v_line_idx + 1

        parts = []
        for j in range(text_start, min(text_start + 30, end)):
            s = lines[j].strip()
            if not s or re.match(r'^\d+$', s) or re.match(r'^\[\d+\]$', s):
                break
            if re.match(r'^--- PAGE \d+ ---$', s):
                continue
            parts.append(s)

        if parts:
            verse_text = re.sub(r'\s+', ' ', ' '.join(parts)).strip()
            if verse_text:
                verses[v_num] = verse_text

    return verses


def norm(s):
    if not isinstance(s, str):
        return ""
    s = s.strip()
    s = s.replace('\u2019', "'").replace('\u2018', "'")
    s = s.replace('\u201c', '"').replace('\u201d', '"')
    s = s.replace('\u2014', ' ').replace('\u2013', ' ')
    s = re.sub(r'\s+', ' ', s)
    return s


def compare_book(book_name, max_chapter=None):
    print(f"\n{'='*60}")
    print(f"  COMPARING: {book_name}")
    print(f"{'='*60}")

    md_chapters = get_md_chapters(book_name)
    if not md_chapters:
        print(f"Book '{book_name}' not found!")
        return

    md_lines = open(MD_PATH, 'r', encoding='utf-8').readlines()
    content_start, book_end, pdf_lines = get_pdf_book_lines(book_name)

    if content_start is None:
        print("Could not locate book in PDF!")
        return

    print(f"PDF: line {content_start} to {book_end}")

    total_m = total_mm = total_md_miss = total_pdf_miss = 0

    for ch_num, ch_start, ch_end in md_chapters:
        if max_chapter and ch_num > max_chapter:
            break

        md_verses = get_md_verses(md_lines, ch_start, ch_end)
        if not md_verses:
            continue

        hdr_start, hdr_end = find_chapter_bounds(pdf_lines, content_start, book_end, ch_num)
        if hdr_start is None:
            print(f"\n  Chapter {ch_num}: ⚠️  Could not locate PDF section")
            continue

        pdf_verses = extract_pdf_verses(pdf_lines, hdr_start, hdr_end)

        hdr_text = pdf_lines[hdr_start].strip() if hdr_start < len(pdf_lines) else '?'

        print(f"\n  {book_name} Chapter {ch_num}  [{hdr_text[:40]}]  (MD:{len(md_verses)} | PDF:{len(pdf_verses)})")

        all_v = sorted(set(list(md_verses.keys()) + list(pdf_verses.keys())))
        ch_m = ch_mm = 0

        for v_num in all_v:
            md_v = md_verses.get(v_num)
            pdf_v = pdf_verses.get(v_num)

            if md_v is None:
                print(f"  v{v_num}: ⚠️  MISSING in markdown")
                total_md_miss += 1
            elif pdf_v is None:
                print(f"  v{v_num}: ⚠️  MISSING in PDF")
                total_pdf_miss += 1
            else:
                if norm(md_v) == norm(pdf_v):
                    print(f"  v{v_num}: ✅")
                    ch_m += 1
                else:
                    print(f"  v{v_num}: ❌ MISMATCH")
                    mw = norm(md_v).split()
                    pw = norm(pdf_v).split()
                    for k in range(min(len(mw), len(pw))):
                        if mw[k] != pw[k]:
                            print(f"       diff@{k}: '{mw[k]}' | '{pw[k]}'")
                            break
                    ch_mm += 1

        total_m += ch_m
        total_mm += ch_mm
        print(f"  → {ch_m} ✅  {ch_mm} ❌")

    print(f"\n{'='*40}")
    print(f"  FINAL: {total_m} ✅ | {total_mm} ❌ | {total_md_miss} md-only | {total_pdf_miss} pdf-only")
    print(f"{'='*40}")


if __name__ == "__main__":
    book = sys.argv[1] if len(sys.argv) > 1 else "Genesis"
    max_ch = int(sys.argv[2]) if len(sys.argv) > 2 else None
    compare_book(book, max_ch)
