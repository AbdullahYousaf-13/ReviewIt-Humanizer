"""Offline experiment: which kind of change moves the detector score on the 5 sentences that still fail.
No Gemini calls. Scores with the app's own score_single_text (each text alone) and checks the app's fact guard."""
import json
import statistics
import sys

sys.path.insert(0, r"D:\Abd\Programming\ReviewIt\backend")
from aidetector.pipeline.detector import score_single_text  # noqa: E402
from aidetector.pipeline.candidate_guard import check_candidate  # noqa: E402

PAR = 0.30

# key: A split in two | B active<->passive / subject flip | C start from another part | D abstract nouns -> verb clauses
#      E plainer, wordier wording | AE, CE, DE, AD = combinations
S = {
    "S1": {
        "O": "Nursing leadership succession planning is vital for maintaining organizational resilience and high-quality patient care.",
        "G": "High-quality patient care and organizational resilience both depend vitally on succession planning for nursing leadership.",
        "G_logged": 0.9893,
        "V": {
            "A": "Succession planning for nursing leadership is vital. It is needed to maintain organizational resilience and high-quality patient care.",
            "B": "Organizational resilience and high-quality patient care are kept up by nursing leadership succession planning, which is vital.",
            "C": "To maintain organizational resilience and high-quality patient care, succession planning for nursing leadership is vital.",
            "D": "Planning for who will succeed nursing leaders is vital if organizations are to stay resilient and keep delivering high-quality patient care.",
            "E": "Planning ahead for who will take over as nursing leaders is vital for keeping an organization able to bounce back and for keeping patient care at a high standard.",
            "AE": "Planning ahead for who will take over as nursing leaders is vital. It keeps an organization able to bounce back and keeps patient care at a high standard.",
            "CE": "To keep an organization able to bounce back and patient care at a high standard, planning ahead for who will take over as nursing leaders is vital.",
            "DE": "Planning for who will take over as nursing leaders is vital if organizations are to stay able to bounce back and keep patient care at a high standard.",
            "AD": "Planning for who will succeed nursing leaders is vital. It lets organizations stay resilient and keep delivering high-quality patient care.",
        },
    },
    "S2": {
        "O": "Guided by Organisational Learning Theory (OLT), this study explored nursing leadership succession planning practices and organizational preparedness across public, private, and faith-based healthcare facilities in Kumasi, Ghana.",
        "G": "In Kumasi, Ghana, healthcare facilities run publicly or privately, as well as those based on faith, were studied to see how they plan for nursing leadership succession and how ready they are as organizations. Organisational Learning Theory (OLT) guided the inquiry.",
        "G_logged": 0.9979,
        "V": {
            "A": "This study explored nursing leadership succession planning practices and organizational preparedness across public, private, and faith-based healthcare facilities in Kumasi, Ghana. It was guided by Organisational Learning Theory (OLT).",
            "B": "Nursing leadership succession planning practices and organizational preparedness were explored in this study, which was guided by Organisational Learning Theory (OLT), across public, private, and faith-based healthcare facilities in Kumasi, Ghana.",
            "C": "Across public, private, and faith-based healthcare facilities in Kumasi, Ghana, this study explored nursing leadership succession planning practices and organizational preparedness, guided by Organisational Learning Theory (OLT).",
            "D": "This study, guided by Organisational Learning Theory (OLT), explored how nursing leadership succession is planned and how prepared organizations are, across public, private, and faith-based healthcare facilities in Kumasi, Ghana.",
            "E": "This study looked at how public, private, and faith-based healthcare facilities in Kumasi, Ghana, plan for who will take over nursing leadership and how ready the organizations are, using Organisational Learning Theory (OLT) as its guide.",
            "AE": "This study looked at how public, private, and faith-based healthcare facilities in Kumasi, Ghana, plan for who will take over nursing leadership and how ready their organizations are. Organisational Learning Theory (OLT) guided the work.",
            "CE": "In public, private, and faith-based healthcare facilities in Kumasi, Ghana, this study looked at how they plan for who will take over nursing leadership and how ready the organizations are, guided by Organisational Learning Theory (OLT).",
            "DE": "Guided by Organisational Learning Theory (OLT), the study asked how healthcare facilities in Kumasi, Ghana, whether public, private, or faith-based, plan for who will take over nursing leadership and how ready they are as organizations.",
            "AD": "The study asked how nursing leadership succession is planned and how prepared organizations are, across public, private, and faith-based healthcare facilities in Kumasi, Ghana. Organisational Learning Theory (OLT) guided it.",
        },
    },
    "S3": {
        "O": "Purposive sampling was used to recruit key stakeholders across three hospital ownership models in the Ashanti Region.",
        "G": "A purposive approach to sampling guided the recruitment of key stakeholders from three models of hospital ownership in the Ashanti Region.",
        "G_logged": 0.9726,
        "V": {
            "A": "Key stakeholders were recruited through purposive sampling. They came from three hospital ownership models in the Ashanti Region.",
            "B": "Recruitment of key stakeholders across three hospital ownership models in the Ashanti Region relied on purposive sampling.",
            "C": "Across three hospital ownership models in the Ashanti Region, key stakeholders were recruited using purposive sampling.",
            "D": "Key stakeholders were recruited purposively, with people chosen from across three hospital ownership models in the Ashanti Region.",
            "E": "Key stakeholders were brought in through purposive sampling, and they were drawn from three kinds of hospital ownership in the Ashanti Region.",
            "AE": "Key stakeholders were brought in through purposive sampling. They were drawn from three kinds of hospital ownership in the Ashanti Region.",
            "CE": "From three kinds of hospital ownership in the Ashanti Region, key stakeholders were brought in through purposive sampling.",
            "DE": "Key stakeholders were recruited purposively, with people picked from each of three kinds of hospital ownership in the Ashanti Region.",
            "AD": "Key stakeholders were recruited purposively. People were chosen from across three hospital ownership models in the Ashanti Region.",
        },
    },
    "S4": {
        "O": "Emerging leaders were progressively prepared via experiential workplace learning, delegated responsibilities, acting appointments, and informal mentoring.",
        "G": "People stepping into leadership were progressively prepared through informal mentoring alongside hands-on learning at work. Having responsibilities delegated to them and filling acting appointments served the same purpose.",
        "G_logged": 0.9743,
        "V": {
            "A": "Emerging leaders were progressively prepared through experiential workplace learning and delegated responsibilities. Acting appointments and informal mentoring also prepared them.",
            "B": "Experiential workplace learning, delegated responsibilities, acting appointments, and informal mentoring progressively prepared emerging leaders.",
            "C": "Through experiential workplace learning, delegated responsibilities, acting appointments, and informal mentoring, emerging leaders were progressively prepared.",
            "D": "Emerging leaders were progressively prepared as they learned by doing at work, took on delegated responsibilities, held acting appointments, and received informal mentoring.",
            "E": "People who were coming up as leaders were gradually prepared by learning from real work experience, being handed responsibilities, covering in acting posts, and getting informal mentoring.",
            "AE": "People who were coming up as leaders were gradually prepared by learning from real work experience and being handed responsibilities. Covering in acting posts and getting informal mentoring helped prepare them too.",
            "CE": "By learning from real work experience, being handed responsibilities, covering in acting posts, and getting informal mentoring, people coming up as leaders were gradually prepared.",
            "DE": "Emerging leaders were gradually prepared as they learned from real work experience, took on handed-over responsibilities, covered in acting posts, and got informal mentoring.",
            "AD": "Emerging leaders were progressively prepared as they learned by doing at work and took on delegated responsibilities. They also held acting appointments and received informal mentoring.",
        },
    },
    "S5": {
        "O": "While informal organizational learning processes maintain operational continuity, they leave health institutions vulnerable to sudden leadership disruption.",
        "G": "Informal ways that organizations learn keep operations running smoothly, but they expose health institutions to sudden disruption in leadership.",
        "G_logged": 0.9774,
        "V": {
            "A": "Informal organizational learning processes maintain operational continuity. They also leave health institutions vulnerable to sudden leadership disruption.",
            "B": "Operational continuity is maintained by informal organizational learning processes, but health institutions are left vulnerable to sudden leadership disruption.",
            "C": "Health institutions are left vulnerable to sudden leadership disruption, even though informal organizational learning processes maintain operational continuity.",
            "D": "While organizations keep operating because they learn informally, health institutions remain vulnerable when their leadership is suddenly disrupted.",
            "E": "Informal ways of learning in organizations keep day-to-day operations going steadily, yet they leave health institutions open to a sudden disruption in who leads them.",
            "AE": "Informal ways of learning in organizations keep day-to-day operations going steadily. Even so, they leave health institutions open to a sudden disruption in who leads them.",
            "CE": "Health institutions are left open to a sudden disruption in who leads them, even though informal ways of learning in organizations keep day-to-day operations going steadily.",
            "DE": "Organizations keep day-to-day operations going steadily because they learn informally, but this leaves health institutions open to a sudden disruption in who leads them.",
            "AD": "Organizations keep operating steadily because they learn informally. This leaves health institutions vulnerable when leadership is suddenly disrupted.",
        },
    },
}


