"""Do passing rewrites keep fewer of the original's content words than failing ones? 27 full-text final rewrites of two runs."""
import re
import statistics

O = {
    "S1": "Nursing leadership succession planning is vital for maintaining organizational resilience and high-quality patient care.",
    "S2": "Within sub-Saharan Africa, and Ghana in particular, the structural implementation of succession management systems remains constrained by acute resource limitations and an escalating professional brain drain.",
    "S3": "Guided by Organisational Learning Theory (OLT), this study explored nursing leadership succession planning practices and organizational preparedness across public, private, and faith-based healthcare facilities in Kumasi, Ghana.",
    "S4": "A qualitative, multiple-case study design anchored in an interpretivist paradigm was employed.",
    "S5": "Purposive sampling was used to recruit key stakeholders across three hospital ownership models in the Ashanti Region.",
    "S6": "Data collection comprised semi-structured individual interviews (n = 18), focus group discussions (n = 3), and organizational document reviews.",
    "S7": "Data were analyzed using reflexive thematic analysis.",
    "S8": "The empirical results revealed that nursing leadership succession planning was predominantly informal, reactive, and vacancy-driven across all contexts.",
    "S9": "Formal written succession policies and standardized transition pathways were entirely absent.",
    "S10": "Despite this lack of structural infrastructure, organizations sustained leadership continuity through dynamic, informal organizational learning processes.",
    "S11": "Emerging leaders were progressively prepared via experiential workplace learning, delegated responsibilities, acting appointments, and informal mentoring.",
    "S12": "Document analysis revealed a distinct cross-case divergence: public and faith-based settings utilized standardized, written handover notes, whereas the private facility relied on brief, verbal orientations.",
    "S13": "Crucially, existing transition mechanisms excelled at tracking physical and operational assets but systematically failed to capture the strategic, tacit, and relational insights necessary to navigate complex human and cultural dynamics.",
    "S14": "While informal organizational learning processes maintain operational continuity, they leave health institutions vulnerable to sudden leadership disruption.",
    "S15": "To maximize workforce sustainability, healthcare organizations must move away from reactive replacement planning.",
    "S16": "Existing informal mechanisms must be systematically institutionalized within formal, policy-driven succession planning frameworks.",
}
R = [
    ("S1", "High-quality patient care and organizational resilience both depend vitally on succession planning for nursing leadership.", .9893),
    ("S2", "Putting succession management systems structurally into practice remains restricted across sub-Saharan Africa, and in Ghana especially. This difficulty stems from acute resource limits together with an escalating brain drain of professionals.", 0.0),
    ("S3", "In Kumasi, Ghana, healthcare facilities run publicly or privately, as well as those based on faith, were studied to see how they plan for nursing leadership succession and how ready they are as organizations. Organisational Learning Theory (OLT) guided the inquiry.", .9979),
    ("S4", "The inquiry adopted an interpretivist paradigm to ground its qualitative, multiple-case design.", .0013),
    ("S5", "A purposive approach to sampling guided the recruitment of key stakeholders from three models of hospital ownership in the Ashanti Region.", .9726),
    ("S6", "Reviewing organizational documents provided part of the data. The rest came from conducting semi-structured individual interviews (n = 18) and focus group discussions (n = 3).", .0131),
    ("S7", "A reflexive thematic analysis was carried out on the data.", .077),
    ("S8", "Nursing leadership succession planning was mostly informal regardless of context, as the empirical results showed. It took place only when posts became empty, reacting to needs as they came up.", .0159),
    ("S9", "There were entirely no standardized pathways for transition. Formal written policies for succession were also missing.", .0002),
    ("S10", "Even without such structural infrastructure, organizations kept leadership continuous by relying on dynamic, informal processes of learning as an organization.", .0091),
    ("S11", "People stepping into leadership were progressively prepared through informal mentoring alongside hands-on learning at work. Having responsibilities delegated to them and filling acting appointments served the same purpose.", .9743),
    ("S12", "A clear difference emerged across the cases upon analyzing the documents. Although public and faith-based settings used standardized handover notes in writing, the private facility depended instead on orientations that were brief and verbal.", .009),
    ("S13", "Although existing transition processes did very well at monitoring physical and operational resources, they systematically fell short elsewhere. In particular, they did not capture the strategic vision, unspoken understanding, and relational knowledge needed to handle complicated human and cultural patterns.", .0019),
    ("S14", "Informal ways that organizations learn keep operations running smoothly, but they expose health institutions to sudden disruption in leadership.", .9774),
    ("S15", "In order to make workforce sustainability as high as possible, healthcare organizations must leave behind reactive replacement planning.", .0),
    ("S16", "It is necessary to build existing informal mechanisms systematically into formal, policy-driven succession planning frameworks.", .1531),
    ("S1", "Care of high quality for patients is vital. So is keeping an organization resilient, and both require planning for who will follow current nursing leaders.", .0029),
    ("S2", "Putting succession management systems into place structurally is still limited across sub-Saharan Africa, particularly in Ghana. This is because resources are acutely limited and the professional brain drain is growing.", .0296),
    ("S3", "This study looked at healthcare facilities in Kumasi, Ghana. Guided by Organisational Learning Theory (OLT), it set out to see how these places plan for future nursing leaders to take over, checking how ready the organizations are across facilities that are public, those that operate privately, and settings that are founded on faith.", .2086),
    ("S4", "An interpretivist paradigm served as the foundation for this qualitative, multiple-case study design.", .0013),
    ("S5", "Three hospital ownership models were represented in the Ashanti Region. Key stakeholders from each of these models were chosen and brought into the study by means of purposive sampling.", .0009),
    ("S6", "People took part in semi-structured individual interviews (n = 18) and spoke together in focus group discussions (n = 3). Data were also drawn from looking over organizational documents.", .0054),
    ("S7", "Reflexive thematic analysis was carried out. In this way, the data were examined and analyzed.", .0606),
    ("S13", "Existing transition mechanisms performed very well when following physical and operational assets, but they systematically failed on another front. They did not capture the strategic, tacit, or relational understanding that people need in order to navigate complex human and cultural dynamics.", 0.0),
    ("S14", "Informal organizational learning keeps everyday operations going. Even so, it leaves health institutions open to unexpected disruption at the leadership level.", .0139),
    ("S15", "In order to achieve maximum workforce sustainability, healthcare organizations must turn away from planning replacements reactively.", .0015),
    ("S16", "Current informal mechanisms need to be built systematically into formal frameworks for succession planning that policy drives.", .0054),
]
STOP = set("that this with from which these those their there where while whereas across through about between within".split())


