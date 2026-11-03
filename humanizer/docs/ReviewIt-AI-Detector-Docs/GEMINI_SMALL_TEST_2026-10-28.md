# Small test of the latest prompt — 2026-10-28

10 flagged sentences from the student paper, Academic style, Gemini only (Humarin and T5 off), through the app's real pipeline: guard, 30% par rules and the one retry. Hard stops were 20 calls and $0.03; it stopped at neither.

## Summary

| | Previous prompt (5 rewrites per call, no retry feedback) | Latest prompt (2 rewrites + retry with earlier attempts) |
|---|---|---|
| Recommended rewrite at 30% AI or below | 8 of 10 | **6 of 10** |
| A second Gemini result shown (at 30% or below) | – | 2 of 10 |
| Sentences that needed the retry | – | 6 of 10 |
| Gemini calls | 10 (one per sentence) | 16 |
| Cost | about $0.015 | **$0.0161** ($0.0016 per sentence) |
| Time per sentence | – | 2.4–7.1 s (mean 5.2 s) |

Scores are our BERT detector on the single sentence. n = 10: one sentence moves the numbers by 10 points, so this shows where we stand, not a reliable percentage. The previous-prompt column is the recorded `GEMINI_PROMPT_V3` run on the same sentences.

## #20 — 5.6 s first call, 1 call(s), 6.7 s in total

**Original** (block score 98%; the sentence scored alone: 9%): This study is significant as it will introduce faculty who are and those who are not to the use of AI-generated content submitted by the students, and how their colleagues view it and react to it.

- **Call 1** (0% AI) Because it will show both faculty who are familiar with student-submitted, AI-generated content and those who are not how their peers see and respond to this work, this study matters.
- **Call 1** (0% AI) Faculty, whether they already know about students submitting AI-generated content or not, will learn through this study how their peers view and respond to it, which makes the work significant.

**Shown:** **Recommended**: 0% · **Option 1**: 0%  (gemini). **Meaning:** ✔
**Previous prompt:** best rewrite 0%

## #21 — 4.0 s first call, 2 call(s), 7.1 s in total

**Original** (block score 98%; the sentence scored alone: 100%): Since AI-generated content is leading a paradigm shift in content creation and knowledge representation, some researchers highlighted the need for addressing its ethical, privacy, security, and legal challenges (Wang, Pan, Yan, Su & Luan, 2023).

- **Call 1** ($0.00000): the reply held no rewrites.
- **Call 2** (1% AI) Because AI-generated content is driving a basic change in how people create content and represent knowledge, some researchers pointed out that its legal, security, privacy, and ethical challenges must be dealt with (Wang, Pan, Yan, Su & Luan, 2023).
- **Call 2** (100% AI) Some researchers stressed that we must deal with the ethical, privacy, security, and legal challenges of AI-generated content, as it is leading a fundamental shift in how content is made and knowledge is represented (Wang, Pan, Yan, Su & Luan, 2023).

**Shown:** **Recommended**: 1%  (gemini). **Meaning:** ⚠ "the need for addressing" became "must be dealt with" (strength)
**Previous prompt:** best rewrite 0%

## #25 — 2.9 s first call, 2 call(s), 6.6 s in total

**Original** (block score 100%; the sentence scored alone: 100%): To maximize the benefits of AI in education, it is crucial to address the challenges posed by AI in assessment, digital literacy, and ethical considerations and develop strategies for ensuring responsible and equitable implementation.

