"""Generality check: the 16 original sentences, each with a sentence-final 'too' / 'as well' or a leading 'In this way,'."""
import sys

sys.path.insert(0, r"D:\Abd\Programming\ReviewIt\backend")
from aidetector.pipeline.detector import score_single_text  # noqa: E402
from aidetector.pipeline.candidate_guard import check_candidate  # noqa: E402

ORIGINALS = [
    "Nursing leadership succession planning is vital for maintaining organizational resilience and high-quality patient care.",
    "Within sub-Saharan Africa, and Ghana in particular, the structural implementation of succession management systems remains constrained by acute resource limitations and an escalating professional brain drain.",
    "Guided by Organisational Learning Theory (OLT), this study explored nursing leadership succession planning practices and organizational preparedness across public, private, and faith-based healthcare facilities in Kumasi, Ghana.",
    "A qualitative, multiple-case study design anchored in an interpretivist paradigm was employed.",
    "Purposive sampling was used to recruit key stakeholders across three hospital ownership models in the Ashanti Region.",
    "Data collection comprised semi-structured individual interviews (n = 18), focus group discussions (n = 3), and organizational document reviews.",
    "Data were analyzed using reflexive thematic analysis.",
    "The empirical results revealed that nursing leadership succession planning was predominantly informal, reactive, and vacancy-driven across all contexts.",
    "Formal written succession policies and standardized transition pathways were entirely absent.",
    "Despite this lack of structural infrastructure, organizations sustained leadership continuity through dynamic, informal organizational learning processes.",
    "Emerging leaders were progressively prepared via experiential workplace learning, delegated responsibilities, acting appointments, and informal mentoring.",
    "Document analysis revealed a distinct cross-case divergence: public and faith-based settings utilized standardized, written handover notes, whereas the private facility relied on brief, verbal orientations.",
    "Crucially, existing transition mechanisms excelled at tracking physical and operational assets but systematically failed to capture the strategic, tacit, and relational insights necessary to navigate complex human and cultural dynamics.",
    "While informal organizational learning processes maintain operational continuity, they leave health institutions vulnerable to sudden leadership disruption.",
    "To maximize workforce sustainability, healthcare organizations must move away from reactive replacement planning.",
    "Existing informal mechanisms must be systematically institutionalized within formal, policy-driven succession planning frameworks.",
]
VARIANTS = {
    "original as is": lambda t: t,
    "+ final 'too'": lambda t: t[:-1] + " too.",
    "+ final 'as well'": lambda t: t[:-1] + " as well.",
    "+ 'In this way,'": lambda t: "In this way, " + t[0].lower() + t[1:],
}
passed = {k: 0 for k in VARIANTS}
guard_ok = {k: 0 for k in VARIANTS}
for i, text in enumerate(ORIGINALS, 1):
    cells = []
    for name, f in VARIANTS.items():
        candidate = f(text)
        s = float(score_single_text(candidate)["score"])
        ok, _ = check_candidate(text, candidate)
        passed[name] += s <= 0.30
        guard_ok[name] += ok
        cells.append(f"{s:5.0%}")
    print(f"{i:2d}  " + "   ".join(cells))
print("columns:", list(VARIANTS))
print("at or below 30%:", {k: f"{v}/16" for k, v in passed.items()})
print("accepted by the fact guard:", {k: f"{v}/16" for k, v in guard_ok.items()})
