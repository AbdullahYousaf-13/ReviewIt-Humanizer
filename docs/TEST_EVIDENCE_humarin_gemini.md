# Test Evidence — humarin T5 Paraphraser and Gemini 3.5 Flash-Lite

Supporting record for the model comparison. Each test follows the product pipeline: a mostly
human-written passage contains AI-flagged sentences; only those sentences are rewritten and
reinserted; the reassembled passage is then scored by an AI-content detector.

In each **Original passage** below, the AI-flagged sentences are shown in **bold**; the
surrounding text is the untouched human-written context.

---

## humarin T5 Paraphraser

### Test 1 — Biopharma / clinical trials

**Original passage** (AI-flagged sentences in bold):

> Traditional 'linear and sequential' clinical trials are still the gold standard for ensuring the efficacy and safety of new drugs. **Historically speaking, this conventional methodology has persisted as a foundational pillar within the pharmaceutical industry, navigating the complex regulatory landscapes of drug development with steadfast reliability. By leveraging cutting-edge machine learning algorithms, artificial intelligence serves as a transformative catalyst capable of exponentially accelerating trial timelines while simultaneously maximizing operational efficiency and optimizing clinical success rates.** This is the third in a series of reports on AI's impact on the biopharma value chain (Lee, 2021) (Angus, 2020). Biopharma businesses have been able to obtain increasing volumes of scientific and research information from a multitude of sources in recent years, which is referred to as real-world data (RWD). **Nevertheless, organizations frequently encounter significant hurdles stemming from a deficiency in specialized technical competencies and advanced technological infrastructures required to fully harness the immense analytical power inherent within these expansive datasets.** Applying predictive AI models and advanced analytics to unlock RWD can help researchers better understand diseases, find relevant patients and important investigators, and enable revolutionary clinical study designs (Woo, 2019). **When seamlessly integrated with a robust digital ecosystem, sophisticated artificial intelligence algorithms can efficiently streamline the meticulous processes of data cleansing, aggregation, coding, and long-term preservation.** Furthermore, improved electronic data capture (EDC) may reduce the impact of human error in data collection while also allowing for smooth system integration (Mayorga-Ruiz et al., 2019).

**AI-flagged sentence → humanized rewrite:**

1. *"Historically speaking, this conventional methodology has persisted as a foundational pillar within the pharmaceutical industry, navigating the complex regulatory landscapes of drug development with steadfast reliability."*
   → "In the past, this old-fashioned method has continued to function as a key component of the pharmaceutical sector, operating with unwavering trustworthiness through the complex regulatory waters of drug development."
2. *"By leveraging cutting-edge machine learning algorithms, artificial intelligence serves as a transformative catalyst capable of exponentially accelerating trial timelines while simultaneously maximizing operational efficiency and optimizing clinical success rates."*
   → "With the help of machine learning algorithms, artificial intelligence can revolutionize trial timelines by driving down operational costs and improving clinical success rates."
3. *"Nevertheless, organizations frequently encounter significant hurdles stemming from a deficiency in specialized technical competencies and advanced technological infrastructures required to fully harness the immense analytical power inherent within these expansive datasets."*
   → "However, organizations often face significant challenges due to the inadequacy of specialized technical skills and technological infrastructures required to fully utilize the analytical power contained within these vast datasets."
4. *"When seamlessly integrated with a robust digital ecosystem, sophisticated artificial intelligence algorithms can efficiently streamline the meticulous processes of data cleansing, aggregation, coding, and long-term preservation."*
   → "By collaborating with a robust digital ecosystem, advanced artificial intelligence algorithms can efficiently simplify the task of data cleansing, aggregation, codification, and long-term preservation."

**Detector result (reassembled passage):** Copyleaks — **0% AI** ("No AI Content Found", 234 words human).

---

### Test 2 — Medical robots and data-driven medicine

**Original passage** (AI-flagged sentences in bold):

> In addition to medical personnel, certain medical robots assist patients. Exoskeleton robots, for example, can assist paralyzed patients in walking again and becoming self-sufficient (Shi et al., 2019). A smart prosthesis is another example of technology in action. These bionic limbs attach sensors that render them more responsive and accurate than natural body parts, with the option of covering them in bionic skin and connecting them to the user's muscles. Robots can help with rehabilitation and surgery. Cyberdyne's Hybrid Assistive Limb (HAL) exoskeleton, for example, is designed to help patients rehabilitate from conditions that lead to lower limb disorders, such as spinal cord injuries and strokes, by using sensors placed on the skin to efficiently detect electrical signals in the patient's body and responding with movement at the joint (Cruciger et al., 2016). **In today's fast-paced world, it is important to note that these groundbreaking technological advancements serve as a testament to human ingenuity, playing a pivotal role in revolutionizing the healthcare landscape and fostering a paradigm shift towards a more inclusive and accessible future for all.**
>
> From genome sequencing to creating a tailored health status from the data in our fitness/activity trackers, today's healthcare consumer has grown increasingly involved in their personal medical treatment. All of this big data is being compiled and linked to produce a more predictive picture of our health or medical status. **It is worth noting that in the ever-evolving landscape of modern medicine, the seamless integration of cutting-edge artificial intelligence plays a crucial role in unlocking the vast potential of big data, thereby facilitating improved patient outcomes and paving the way for a future where personalized healthcare is not just a luxury, but a fundamental human right.** Data-driven medicine has the potential to improve not just the precision and agility of genetic disease detection, but also to open the door to individualized medical treatments (Hummel & Braun, 2020).