- **Call 1** (100% AI) Getting the most out of AI in education requires tackling the problems it brings to assessment, ethical considerations, and digital literacy. At the same time, strategies must be developed to ensure that its rollout is both responsible and fair.
- **Call 1** (100% AI) Educators and researchers must face the difficulties AI creates for digital literacy, ethical considerations, and assessment to gain its greatest benefits. They also need to build strategies that make sure it is applied in a fair and responsible way.
- **Call 2** (100% AI) Reaping the full advantages of AI in education depends on resolving the challenges it raises for ethical considerations, digital literacy, and assessment. Effective approaches must also be created so that it is introduced in an equitable and responsible manner.
- **Call 2** (100% AI) Making the most of educational AI requires addressing the hurdles it creates in digital literacy, assessment, and ethical considerations. Alongside this work, plans need to be made to ensure that the technology is implemented fairly and responsibly.

**Shown:** **Recommended**: 100%  (gemini). **Meaning:** ✔ (but still 100% AI)
**Previous prompt:** best rewrite 17%

## #30 — 2.5 s first call, 2 call(s), 5.1 s in total

**Original** (block score 97%; the sentence scored alone: 0%): Examples of Chatbots used in education are course inquiries, student support, student engagement and student feedback chatbots.

- **Call 1** (100% AI) In education, chatbots commonly handle course inquiries, student support, student engagement, and student feedback.
- **Call 1** (100% AI) Educational chatbots include those designed for student support and course inquiries. Others focus on student engagement and student feedback.
- **Call 2** (100% AI) Among educational applications, chatbots often collect student feedback or answer course inquiries. They also support and engage students.
- **Call 2** (100% AI) Chatbots deployed in education frequently engage students and offer student support, while other examples address student feedback and course inquiries.

**Shown:** **Recommended**: 0%  (original). **Meaning:** — original kept (see note 1)
**Previous prompt:** no rewrite kept

## #31 — 2.7 s first call, 2 call(s), 6.2 s in total

**Original** (block score 97%; the sentence scored alone: 99%): AI tools are software programs or applications that utilize AI techniques to perform specific tasks, such as natural language processing, data analysis and image recognition.

- **Call 1** (100% AI) Software programs or applications qualify as AI tools when they use AI techniques to carry out particular tasks, such as natural language processing, data analysis, and image recognition.
- **Call 1** (100% AI) By using AI techniques to handle specific tasks like natural language processing, data analysis, and image recognition, certain software programs or applications function as AI tools.
- **Call 2** (100% AI) Specific tasks such as image recognition, natural language processing, and data analysis can be carried out by software programs or applications known as AI tools, which apply AI techniques.
- **Call 2** (100% AI) When software programs or applications employ AI techniques, they become AI tools that address specific tasks. These include data analysis, natural language processing, and image recognition.

**Shown:** **Recommended**: 94%  (rule_based). **Meaning:** ⚠ rule-based fallback: only "utilize" → "use", shown as Recommended at 94%
**Previous prompt:** best rewrite 1%

## #74 — 2.7 s first call, 1 call(s), 2.9 s in total

**Original** (block score 100%; the sentence scored alone: 11%): Xames and Shefa (2023) revealed the challenges and concerns exposed by ChatGPT that require immediate attention such as AI authorship, nonexistent references, threats of international inequalities and unintentional plagiarism.

- **Call 1** (0% AI) Among the problems that ChatGPT brings to light and that need prompt action, Xames and Shefa (2023) pointed to unintentional plagiarism, AI authorship, fake references, and the threat of global inequalities.
- **Call 1** (100% AI) Issues uncovered by ChatGPT need quick action, as Xames and Shefa (2023) showed. These include unintentional plagiarism, false references, AI authorship, and risks of inequality across countries.

**Shown:** **Recommended**: 0%  (gemini). **Meaning:** ✔ ("revealed" → "pointed to")
**Previous prompt:** best rewrite 67%

## #75 — 3.2 s first call, 2 call(s), 6.2 s in total

**Original** (block score 100%; the sentence scored alone: 100%): Moreover, Firat (2023) emphasized that the use of AI in education raises ethical and social concerns about access, privacy, and the potential for increased reliance on technology, which may lead to reduced cognitive capacities among the students.

