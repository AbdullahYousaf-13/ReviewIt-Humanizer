"""Why does 'Emerging leaders...' (a list of four items) not pass even with the new retry?
Full factorial: each of the 4 list items verbatim (V) or reworded (P), in a single sentence and in a split frame."""
import itertools
import sys

sys.path.insert(0, r"D:\Abd\Programming\ReviewIt\backend")
from aidetector.pipeline.detector import score_single_text  # noqa: E402
from aidetector.pipeline.candidate_guard import check_candidate  # noqa: E402

O = "Emerging leaders were progressively prepared via experiential workplace learning, delegated responsibilities, acting appointments, and informal mentoring."
ITEMS = [
    ("a", "experiential workplace learning", "learning from real work experience"),
    ("b", "delegated responsibilities", "being handed responsibilities"),
    ("c", "acting appointments", "covering in acting posts"),
    ("d", "informal mentoring", "getting informal mentoring"),
]
SUBJ = "People who were coming up as leaders were gradually prepared by"


def frame1(it):
    return f"{SUBJ} {it[0]}, {it[1]}, {it[2]}, and {it[3]}."


def frame2(it):
    tail = f"{it[2]} and {it[3]} also helped prepare them."
    return f"{SUBJ} {it[0]} and {it[1]}. {tail[0].upper() + tail[1:]}"


results = []
for frame_name, frame in (("single", frame1), ("split", frame2)):
    for pattern in itertools.product("VP", repeat=4):
        items = [(v if p == "V" else pl) for p, (_, v, pl) in zip(pattern, ITEMS)]
        text = frame(items)
        s = float(score_single_text(text)["score"])
        ok, why = check_candidate(O, text)
        results.append((frame_name, "".join(pattern), s, ok, len(text.split()) / len(O.split())))

print("frame  items(abcd)  score   <=par  guard   length")
for fr, pat, s, ok, r in results:
    print(f"{fr:6s} {pat}        {s:.4f}  {'yes' if s <= .30 else '   '}   {'ok' if ok else 'REJ'}    x{r:.2f}")

print("\npass rate when the item is reworded (P) vs verbatim (V), over both frames:")
for k, (key, v, pl) in enumerate(ITEMS):
    for mark in "VP":
        sel = [r for r in results if r[1][k] == mark]
        print(f"  item {key} {mark} ({(v if mark == 'V' else pl)[:34]:34s}): {sum(r[2] <= .30 for r in sel)}/{len(sel)}")
for fr in ("single", "split"):
    sel = [r for r in results if r[0] == fr]
    print(f"frame {fr}: {sum(r[2] <= .30 for r in sel)}/{len(sel)} reach the par score")
allv = [r for r in results if r[1] == "VVVV"]
print("all four verbatim:", [(r[0], round(r[2], 4)) for r in allv])
