#!/usr/bin/env python3
"""Extract section headers from esv.md - conservative version using PDF exact matches."""
import re

PDF = "/Users/silas/Downloads/esv_pdf_full.txt"
MD = "/Users/silas/.openclaw/workspace/bibles/esv/esv.md"

# Step 1: Build PDF header set
print("Scanning PDF for section headers...")
with open(PDF, 'r', errors='replace') as f:
    pl = f.read().split('\n')

STOP = {'of','and','the','to','in','for','on','at','by','from','with','a','an',
        'is','are','was','were','be','been','his','her','their','you','your',
        'i','my','me','we','our','it','they','do','does','did','has','had',
        'have','will','would','shall','should','can','could','may','might',
        'but','or','if','so','not','than','then','when','where','who','how',
        'what','why','all','some','any','every','each','both','few','more',
        'most','other','such','only','own','same','these','those','this',
        'that','there','here','out','up','down','now','also','just','like',
        'about','after','before','because','between','through','during',
        'over','under','again','yet','still','very','much','many','come',
        'comes','came','going','gone','given','gives','gave','make','made',
        'takes','took','seen','sees','saw','know','knew','says','said',
        'let','send','sends','find','found','turned','turn','turns','speak',
        'spoke','heard','hear','call','calls','become','became','done',
        'remains','remained','keep','keeps','stand','stands','walk','walks',
        'live','lives','die','dies','born','bears','bore','raise','raises',
        'rise','rises','fell','fall','falls','sat','sit','set','left',
        'leave','leaves','held','hold','holds','brought','bring','brings',
        'went','get','gets','got','lay','lies','grow','grew','grows'}

pdf_headers = {}
for i in range(len(pl) - 1):
    line = pl[i].strip()
    nxt = pl[i+1].strip()
    if not line or not nxt:
        continue
    if not (re.match(r'^\d+$', nxt) or re.match(r'^:\d+$', nxt)):
        continue
    if re.match(r'^Chapter \d+$', line):
        continue
    if re.match(r'^The Holy Bible', line):
        continue
    if "'" in line:
        continue
    if len(line) > 45 or len(line) < 4:
        continue
    words = line.split()
    if len(words) < 2:
        continue
    if words[0][0].islower():
        continue
    ns = [w for w in words if w.lower() not in STOP and len(w) > 2]
    if ns and all(w[0].isupper() for w in ns):
        pdf_headers[line] = True

print(f"Found {len(pdf_headers)} PDF headers")
# Print a sample
for h in sorted(pdf_headers)[:15]:
    print(f"  {h}")

# Step 2: Find EXACT matches in markdown
print("\nScanning markdown for embedded headers...")
with open(MD, 'r') as f:
    lines = f.readlines()

fixed = 0
i = 0
while i < len(lines):
    line = lines[i]

    # Only verse lines
    if not re.match(r'^\*\*v\d+\*\*', line):
        i += 1
        continue

    # Find ". HeaderText" at end of verse line
    m = re.search(r'\. ([A-Z][^\.\n]+)$', line)
    if m:
        potential = m.group(1).strip()
        if potential in pdf_headers:
            # Extract: remove from verse line, insert as section header
            new_verse = line[:m.start()] + '\n'
            section = f"#### {potential}\n"
            lines[i] = new_verse
            lines[i+1:i+1] = [section]
            fixed += 1
            print(f"  Line {i}: '{potential}'")

    i += 1

print(f"\nFixed {fixed} embedded headers")
with open(MD, 'w') as f:
    f.writelines(lines)
print("Saved.")