- **Call 1** (100% AI) Using AI in education brings up ethical and social worries regarding access and privacy, as Firat (2023) stressed. He also noted that students might depend more on technology, which may reduce their cognitive capacities.
- **Call 1** (100% AI) Firat (2023) highlighted the ethical and social issues that follow from using AI in education, pointing to matters of privacy, access, and the possibility that students will rely more on technology and perhaps weaken their cognitive capacities.
- **Call 2** (95% AI) Ethical and social questions surround privacy, access, and whether students will lean too much on technology and perhaps dull their cognitive capacities. Firat (2023) stressed these risks when AI is used in education.
- **Call 2** (100% AI) Students could end up relying more on technology, which may lower their cognitive capacities, alongside other ethical and social problems with access and privacy. Firat (2023) emphasized these points regarding the use of AI in education.

**Shown:** **Recommended**: 95%  (gemini). **Meaning:** ✔ (qualifiers kept; still 95% AI)
**Previous prompt:** best rewrite 0%

## #118 — 3.1 s first call, 2 call(s), 5.9 s in total

**Original** (block score 100%; the sentence scored alone: 99%): Students who actively used ChatGPT showed a greater ethical acceptance of its educational use compared to those who did not.

- **Call 1** (100% AI) Compared to their peers who did not, students who actively used ChatGPT found its educational use more ethically acceptable.
- **Call 1** (0% AI) ✘ rejected by the guard: direction of the claim reversed (e.g. higher -> lower) — Those who did not use ChatGPT accepted its educational use far less ethically than students who actively used it.
- **Call 2** (100% AI) Ethical acceptance of ChatGPT in education was higher among students who actively used the tool than among those who did not.
- **Call 2** (0% AI) Active users of ChatGPT viewed using it for education as more ethically acceptable than non-users did.

**Shown:** **Recommended**: 0%  (gemini). **Meaning:** ✔ (the comparison stayed a comparison)
**Previous prompt:** best rewrite 1%

## #29 — 2.3 s first call, 1 call(s), 2.4 s in total

**Original** (block score 97%; the sentence scored alone: 95%): They automate repetitive processes and interactions in a workflow.

- **Call 1** (11% AI) Within a workflow, they take over the processes and interactions that repeat.
- **Call 1** (0% AI) Repetitive interactions and processes in a workflow are automated by them.

**Shown:** **Recommended**: 0% · **Option 1**: 11%  (gemini). **Meaning:** ✔
**Previous prompt:** best rewrite 0%

## #73 — 2.2 s first call, 1 call(s), 2.4 s in total

**Original** (block score 100%; the sentence scored alone: 100%): For example, through health misinformation, a foreign adversary can make a whole population in a particular region more vulnerable to a future pandemic.

- **Call 1** (81% AI) A foreign adversary can, for example, use health misinformation to leave an entire regional population more at risk during a future pandemic.
- **Call 1** (3% AI) By spreading health misinformation, for instance, a foreign adversary can weaken an entire population in a given region ahead of a future pandemic.

**Shown:** **Recommended**: 3%  (gemini). **Meaning:** ⚠ "make more vulnerable" became "weaken" (stronger); the faithful rewrite scored 81%
**Previous prompt:** best rewrite 0%

## Notes

1. **Sentence alone vs its block.** The detector flags blocks of 4 sentences, but the humanizer scores one sentence alone. #20, #74 and #30 are red in the document (block 98–100%) yet score 9%, 11% and 0% alone. For #30 every rewrite scored 100% alone, so the original was kept.
2. **Ranking by the lowest score can choose the less faithful rewrite** (#73: "weaken" at 3% over the faithful rewrite at 81%).
3. **The rule-based fallback** ran for #31 and its near-copy was shown as Recommended at 94%; it is not filtered by the 30% rule.
4. **Retries:** 6 of 10 sentences retried (#21's first call returned no rewrites, so it retried at no cost). For #25, #30, #31 and #75 the retry did not help.
