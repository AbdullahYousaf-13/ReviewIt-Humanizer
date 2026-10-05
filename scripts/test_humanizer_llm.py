import os
import sys
import time
import re
from groq import Groq
from dotenv import load_dotenv
load_dotenv()


client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def read_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.pdf':
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            return '\n\n'.join(page.extract_text() or '' for page in pdf.pages)
    elif ext == '.docx':
        from docx import Document
        doc = Document(path)
        return '\n'.join(p.text for p in doc.paragraphs if p.text.strip())
    elif ext == '.txt':
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        print(f"Unsupported file type: {ext}")
        sys.exit(1)

def extract_body(text):
    """Remove metadata header and references section."""
    # Cut off at References/Bibliography
    for marker in ['\nReferences\n', '\nREFERENCES\n', '\nBibliography\n']:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]

    # Skip first ~500 chars of PDF metadata garbage
    lines = text.split('\n')
    clean = []
    skip_header = True
    for line in lines:
        # Start keeping text once we hit Abstract or Introduction
        if skip_header and re.search(r'\b(Abstract|Introduction|abstract|ABSTRACT)\b', line):
            skip_header = False
        if not skip_header:
            clean.append(line)
    return '\n'.join(clean)

def clean_pdf_artifacts(text):
    # Remove isolated 1-2 char fragments surrounded by spaces (e.g. ".w", "e iv")
    text = re.sub(r'(?<= )\.[a-z]{1,2}(?= )', '', text)
    text = re.sub(r'(?<= )[a-z]{1,2} [a-z]{1,2}(?= )', '', text)
    # Remove stray non-ASCII characters common in PDF extraction (ligatures, etc.)
    text = re.sub(r'[^\x00-\x7F]+', lambda m: m.group() if m.group().isalpha() else ' ', text)
    # Collapse multiple spaces
    text = re.sub(r'  +', ' ', text)
    return text.strip()

def split_paragraphs(text):
    """Split into paragraphs, skip short lines (headers, DOIs, etc.)."""
    # First split on double newlines
    chunks = re.split(r'\n{2,}', text)
    result = []
    for chunk in chunks:
        chunk = chunk.strip().replace('\n', ' ')
        # Skip if too short (headers, section numbers, single lines)
        if len(chunk.split()) < 20:
            continue
        # Skip if it looks like a reference/citation line
        if re.match(r'^\[\d+\]', chunk):
            continue
        if re.match(r'^[A-Z][a-z]+,\s[A-Z]\.\s\(', chunk):
            continue
        # If chunk is very long (>300 words), split further by sentences
        words = chunk.split()
        if len(words) > 300:
            sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', chunk)
            group = []
            count = 0
            for s in sentences:
                group.append(s)
                count += len(s.split())
                if count >= 150:
                    para = ' '.join(group)
                    if len(para.split()) >= 20:
                        result.append(para)
                    group = []
                    count = 0
            if group:
                para = ' '.join(group)
                if len(para.split()) >= 20:
                    result.append(para)
        else:
            result.append(chunk)
    return result

def humanize_paragraph(para, index, total):
    para = clean_pdf_artifacts(para)
    word_count = len(para.split())

    for attempt in range(5):
        try:
            response = client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                messages=[
                    {
                        'role': 'system',
                        'content': "You are a plain-language editor. Rewrite academic text into simple, everyday English that a non-expert would write."
                    },
                    {
                        'role': 'user',
                        'content': f"""/no_think
Rewrite this paragraph in simple, everyday English.

RULES:
- Replace every complex or academic word with its simplest everyday synonym
- Break long sentences into shorter ones — aim for 8 to 15 words per sentence
- Occasionally start a sentence with "And" or "But" to sound natural
- Do NOT use formal connectors: no however, nevertheless, consequently, moreover, furthermore, thus, hence, thereby
- Keep all facts and do not add or remove any information
- Preserve all in-text citations exactly as they appear e.g. (Smith et al., 2020)
- Target length: ~{word_count} words — do not cut content to meet this
- Write like a person explaining something casually, not presenting research

Return ONLY the rewritten paragraph. No preamble, no explanation.

Paragraph:
{para}"""
                    }
                ],
                temperature=1.0,
                max_tokens=1024
            )
            result = response.choices[0].message.content.strip()
            if not result:
                print(f"[{index}/{total}] Empty response — keeping original")
                return para
            print(f"[{index}/{total}] ({word_count}w → {len(result.split())}w) done")
            return result

        except Exception as e:
            err = str(e)
            if '429' in err:
                # Parse Groq's actual "Please try again in X.XXXs" wait time
                match = re.search(r'try again in (\d+\.?\d*)s', err)
                wait = float(match.group(1)) + 2 if match else 60
                print(f"[{index}/{total}] Rate limit — waiting {wait:.0f}s...")
                time.sleep(wait)
            else:
                print(f"[{index}/{total}] Error: {err}")
                return para  # return original if failed

    print(f"[{index}/{total}] Failed after retries — keeping original")
    return para

# --- Main ---
if len(sys.argv) > 1:
    file_path = sys.argv[1]
    print(f"Reading: {file_path}")
    raw = read_file(file_path)
else:
    raw = """The implementation of machine learning algorithms has demonstrated significant potential in the domain of medical diagnosis. The utilization of deep neural networks enables the automated classification of medical images with remarkable accuracy. Furthermore, the integration of such computational methodologies facilitates the identification of pathological anomalies that would otherwise remain undetected by conventional diagnostic procedures. It is noteworthy that the aforementioned technological advancements have the potential to revolutionize the healthcare sector by enhancing diagnostic precision and reducing the probability of human error."""
    file_path = None

text = extract_body(raw)
paragraphs = split_paragraphs(text)
print(f"Found {len(paragraphs)} paragraphs to process\n")

start = time.time()
humanized = []

for i, para in enumerate(paragraphs, 1):
    result = humanize_paragraph(para, i, len(paragraphs))
    humanized.append(result)
    time.sleep(8)  # 1000 OTPM limit; ~290 tokens/call = max 3 calls/min, 8s spacing stays under

elapsed = time.time() - start
final = '\n\n'.join(humanized)

# Save output
if file_path:
    base = os.path.splitext(file_path)[0]
    out_path = base + "_humanized.txt"
else:
    out_path = "output_humanized.txt"

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(final)

print(f"\nDone in {elapsed:.0f}s")
print(f"Paragraphs: {len(paragraphs)}")
print(f"Saved to: {out_path}")
