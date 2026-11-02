"""End to end with the REAL detector and guard; Gemini is mocked to return rewrites that really failed (97-100%) earlier."""
import json
import logging
import sys
from types import SimpleNamespace

sys.path.insert(0, r"D:\Abd\Programming\ReviewIt\backend")
from aidetector.pipeline import humanizer as hz  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(message)s")
hz.HAS_T5 = False
hz._load_humarin_singleton = lambda: (None, None, None)

CASES = [
    ("Guided by Organisational Learning Theory (OLT), this study explored nursing leadership succession planning practices and organizational preparedness across public, private, and faith-based healthcare facilities in Kumasi, Ghana.",
     ["In Kumasi, Ghana, healthcare facilities run publicly or privately, as well as those based on faith, were studied to see how they plan for nursing leadership succession and how ready they are as organizations. Organisational Learning Theory (OLT) guided the inquiry."]),
    ("Nursing leadership succession planning is vital for maintaining organizational resilience and high-quality patient care.",
     ["High-quality patient care and organizational resilience both depend vitally on succession planning for nursing leadership."]),
    ("Emerging leaders were progressively prepared via experiential workplace learning, delegated responsibilities, acting appointments, and informal mentoring.",
     ["People stepping into leadership were progressively prepared through informal mentoring alongside hands-on learning at work. Having responsibilities delegated to them and filling acting appointments served the same purpose."]),
]
for original, rewrites in CASES:
    engine = hz.ProfessionalHumanizer(use_t5=False)
    engine.gemini_client = object()
    engine._humanize_rule_based = lambda *a, **k: SimpleNamespace(humanized=original, new_score=1.0)
    replies = [rewrites, rewrites]  # both calls give the same failing rewrite(s): this is the "retry also failed" case
    calls = []

    def call(client, prompt, _r=replies, _c=calls, **kw):
        _c.append(1)
        return json.dumps({"rewrites": _r[len(_c) - 1]}), "mock"

    engine._call_gemini = call
    hz._gemini_blocked_until = 0.0
    result = engine.humanize_single_sentence_smart(original, original_score=1.0)
    print(f"\nORIGINAL : {original[:90]}...")
    print(f"gemini calls={len(calls)}  engine={result['engine']}  score {result['original_score']:.0%} -> {result['new_score']:.0%}  label={result['label']}  failed={result['failed']}")
    print(f"SHOWN    : {result['humanized']}")
