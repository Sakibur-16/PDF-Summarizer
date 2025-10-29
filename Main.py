# Main.py
import os
import json
import re
import time
import requests
from pathlib import Path
from datetime import datetime
import PyPDF2
import docx
from langdetect import detect
from deep_translator import GoogleTranslator
from utils import setup_logger


class DocumentSummarizer:
    def __init__(self, api_key, output_lang='en'):
        self.api_key = api_key
        self.output_lang = output_lang
        self.lang_names = {'en': 'English', 'bn': 'Bengali', 'ar': 'Arabic'}
        self.logger = setup_logger()

    # ------------------- File Reading -------------------
    def read_pdf(self, path):
        text = ""
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
        return text

    def read_docx(self, path):
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs)

    def read_document(self, path):
        p = Path(path)
        if p.suffix.lower() == '.pdf':
            return self.read_pdf(p)
        if p.suffix.lower() in {'.docx', '.doc'}:
            return self.read_docx(p)
        raise ValueError("Only PDF/DOCX supported")

    # ------------------- Chapter Detection -------------------
    def detect_chapters(self, text):
        self.logger.info("Detecting chapters...")
        patterns = [
            r'(?:Chapter|CHAPTER|Ch\.?)\s*(\d+[A-Za-z]?)[:\-\.\s]*(.*?)(?:\n|$)',
            r'(\d+)\.\s+([A-Z][^\n]{5,100})',
            r'(?:Section|SECTION)\s*(\d+)[:\-\.\s]*(.*?)(?:\n|$)',
            r'(?:অধ্যায়|অ\.)\s*(\d+)[:\-\.\s]*(.*?)(?:\n|$)',
            r'(?:الفصل|الباب)\s*(\d+)[:\-\.\s]*(.*?)(?:\n|$)',
        ]
        chapters = []
        lines = text.splitlines()
        i = 0
        while i < len(lines):
            matched = False
            for pat in patterns:
                m = re.match(pat, lines[i].strip())
                if m:
                    num, title = m.group(1), m.group(2).strip()
                    start = text.find(lines[i])
                    end = start + 25000
                    for j in range(i + 1, min(i + 120, len(lines))):
                        if any(re.search(p, lines[j]) for p in patterns):
                            end = text.find(lines[j])
                            break
                    content = text[start:end]
                    chapters.append({"num": num, "title": title, "content": content})
                    i = j if end == text.find(lines[j]) else i + 1
                    matched = True
                    break
            if not matched:
                i += 1

        if not chapters:
            chunk = 20000
            for idx, pos in enumerate(range(0, len(text), chunk), 1):
                chapters.append({"num": str(idx), "title": f"Section {idx}",
                                 "content": text[pos:pos + chunk]})
        return chapters

    # ------------------- Research Sections -------------------
    def detect_research_sections(self, text):
        patterns = {
            'abstract': r'(?i)abstract[:\s]*(.*?)(?=\n[A-Z]{2,}|\n\d+\.|\Z)',
            'introduction': r'(?i)(?:introduction|1\.?\s+introduction)[:\s]*(.*?)(?=\n[A-Z]{2,}|\n\d+\.|\Z)',
            'methodology': r'(?i)(?:methodology|method|methods)[:\s]*(.*?)(?=\n[A-Z]{2,}|\n\d+\.|\Z)',
            'results': r'(?i)(?:results|findings)[:\s]*(.*?)(?=\n[A-Z]{2,}|\n\d+\.|\Z)',
            'discussion': r'(?i)discussion[:\s]*(.*?)(?=\n[A-Z]{2,}|\n\d+\.|\Z)',
            'conclusion': r'(?i)(?:conclusion|conclusions)[:\s]*(.*?)(?=\n[A-Z]{2,}|\n\d+\.|\Z)',
        }
        secs = {}
        for name, pat in patterns.items():
            m = re.search(pat, text, re.DOTALL)
            if m:
                secs[name] = m.group(1).strip()
        return secs

    # ------------------- Translation -------------------
    def translate(self, txt, target):
        if target == 'en':
            return txt
        try:
            tr = GoogleTranslator(source='auto', target=target)
            chunks = [txt[i:i + 4500] for i in range(0, len(txt), 4500)]
            return " ".join(tr.translate(c) for c in chunks)
        except Exception as e:
            self.logger.warning(f"Translation failed: {e}")
            return txt

    # ------------------- OpenRouter Call -------------------
    def openrouter(self, prompt, model="anthropic/claude-3.5-sonnet", cancel_event=None):
        """Centralised API call – respects cancel_event."""
        if cancel_event and cancel_event.is_set():
            self.logger.info("OpenRouter call cancelled by user")
            raise RuntimeError("Cancelled by user")

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "PDF Summarizer"
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4000,
            "temperature": 0.7
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    # ------------------- Summary Helpers -------------------
    def chapter_summary(self, text, num, title, cancel_event=None):
        prompt = f"""Write a **detailed, elaborated** summary in {self.lang_names[self.output_lang]}.
Chapter {num}: {title}
TEXT (first 15k chars):
{text[:15000]}
ELABORATED SUMMARY:"""
        return self.openrouter(prompt, cancel_event=cancel_event)

    def full_summary(self, text, cancel_event=None):
        prompt = f"""Write a **comprehensive, elaborated** full-document summary in {self.lang_names[self.output_lang]}.
Include purpose, structure, key arguments, findings, and take-aways.
TEXT (first 20k chars):
{text[:20000]}
FULL SUMMARY:"""
        return self.openrouter(prompt, cancel_event=cancel_event)

    def research_section_summary(self, text, name, cancel_event=None):
        prompt = f"""Summarise the **{name.upper()}** section in {self.lang_names[self.output_lang]}.
Include objectives, methods, data, conclusions – be detailed.
TEXT:
{text[:15000]}
SUMMARY:"""
        return self.openrouter(prompt, cancel_event=cancel_event)

    def suggestions(self, full_sum, cancel_event=None):
        prompt = f"""Give **actionable** suggestions in {self.lang_names[self.output_lang]}:
1. Key take-aways
2. Applications
3. Related books
4. Who benefits
5. Critical questions
SUMMARY:
{full_sum[:8000]}
SUGGESTIONS:"""
        return self.openrouter(prompt, cancel_event=cancel_event)

    # ------------------- Main Pipeline -------------------
    def summarise(self, file_path, doc_type='book', cancel_event=None):
        """
        Main entry point called from the GUI.
        cancel_event – threading.Event() from GUI (optional)
        """
        self.logger.info(f"Processing: {file_path}")

        # ---- Read document -------------------------------------------------
        text = self.read_document(file_path)

        # ---- Early language detection --------------------------------------
        detected = detect(text[:1000]) if len(text) > 100 else 'unknown'

        # ---- Result skeleton ------------------------------------------------
        result = {
            "file": Path(file_path).name,
            "detected_lang": detected,
            "output_lang": self.lang_names[self.output_lang],
            "doc_type": doc_type,
            "total_chars": len(text),
            "chapters": [],
            "full_summary": "",
            "research_sections": {},
            "suggestions": "",
            "cost_usd": 0.0,
            "json_path": "",
            "txt_path": ""
        }

        # ---- Chapters -------------------------------------------------------
        chapters = self.detect_chapters(text)
        for ch in chapters:
            if cancel_event and cancel_event.is_set():
                self.logger.info("Chapter summarisation cancelled")
                result["status"] = "cancelled"
                return result

            summ = self.translate(
                self.chapter_summary(ch['content'], ch['num'], ch['title'], cancel_event=cancel_event),
                self.output_lang
            )
            result["chapters"].append({"num": ch['num'], "title": ch['title'], "summary": summ})
            time.sleep(0.8)   # be nice to the API

        # ---- Research sections (only for research docs) --------------------
        if doc_type == 'research':
            secs = self.detect_research_sections(text)
            for name, txt in secs.items():
                if cancel_event and cancel_event.is_set():
                    self.logger.info("Research section summarisation cancelled")
                    result["status"] = "cancelled"
                    return result

                summ = self.translate(
                    self.research_section_summary(txt, name, cancel_event=cancel_event),
                    self.output_lang
                )
                result["research_sections"][name] = summ
                time.sleep(0.8)

     
        )

        # ---- Cost estimate --------------------------------------------------
        calls = len(chapters) + len(result["research_sections"]) + 2
        result["cost_usd"] = round(calls * (15_000 * 3e-6 + 4_000 * 15e-6), 4)

        # ---- Save JSON ------------------------------------------------------
        out_dir = Path('outputs')
        out_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = Path(file_path).stem

        json_path = out_dir / f"{timestamp}_{stem}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        result["json_path"] = str(json_path)

        # ---- Save human-readable .TXT ---------------------------------------
        txt_path = out_dir / f"{timestamp}_{stem}_summary.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("FULL DOCUMENT SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(result["full_summary"] + "\n\n")
            f.write("CHAPTER SUMMARIES\n")
            f.write("-" * 50 + "\n")
            for ch in result["chapters"]:
                f.write(f"\nChapter {ch['num']}: {ch['title']}\n")
                f.write(f"{ch['summary']}\n")
                f.write("-" * 40 + "\n")
        result["txt_path"] = str(txt_path)

        self.logger.info("Summarization complete!")
        return result