def stems(text):
    return {w[:6] for w in re.findall(r"[a-z]+", text.lower()) if len(w) >= 6 and w not in STOP}


rows = []
for sid, text, score in R:
    base = stems(O[sid])
    kept = len(base & stems(text)) / len(base)
    ratio = len(text.split()) / len(O[sid].split())
    rows.append((sid, kept, ratio, score <= 0.30))

passing = [r for r in rows if r[3]]
failing = [r for r in rows if not r[3]]
print(f"passing rewrites: {len(passing)}, keep on average {statistics.mean(r[1] for r in passing):.2f} of the original's content words "
      f"(median {statistics.median(r[1] for r in passing):.2f}), length x{statistics.mean(r[2] for r in passing):.2f}")
print(f"failing rewrites: {len(failing)}, keep on average {statistics.mean(r[1] for r in failing):.2f} "
      f"(median {statistics.median(r[1] for r in failing):.2f}), length x{statistics.mean(r[2] for r in failing):.2f}")
print("failing:", [(r[0], round(r[1], 2)) for r in failing])
for lo, hi in ((0, 0.4), (0.4, 0.6), (0.6, 1.01)):
    sel = [r for r in rows if lo <= r[1] < hi]
    print(f"keeps {lo:.0%}-{min(hi, 1):.0%} of the content words: {sum(r[3] for r in sel)}/{len(sel)} pass")
