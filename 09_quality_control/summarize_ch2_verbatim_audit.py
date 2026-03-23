import re
from pathlib import Path

p = Path(r"c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\09_quality_control\chapter2_verbatim_audit.md")
text = p.read_text(encoding="utf-8")
sections = re.split(r"\n## ", text)

weak = []
partial = []
supported = []
for sec in sections[1:]:
    key = sec.splitlines()[0].strip()
    w = len(re.findall(r"claim_\d+_status: weak_support", sec))
    pa = len(re.findall(r"claim_\d+_status: partially_supported", sec))
    su = len(re.findall(r"claim_\d+_status: supported", sec))
    if w:
        weak.append((w, key))
    if pa:
        partial.append((pa, key))
    if su:
        supported.append((su, key))

weak.sort(reverse=True)
partial.sort(reverse=True)
supported.sort(reverse=True)

print("WEAK_KEYS")
for n, k in weak:
    print(f"{k}\tweak_claims={n}")

print("\nTOP_PARTIAL_KEYS")
for n, k in partial[:15]:
    print(f"{k}\tpartial_claims={n}")

print("\nSUPPORTED_KEYS")
for n, k in supported:
    print(f"{k}\tsupported_claims={n}")

print(f"\nTOTAL_KEYS_WITH_WEAK={len(weak)}")