**AI-flagged sentence → humanized rewrite:**

1. *"In today's fast-paced world, it is important to note that these groundbreaking technological advancements serve as a testament to human ingenuity, playing a pivotal role in revolutionizing the healthcare landscape and fostering a paradigm shift towards a more inclusive and accessible future for all."*
   → "In this fast-paced environment, it is crucial to recognize that these innovative technological advancements are a shining example of human innovation, revolutionizing the healthcare industry and helping to establish an inclusive and accessible future for all patients."
2. *"It is worth noting that in the ever-evolving landscape of modern medicine, the seamless integration of cutting-edge artificial intelligence plays a crucial role in unlocking the vast potential of big data, thereby facilitating improved patient outcomes and paving the way for a future where personalized healthcare is not just a luxury, but a fundamental human right."*
   → "In the midst of modern medicine, the seamless integration of advanced artificial intelligence is essential in unlocking the vast data sets that enable big data to improve patient outcomes and pave the way for personalized healthcare."

**Detector result (reassembled passage):** Copyleaks — **0% AI** ("No AI Content Found", 287 words human).

---

## Gemini 3.5 Flash-Lite

### Test 3 — AI-humanizer overview paragraph

**Original passage** (AI-flagged sentence in bold):

> Content creation has been revolutionized by advanced natural language generation (NLG) models, but this also poses a challenge in differentiating AI-written and human-written texts. AI Humanizers have been designed to modify AI-written content into more natural, human-like words which are also contextually appropriate. **In conclusion, it is vital to recognize that navigating this dynamic landscape requires a multifaceted approach to fully appreciate the transformative potential of these technologies.** This paper explores the techniques used by these humanizers to achieve content that seems human-written, often rendering AI detectors ineffective. Methods such as lexical substitution, sentence restructuring, sentiment adjustment, etc. This paper aims to give a deep understanding of how AI humanizers function.

**AI-flagged sentence → humanized rewrite:**

1. *"In conclusion, it is vital to recognize that navigating this dynamic landscape requires a multifaceted approach to fully appreciate the transformative potential of these technologies."*
   → "We need to use many different methods in this changing field. This helps us fully see how these new tools change things."

**Detector result (reassembled passage):** ZeroGPT — **0% AI** ("Human written"); Copyleaks — **0% AI** ("No AI Content Found", 108 words human).

---

### Test 4 — BERT abstract

**Original passage** (AI-flagged sentences in bold):

> We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. **Delve into the realm of cutting-edge innovation, as this paradigm-shifting breakthrough acts as a testament to the ever-evolving tapestry of modern technology.** As a result, the pre-trained BERT model can be fine-tuned with just one additional output layer to create state-of-the-art models for a wide range of tasks, such as question answering and language inference, without substantial task-specific architecture modifications. BERT is conceptually simple and empirically powerful. **Crucially, it is important to remember that navigating this digital landscape requires a holistic approach to fully grasp the sheer magnitude of these robust solutions.** It obtains new state-of-the-art results on eleven natural language processing tasks, including pushing the GLUE score to 80.5% (7.7% point absolute improvement), MultiNLI accuracy to 86.7% (4.6% absolute improvement), SQuAD v1.1 question answering Test F1 to 93.2 (1.5 point absolute improvement) and SQuAD v2.0 Test F1 to 83.1 (5.1 point absolute improvement).

**AI-flagged sentence → humanized rewrite:**

1. *"Delve into the realm of cutting-edge innovation, as this paradigm-shifting breakthrough acts as a testament to the ever-evolving tapestry of modern technology."*
   → "This new technology is a major breakthrough. It shows how modern technology keeps changing."
2. *"Crucially, it is important to remember that navigating this digital landscape requires a holistic approach to fully grasp the sheer magnitude of these robust solutions."*
   → "This digital world is very complex. You need a complete plan to understand these powerful tools."

**Detector result (reassembled passage):** Copyleaks — **100% AI → 0% AI** (from "AI Content Found" to "No AI Content Found"). All numeric results (GLUE 80.5%, MultiNLI 86.7%, SQuAD F1 93.2 / 83.1, and the point improvements) are preserved, as they sit in the untouched human-written sentences.

---

*All AI-flagged and humanized text above is taken verbatim from the recorded test runs. Detector scores are from ZeroGPT and Copyleaks.*