def score(text):
    return float(score_single_text(text)["score"])


rows = []
print("== control: does my scoring reproduce the logged scores of Gemini's rewrites? ==")
for sid, d in S.items():
    g = score(d["G"])
    print(f"{sid}: logged {d['G_logged']:.4f}  offline {g:.4f}  {'MATCH' if abs(g - d['G_logged']) < 0.0006 else 'DIFFERENT'}")
    o = score(d["O"])
    ok, why = check_candidate(d["O"], d["G"])
    rows.append((sid, "O", o, True, ""))
    rows.append((sid, "G", g, ok, why))
    print(f"    original scored alone: {o:.4f}")

print("\n== variants (each text scored alone; guard = the app's fact guard against the original) ==")
for sid, d in S.items():
    for move, text in d["V"].items():
        s = score(text)
        ok, why = check_candidate(d["O"], text)
        rows.append((sid, move, s, ok, why))
        print(f"{sid} {move:2s}  {s:.4f}  {'<=par' if s <= PAR else '     '}  guard={'ok' if ok else 'REJECT: ' + why}")

print("\n== per move: how many of the 5 sentences end at or below the par score (30%) ==")
moves = ["A", "B", "C", "D", "E", "AE", "CE", "DE", "AD"]
for m in moves:
    sel = [r for r in rows if r[1] == m]
    low = [r for r in sel if r[2] <= PAR]
    low_ok = [r for r in low if r[3]]
    guard_ok = [r for r in sel if r[3]]
    print(f"{m:2s}: <=par {len(low)}/{len(sel)}   <=par and guard ok {len(low_ok)}/{len(sel)}   guard ok {len(guard_ok)}/{len(sel)}   median {statistics.median(r[2] for r in sel):.3f}")

print("\n== per sentence: any variant at or below par (and guard ok) ==")
for sid in S:
    sel = [r for r in rows if r[0] == sid and r[1] in moves]
    good = [r[1] for r in sel if r[2] <= PAR and r[3]]
    low = [r[1] for r in sel if r[2] <= PAR]
    print(f"{sid}: <=par {low}   <=par and guard ok {good}")

json.dump(rows, open("move_experiment_results.json", "w"), indent=1)
