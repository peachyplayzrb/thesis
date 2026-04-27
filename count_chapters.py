import pathlib
import re

def count_words(path):
    if not path.exists():
        return 0
    text = path.read_text(encoding='utf-8')
    # Remove headings
    text = re.sub(r'(?m)^#{1,6}\s.*$', '', text)
    # Remove image refs
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    # Count words
    return len(text.split())

# Test word counts
ch4_lean_rewrite = count_words(pathlib.Path('08_writing/chapter4_v2_LEAN_REWRITE.md'))
ch4_appendix = count_words(pathlib.Path('08_writing/chapter4_appendix.md'))
ch4_old = count_words(pathlib.Path('08_writing/chapter4.md'))
ch4_v2_old = count_words(pathlib.Path('08_writing/chapter4_v2.md'))

print('=== WORD COUNTS ===')
print(f'chapter4_v2_LEAN_REWRITE.md: {ch4_lean_rewrite} words')
print(f'chapter4_appendix.md:        {ch4_appendix} words')
print(f'chapter4.md (old 742):       {ch4_old} words')
print(f'chapter4_v2.md (old):        {ch4_v2_old} words')
print()
print('=== THESIS TOTALS ===')
ch1, ch2, ch3, ch5, ch6 = 820, 3319, 3512, 1788, 1260
total_with_lean = ch1 + ch2 + ch3 + ch4_lean_rewrite + ch5 + ch6
total_with_old = ch1 + ch2 + ch3 + ch4_old + ch5 + ch6
total_with_v2 = ch1 + ch2 + ch3 + ch4_v2_old + ch5 + ch6

print(f'Ch1+2+3+LEAN+5+6:  {total_with_lean} words  target: 8k-12k')
print(f'Ch1+2+3+OLD+5+6:   {total_with_old} words')
print(f'Ch1+2+3+V2+5+6:    {total_with_v2} words')
