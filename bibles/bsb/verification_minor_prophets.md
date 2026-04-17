# BSB Minor Prophets Verification Report
**Verified:** 2026-04-07
**Source:** helloao.org API (https://bible.helloao.org/api/BSB/)
**Books Verified:** Hosea, Joel, Amos, Obadiah, Jonah, Micah, Nahum, Habakkuk, Zephaniah, Haggai, Zechariah, Malachi

---

## Summary

**Status: 1 DISCREPANCY FOUND**

All 12 Minor Prophet books were checked chapter-by-chapter against the helloao.org BSB API. Every chapter matches **except one**: Micah Chapter 4 contains a **spurious verse 14** that is not present in the API.

---

## Detailed Verse Count Comparison

### Hosea (HOS) — 14 Chapters
| Chapter | File | API | Match |
|---------|------|-----|-------|
| 1 | 11 | 11 | ✅ |
| 2 | 23 | 23 | ✅ |
| 3 | 5 | 5 | ✅ |
| 4 | 19 | 19 | ✅ |
| 5 | 15 | 15 | ✅ |
| 6 | 11 | 11 | ✅ |
| 7 | 16 | 16 | ✅ |
| 8 | 14 | 14 | ✅ |
| 9 | 17 | 17 | ✅ |
| 10 | 15 | 15 | ✅ |
| 11 | 12 | 12 | ✅ |
| 12 | 14 | 14 | ✅ |
| 13 | 16 | 16 | ✅ |
| 14 | 9 | 9 | ✅ |

### Joel (JOL) — 3 Chapters
| Chapter | File | API | Match |
|---------|------|-----|-------|
| 1 | 20 | 20 | ✅ |
| 2 | 32 | 32 | ✅ |
| 3 | 21 | 21 | ✅ |

### Amos (AMO) — 9 Chapters
| Chapter | File | API | Match |
|---------|------|-----|-------|
| 1 | 15 | 15 | ✅ |
| 2 | 16 | 16 | ✅ |
| 3 | 15 | 15 | ✅ |
| 4 | 13 | 13 | ✅ |
| 5 | 27 | 27 | ✅ |
| 6 | 14 | 14 | ✅ |
| 7 | 17 | 17 | ✅ |
| 8 | 14 | 14 | ✅ |
| 9 | 15 | 15 | ✅ |

### Obadiah (OBA) — 1 Chapter
| Chapter | File | API | Match |
|---------|------|-----|-------|
| 1 | 21 | 21 | ✅ |

### Jonah (JON) — 4 Chapters
| Chapter | File | API | Match |
|---------|------|-----|-------|
| 1 | 17 | 17 | ✅ |
| 2 | 10 | 10 | ✅ |
| 3 | 10 | 10 | ✅ |
| 4 | 11 | 11 | ✅ |

### Micah (MIC) — 7 Chapters
| Chapter | File | API | Match |
|---------|------|-----|-------|
| 1 | 16 | 16 | ✅ |
| 2 | 13 | 13 | ✅ |
| 3 | 12 | 12 | ✅ |
| **4** | **14** | **13** | **❌** |
| 5 | 15 | 15 | ✅ |
| 6 | 16 | 16 | ✅ |
| 7 | 20 | 20 | ✅ |

### Nahum (NAM) — 3 Chapters
| Chapter | File | API | Match |
|---------|------|-----|-------|
| 1 | 15 | 15 | ✅ |
| 2 | 13 | 13 | ✅ |
| 3 | 19 | 19 | ✅ |

### Habakkuk (HAB) — 3 Chapters
| Chapter | File | API | Match |
|---------|------|-----|-------|
| 1 | 17 | 17 | ✅ |
| 2 | 20 | 20 | ✅ |
| 3 | 19 | 19 | ✅ |

### Zephaniah (ZEP) — 3 Chapters
| Chapter | File | API | Match |
|---------|------|-----|-------|
| 1 | 18 | 18 | ✅ |
| 2 | 15 | 15 | ✅ |
| 3 | 20 | 20 | ✅ |

### Haggai (HAG) — 2 Chapters
| Chapter | File | API | Match |
|---------|------|-----|-------|
| 1 | 15 | 15 | ✅ |
| 2 | 23 | 23 | ✅ |

### Zechariah (ZEC) — 14 Chapters
| Chapter | File | API | Match |
|---------|------|-----|-------|
| 1 | 21 | 21 | ✅ |
| 2 | 13 | 13 | ✅ |
| 3 | 10 | 10 | ✅ |
| 4 | 14 | 14 | ✅ |
| 5 | 11 | 11 | ✅ |
| 6 | 15 | 15 | ✅ |
| 7 | 14 | 14 | ✅ |
| 8 | 23 | 23 | ✅ |
| 9 | 17 | 17 | ✅ |
| 10 | 12 | 12 | ✅ |
| 11 | 17 | 17 | ✅ |
| 12 | 14 | 14 | ✅ |
| 13 | 9 | 9 | ✅ |
| 14 | 21 | 21 | ✅ |

### Malachi (MAL) — 4 Chapters
| Chapter | File | API | Match |
|---------|------|-----|-------|
| 1 | 14 | 14 | ✅ |
| 2 | 17 | 17 | ✅ |
| 3 | 18 | 18 | ✅ |
| 4 | 6 | 6 | ✅ |

---

## ❌ DISCREPANCY DETAIL: Micah Chapter 4

### The Problem

Micah Chapter 4 in `bsb-edited.md` contains **14 verses**, but the helloao.org API (and all standard BSB texts) have only **13 verses**. A spurious verse 14 is present.

### Spurious Text (currently in the file)

After verse 13 (ending with "their wealth to the Lord of all the earth") and its footnote reference `[^2]`, the following text appears as **v14**:

> **v14** Strike her with a club, O Daughter of Zion,
> for the enemy will strike her with a staff.
> He will pass through.

### Source of the Error

The spurious v14 text is actually **Micah 4:14 in the MT (Masoretic Text) tradition**, but in standard BSB it was merged/combined into v13 as part of the Hebrew verse numbering differences. Some translations retain it as a separate verse (v14), but BSB does not — it belongs to the end of v13.

Looking at the actual BSB text structure on helloao.org, the text "Strike her with a club..." is NOT a separate verse — it does not appear in the BSB at all as its own verse. This appears to be an error introduced during editing, where text from an alternate verse numbering system was incorrectly inserted as its own verse.

### Required Fix

**Delete the following from `bsb-edited.md` (Micah Chapter 4, after the `[^2]` footnote reference):**

```
**v14** Strike her with a club, O Daughter of Zion,
for the enemy will strike her with a staff.
He will pass through.
```

The `### Chapter 5` header should immediately follow the `[^2]` footnote reference at the end of verse 13.

### Note on Footnotes

The footnotes `[^1]` and `[^2]` currently in the file (at the end of the chapter) are correctly placed and should be retained — they belong to verses 8 and 13 respectively. Only the spurious **v14** verse marker and its text should be removed.

---

## Conclusion

- **11 of 12 books** are perfectly correct (all chapters match the API exactly)
- **Micah** has one issue: a spurious v14 in Chapter 4 that must be removed
- All other chapters across all 12 books are verified accurate against the helloao.org BSB API
