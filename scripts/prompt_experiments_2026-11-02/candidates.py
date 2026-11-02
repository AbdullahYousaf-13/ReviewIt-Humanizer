"""Per-candidate pass rates from the two [humanizer-diag] logs (every Gemini candidate: call, shape, length ratio, score)."""
from collections import defaultdict

SHAPES1 = ["ordinary", "ordinary", "so", "ts", "se"]          # first call: spelled out = same order, two sentences, starts elsewhere
SHAPES2 = ["so", "ts", "se", "vc", "tsvc"]                      # retry: + verb clauses, two sentences with verb clauses
# (run, sentence, call, [(ratio, score%) x5]); a rejected candidate is left out
D = [
    ("A", "succession", 1, [(1.14, 100), (1.50, 100), (1.79, 100), (1.64, 100), (1.79, 100)]),
    ("A", "succession", 2, [(1.79, 98), (1.71, 100), (1.71, 100), (1.86, 99), (1.71, 100)]),
    ("A", "sub-Saharan", 1, [(1.00, 100), (1.19, 100), (1.42, 0), (1.77, 1), (1.38, 6)]),
    ("A", "Kumasi", 1, [(1.56, 100), (1.74, 100), (1.96, 100), (1.70, 100), (1.74, 100)]),
    ("A", "Kumasi", 2, [(1.85, 100), (1.70, 100), (1.63, 100), (1.78, 100), (1.67, 100)]),
    ("A", "interpretivist", 1, [(1.33, 99), (1.25, 100), (1.92, 100), (1.92, 99), (2.00, 100)]),
    ("A", "interpretivist", 2, [(1.67, 99), (1.58, 16), (1.67, 0), (1.50, 1), (1.50, 4)]),
    ("A", "purposive", 1, [(0.94, 100), (1.00, 100), (1.71, 90), (1.71, 100), (1.76, 100)]),
    ("A", "purposive", 2, [(1.76, 1), (1.65, 92), (1.65, 100), (1.71, 0), (1.59, 100)]),
    ("A", "data collection", 1, [(1.26, 98), (1.42, 0), (1.68, 100), (1.79, 100), (1.79, 100)]),
    ("A", "reflexive", 1, [(1.29, 100), (1.29, 100), (2.00, 100), (1.86, 98), (2.14, 100)]),
    ("A", "reflexive", 2, [(1.71, 100), (1.71, 100), (1.86, 100), (1.71, 99), (1.57, 100)]),
    ("A", "empirical", 1, [(1.28, 100), None, (1.61, 100), (1.67, 100), (1.61, 2)]),
    ("B", "sub-Saharan", 1, [(1.08, 100), (1.04, 100), (1.85, 29), (1.46, 5), (1.42, 99)]),
    ("B", "Kumasi", 1, [(1.59, 100), (1.33, 100), (1.70, 100), (1.70, 100), (1.63, 100)]),
    ("B", "Kumasi", 2, [(1.81, 100), (1.85, 100), (1.85, 100), (1.78, 100), (1.89, 100)]),
    ("B", "interpretivist", 1, [(1.33, 99), (1.25, 100), (1.92, 0), (1.58, 100), (1.83, 100)]),
    ("B", "purposive", 1, [(0.88, 100), (0.94, 100), (1.65, 29), (1.53, 100), (1.59, 100)]),
    ("B", "data collection", 1, [(1.37, 100), (1.32, 100), (1.47, 100), (1.58, 100), (1.68, 99)]),
    ("B", "data collection", 2, [(1.84, 100), (1.68, 100), (1.79, 100), (1.84, 100), (1.95, 95)]),
    ("B", "reflexive", 1, [(1.29, 100), (1.57, 100), (1.71, 100), (1.57, 100), (1.86, 5)]),
    ("B", "empirical", 1, [(1.50, 100), (1.39, 100), (2.00, 4), (2.06, 100), (1.78, 0)]),
    ("B", "existing informal", 1, [(1.00, 100), (1.08, 100), (1.77, 0), (1.62, 1), (1.77, 25)]),
]


def rate(items):
    return f"{sum(s <= 30 for _, s in items)}/{len(items)}"


by_shape = defaultdict(list)
by_call = defaultdict(list)
for run, sentence, call, cands in D:
    shapes = SHAPES1 if call == 1 else SHAPES2
    for shape, cand in zip(shapes, cands):
        if cand is None:
            continue
        by_shape[(call, shape)].append(cand)
        by_call[(call, "ordinary" if shape == "ordinary" else "spelled out")].append(cand)

print("per call and kind:")
for key in sorted(by_call):
    print("  call", key[0], f"{key[1]:12s}", rate(by_call[key]))
print("per shape:")
for key in sorted(by_shape):
    print("  call", key[0], f"{key[1]:9s}", rate(by_shape[key]))

spelled = [c for (call, k), v in by_call.items() if k == "spelled out" for c in v]
for lo, hi in ((1.3, 1.5), (1.5, 1.7), (1.7, 1.9), (1.9, 2.3)):
    sel = [c for c in spelled if lo <= c[0] < hi]
    print(f"spelled-out candidates of length x{lo}-x{hi}: {rate(sel)}")

print("\nper sentence (every spelled-out candidate, both calls and both runs):")
per = defaultdict(list)
for run, sentence, call, cands in D:
    shapes = SHAPES1 if call == 1 else SHAPES2
    for shape, cand in zip(shapes, cands):
        if cand is not None and shape != "ordinary":
            per[sentence].append(cand)
for sentence, items in per.items():
    print(f"  {sentence:16s} {rate(items)}")
