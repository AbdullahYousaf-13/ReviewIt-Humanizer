"""Would the fact guard reject the connective variants of Gemini's failing rewrites?"""
import sys

sys.path.insert(0, r"D:\Abd\Programming\ReviewIt\backend")
from aidetector.pipeline.candidate_guard import check_candidate  # noqa: E402
from aidetector.pipeline.gemini_prompt import STOCK_PHRASE_LIST  # noqa: E402

PAIRS = [  # (original, Gemini's failing rewrite)
    ("Nursing leadership succession planning is vital for maintaining organizational resilience and high-quality patient care.",
     "High-quality patient care and organizational resilience both depend vitally on succession planning for nursing leadership."),
    ("Guided by Organisational Learning Theory (OLT), this study explored nursing leadership succession planning practices and organizational preparedness across public, private, and faith-based healthcare facilities in Kumasi, Ghana.",
     "In Kumasi, Ghana, healthcare facilities run publicly or privately, as well as those based on faith, were studied to see how they plan for nursing leadership succession and how ready they are as organizations. Organisational Learning Theory (OLT) guided the inquiry."),
    ("Purposive sampling was used to recruit key stakeholders across three hospital ownership models in the Ashanti Region.",
     "A purposive approach to sampling guided the recruitment of key stakeholders from three models of hospital ownership in the Ashanti Region."),
    ("Emerging leaders were progressively prepared via experiential workplace learning, delegated responsibilities, acting appointments, and informal mentoring.",
     "People stepping into leadership were progressively prepared through informal mentoring alongside hands-on learning at work. Having responsibilities delegated to them and filling acting appointments served the same purpose."),
    ("While informal organizational learning processes maintain operational continuity, they leave health institutions vulnerable to sudden leadership disruption.",
     "Informal ways that organizations learn keep operations running smoothly, but they expose health institutions to sudden disruption in leadership."),
]
VARIANTS = {
    "too": lambda t: t[:-1] + " too.",
    "as well": lambda t: t[:-1] + " as well.",
    "In this way,": lambda t: "In this way, " + t[0].lower() + t[1:],
}
print("stock phrases the guard rejects include any of: too / as well / in this way ->",
      any(p in ("too", "as well", "in this way") for p in STOCK_PHRASE_LIST))
for name, f in VARIANTS.items():
    results = [check_candidate(original, f(rewrite)) for original, rewrite in PAIRS]
    print(f"{name:14s} accepted by the guard: {sum(ok for ok, _ in results)}/{len(results)}  reasons: {[why for ok, why in results if not ok]}")
print("(the five rewrites without a connective) accepted:", sum(check_candidate(o, r)[0] for o, r in PAIRS), "/ 5")
