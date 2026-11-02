"""Does a small connective at the start or end flip rewrites that scored 97-100%? Free test, local detector only."""
import sys

sys.path.insert(0, r"D:\Abd\Programming\ReviewIt\backend")
from aidetector.pipeline.detector import score_single_text  # noqa: E402

FAILING = {  # final rewrites that scored 97-100% in earlier runs (full text)
    "succession planning": "High-quality patient care and organizational resilience both depend vitally on succession planning for nursing leadership.",
    "Kumasi": "In Kumasi, Ghana, healthcare facilities run publicly or privately, as well as those based on faith, were studied to see how they plan for nursing leadership succession and how ready they are as organizations. Organisational Learning Theory (OLT) guided the inquiry.",
    "purposive sampling": "A purposive approach to sampling guided the recruitment of key stakeholders from three models of hospital ownership in the Ashanti Region.",
    "emerging leaders": "People stepping into leadership were progressively prepared through informal mentoring alongside hands-on learning at work. Having responsibilities delegated to them and filling acting appointments served the same purpose.",
    "informal learning": "Informal ways that organizations learn keep operations running smoothly, but they expose health institutions to sudden disruption in leadership.",
}


def lower_first(text):
    return text[0].lower() + text[1:]


VARIANTS = {
    "as is": lambda t: t,
    "ends '...too.'": lambda t: t[:-1] + " too.",
    "ends '...as well.'": lambda t: t[:-1] + " as well.",
    "starts 'In this way,'": lambda t: "In this way, " + lower_first(t),
    "starts 'Overall,'": lambda t: "Overall, " + lower_first(t),
    "starts 'Also,'": lambda t: "Also, " + lower_first(t),
}

totals = {name: 0 for name in VARIANTS}
print(f"{'rewrite':22s}" + "".join(f"{name:24s}" for name in VARIANTS))
for label, text in FAILING.items():
    cells = []
    for name, f in VARIANTS.items():
        s = float(score_single_text(f(text))["score"])
        totals[name] += s <= 0.30
        cells.append(f"{s:6.1%}{' pass' if s <= 0.30 else '     '}".ljust(24))
    print(f"{label:22s}" + "".join(cells))
print("reach 30% or below:", {k: f"{v}/{len(FAILING)}" for k, v in totals.items()})
