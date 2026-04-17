# BSB Comprehensive Verification Plan

## Agent Assignments

### Agent 1: Torah + History (17 books)
Books: Genesis, Exodus, Leviticus, Numbers, Deuteronomy, Joshua, Judges, Ruth, 1 Samuel, 2 Samuel, 1 Kings, 2 Kings, 1 Chronicles, 2 Chronicles, Ezra, Nehemiah, Esther
Model: minimax/MiniMax-M2.7

### Agent 2: Wisdom + Major Prophets (10 books)  
Books: Job, Psalms, Proverbs, Ecclesiastes, Song of Songs, Isaiah, Jeremiah, Lamentations, Ezekiel, Daniel
Model: zai/glm-5

### Agent 3: Minor Prophets (12 books)
Books: Hosea, Joel, Amos, Obadiah, Jonah, Micah, Nahum, Habakkuk, Zephaniah, Haggai, Zechariah, Malachi
Model: minimax/MiniMax-M2.7

### Agent 4: Gospels + Acts (5 books)
Books: Matthew, Mark, Luke, John, Acts
Model: zai/glm-5

### Agent 5: Pauline Epistles (13 books)
Books: Romans, 1 Corinthians, 2 Corinthians, Galatians, Ephesians, Philippians, Colossians, 1 Thessalonians, 2 Thessalonians, 1 Timothy, 2 Timothy, Titus, Philemon
Model: minimax/MiniMax-M2.7

### Agent 6: General Epistles + Revelation (9 books)
Books: Hebrews, James, 1 Peter, 2 Peter, 1 John, 2 John, 3 John, Jude, Revelation
Model: zai/glm-5

## Verification Method
1. For each book, query helloao.org API for chapter/verse counts
2. Compare against bsb-edited.md
3. Flag any discrepancies
4. Spot-check verse text for accuracy
5. Report findings

## API Endpoints
- https://bible.helloao.org/api/BSB/books.json - List all books
- https://bible.helloao.org/api/BSB/{book_code}/{chapter}.json - Get chapter verses

## Book Codes
GEN, EXO, LEV, NUM, DEU, JOS, JDG, RUT, 1SA, 2SA, 1KI, 2KI, 1CH, 2CH, EZR, NEH, EST, JOB, PSA, PRO, ECC, SNG, ISA, JER, LAM, EZK, DAN, HOS, JOL, AMO, OBA, JON, MIC, NAM, HAB, ZEP, HAG, ZEC, MAL, MAT, MRK, LUK, JHN, ACT, ROM, 1CO, 2CO, GAL, EPH, PHP, COL, 1TH, 2TH, 1TI, 2TI, TIT, PHM, HEB, JAS, 1PE, 2PE, 1JN, 2JN, 3JN, JUD, REV
