# ESV Bible Systematic Fix Plan

## Overview
Systematically verify and fix every book of the Bible using subagents with GLM 5.1 (via Venice) and the ESV API.

## Editorial Omissions Reference
See `ESV_EDITORIAL_OMISSIONS.md` - 17 verses intentionally omitted by ESV (should NOT be added back).

## Rate Limiting
ESV API: 1 second delay between requests, exponential backoff on 429 errors.

## Task Batches

### BATCH 1: Pentateuch (Torah)
| Book | Chapters | Status | Notes |
|------|----------|--------|-------|
| Genesis | 50 | 🔴 NEEDS FIX | Missing verses throughout |
| Exodus | 40 | 🔴 NEEDS FIX | Duplicate ch 32-33, many missing verses |
| Leviticus | 27 | 🟡 CHECK | Needs verification |
| Numbers | 36 | ✅ DONE | Already re-fetched from API |
| Deuteronomy | 34 | 🟡 CHECK | Some unclassified fragments |

### BATCH 2: Historical Books (Part 1)
| Book | Chapters | Status | Notes |
|------|----------|--------|-------|
| Joshua | 24 | 🟡 CHECK | Verify after cleanup |
| Judges | 21 | 🔴 NEEDS FIX | Unclassified fragments |
| Ruth | 4 | 🟢 QUICK | Small book |
| 1 Samuel | 31 | 🟡 CHECK | Verify |
| 2 Samuel | 24 | 🟡 CHECK | Verify |

### BATCH 3: Historical Books (Part 2)
| Book | Chapters | Status | Notes |
|------|----------|--------|-------|
| 1 Kings | 22 | 🔴 NEEDS FIX | Many unclassified fragments |
| 2 Kings | 25 | 🔴 NEEDS FIX | Unclassified fragments |
| 1 Chronicles | 29 | 🟡 CHECK | Verify |
| 2 Chronicles | 36 | 🔴 NEEDS FIX | Commentary fragments |
| Ezra | 10 | 🟢 QUICK | Small book |
| Nehemiah | 13 | 🟢 QUICK | Small book |
| Esther | 10 | 🟡 CHECK | Commentary fragments noted |

### BATCH 4: Wisdom & Poetry
| Book | Chapters | Status | Notes |
|------|----------|--------|-------|
| Job | 42 | 🟡 CHECK | Needs verification |
| Psalms (1-75) | 75 | 🟡 CHECK | Split into two parts |
| Psalms (76-150) | 75 | 🟡 CHECK | Split into two parts |
| Proverbs | 31 | 🟡 CHECK | Verify |
| Ecclesiastes | 12 | 🟢 QUICK | Small book |
| Song of Solomon | 8 | 🟢 QUICK | Small book |

### BATCH 5: Major Prophets (Part 1)
| Book | Chapters | Status | Notes |
|------|----------|--------|-------|
| Isaiah (1-33) | 33 | 🟡 CHECK | Split long book |
| Isaiah (34-66) | 33 | 🟡 CHECK | Split long book |
| Jeremiah (1-26) | 26 | 🟡 CHECK | Split long book |
| Jeremiah (27-52) | 26 | 🟡 CHECK | Split long book |

### BATCH 6: Major Prophets (Part 2) & Daniel
| Book | Chapters | Status | Notes |
|------|----------|--------|-------|
| Lamentations | 5 | 🟢 QUICK | Small book |
| Ezekiel (1-24) | 24 | 🟡 CHECK | Split long book |
| Ezekiel (25-48) | 24 | 🟡 CHECK | Split long book |
| Daniel | 12 | 🟡 CHECK | Commentary/date fragments noted |

### BATCH 7: Minor Prophets (Combined)
| Book | Chapters | Status | Notes |
|------|----------|--------|-------|
| Hosea | 14 | 🟢 QUICK | |
| Joel | 3 | 🟢 QUICK | |
| Amos | 9 | 🟢 QUICK | |
| Obadiah | 1 | 🟢 QUICK | Fragment noted |
| Jonah | 4 | 🟢 QUICK | |
| Micah | 7 | 🟢 QUICK | |
| Nahum | 3 | 🟢 QUICK | |
| Habakkuk | 3 | 🟢 QUICK | |
| Zephaniah | 3 | 🟢 QUICK | |
| Haggai | 2 | 🟢 QUICK | |
| Zechariah | 14 | 🟢 QUICK | |
| Malachi | 4 | 🟢 QUICK | |

### BATCH 8: Gospels
| Book | Chapters | Status | Notes |
|------|----------|--------|-------|
| Matthew | 28 | 🟡 CHECK | Check editorial omissions |
| Mark | 16 | 🟡 CHECK | Check editorial omissions |
| Luke | 24 | 🟡 CHECK | Check editorial omissions |
| John | 21 | 🟡 CHECK | Check editorial omissions |

### BATCH 9: Acts & Pauline Epistles
| Book | Chapters | Status | Notes |
|------|----------|--------|-------|
| Acts | 28 | 🟡 CHECK | Check editorial omissions |
| Romans | 16 | 🟡 CHECK | Check editorial omissions |
| 1 Corinthians | 16 | 🟡 CHECK | |
| 2 Corinthians | 13 | 🟡 CHECK | |
| Galatians | 6 | 🟢 QUICK | |
| Ephesians | 6 | 🟢 QUICK | |
| Philippians | 4 | 🟢 QUICK | |
| Colossians | 4 | 🟢 QUICK | |

### BATCH 10: More Pauline Epistles
| Book | Chapters | Status | Notes |
|------|----------|--------|-------|
| 1 Thessalonians | 5 | 🟢 QUICK | |
| 2 Thessalonians | 3 | 🟢 QUICK | |
| 1 Timothy | 6 | 🟢 QUICK | |
| 2 Timothy | 4 | 🟢 QUICK | |
| Titus | 3 | 🟢 QUICK | |
| Philemon | 1 | 🟢 QUICK | |
| Hebrews | 13 | 🟡 CHECK | |

### BATCH 11: General Epistles & Revelation
| Book | Chapters | Status | Notes |
|------|----------|--------|-------|
| James | 5 | 🟢 QUICK | |
| 1 Peter | 5 | 🟢 QUICK | |
| 2 Peter | 3 | 🟢 QUICK | |
| 1 John | 5 | 🟡 CHECK | Editorial omission 5:7 |
| 2 John | 1 | 🟢 QUICK | |
| 3 John | 1 | 🟢 QUICK | |
| Jude | 1 | 🟢 QUICK | |
| Revelation | 22 | 🟡 CHECK | |

## Subagent Task Template

Each subagent should:
1. Read the current book from esv.md
2. Use the ESV API to fetch the book (or chapters)
3. Compare verse-by-verse
4. Check for missing verses (that are NOT in editorial omissions list)
5. Check for duplicate chapters
6. Check for section headers embedded in verses
7. Fix any issues found
8. Report: verses fixed, issues found, time taken

## API Key
ESV API Key: `9480e52697feb72baa1453cbd76b9d976ed1c5e3`
Rate limit: 1 sec between requests

## Execution Order
Start with BATCH 1 (highest priority - most errors detected), then proceed numerically.
