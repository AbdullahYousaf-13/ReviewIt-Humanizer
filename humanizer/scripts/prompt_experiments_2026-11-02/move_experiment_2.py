"""Round 2: is it the plainer wording or just the extra length? Ablations + length-only controls + harder variants for S2/S3."""
import sys

sys.path.insert(0, r"D:\Abd\Programming\ReviewIt\backend")
from aidetector.pipeline.detector import score_single_text  # noqa: E402
from aidetector.pipeline.candidate_guard import check_candidate  # noqa: E402

O = {
    "S1": "Nursing leadership succession planning is vital for maintaining organizational resilience and high-quality patient care.",
    "S2": "Guided by Organisational Learning Theory (OLT), this study explored nursing leadership succession planning practices and organizational preparedness across public, private, and faith-based healthcare facilities in Kumasi, Ghana.",
    "S3": "Purposive sampling was used to recruit key stakeholders across three hospital ownership models in the Ashanti Region.",
    "S4": "Emerging leaders were progressively prepared via experiential workplace learning, delegated responsibilities, acting appointments, and informal mentoring.",
    "S5": "While informal organizational learning processes maintain operational continuity, they leave health institutions vulnerable to sudden leadership disruption.",
}

# kind: ABL = a passing variant with some formal phrases put back; W = formal wording padded to about the length of the
# passing variants (length only); P = harder plain-wording variants for the two sentences nothing rescued.
V = [
    ("S1", "ABL restore 'organizational resilience'", "Planning ahead for who will take over as nursing leaders is vital for maintaining organizational resilience and for keeping patient care at a high standard."),
    ("S1", "ABL restore 'high-quality patient care'", "Planning ahead for who will take over as nursing leaders is vital for keeping an organization able to bounce back and for maintaining high-quality patient care."),
    ("S1", "ABL restore 'succession planning for nursing leadership'", "Succession planning for nursing leadership is vital for keeping an organization able to bounce back and for keeping patient care at a high standard."),
    ("S1", "W formal wording, padded", "Nursing leadership succession planning is vital, and it is vital in particular for the purpose of maintaining organizational resilience and also for maintaining high-quality patient care."),
    ("S2", "W formal wording, padded", "Guided by Organisational Learning Theory (OLT), this study explored the nursing leadership succession planning practices as well as the organizational preparedness that are found across public, private, and faith-based healthcare facilities in Kumasi, Ghana."),
    ("S2", "P four short plain sentences", "Organisational Learning Theory (OLT) guided this study. It looked at how healthcare facilities in Kumasi, Ghana, plan for who takes over nursing leadership. It also looked at how ready the organizations are. The facilities were public, private, and faith-based."),
    ("S2", "P plain, 'looked at', two sentences", "This study looked at how healthcare facilities in Kumasi, Ghana, plan for who will take over nursing leadership and how ready their organizations are. The facilities were public, private, or faith-based, and Organisational Learning Theory (OLT) guided the work."),
    ("S3", "W formal wording, padded", "Purposive sampling was the method that was used in order to recruit key stakeholders across the three hospital ownership models that exist in the Ashanti Region."),
    ("S3", "P term replaced ('picked on purpose')", "Key stakeholders were picked on purpose. They came from three kinds of hospital ownership in the Ashanti Region."),
    ("S3", "P term kept, plain, two sentences", "Key stakeholders were recruited using a purposive sample. The hospitals they came from fell into three ownership models, all in the Ashanti Region."),
    ("S4", "ABL restore 'experiential workplace learning'", "People who were coming up as leaders were gradually prepared by experiential workplace learning and being handed responsibilities. Covering in acting posts and getting informal mentoring helped prepare them too."),
    ("S4", "ABL restore 'delegated responsibilities'/'acting appointments'", "People who were coming up as leaders were gradually prepared by learning from real work experience and delegated responsibilities. Acting appointments and informal mentoring helped prepare them too."),
    ("S4", "W formal wording, padded", "Emerging leaders were progressively prepared by means of experiential workplace learning, by means of delegated responsibilities, by means of acting appointments, and by means of informal mentoring."),
    ("S5", "ABL restore 'informal organizational learning processes'", "Informal organizational learning processes keep day-to-day operations going steadily, yet they leave health institutions open to a sudden disruption in who leads them."),
    ("S5", "ABL restore 'vulnerable to sudden leadership disruption'", "Informal ways of learning in organizations keep day-to-day operations going steadily, yet they leave health institutions vulnerable to sudden leadership disruption."),
    ("S5", "W formal wording, padded", "While informal organizational learning processes do serve to maintain operational continuity, they also serve to leave health institutions vulnerable to sudden leadership disruption."),
]

for sid, label, text in V:
    s = float(score_single_text(text)["score"])
    ok, why = check_candidate(O[sid], text)
    ratio = len(text.split()) / len(O[sid].split())
    print(f"{sid}  {s:.4f} {'<=par' if s <= 0.30 else '     '}  x{ratio:.2f}  guard={'ok' if ok else 'REJECT ' + why}  {label}")
