# Main.py - FULLY FIXED: OCR + Summary + Error Handling
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

# OCR (Safe Import)
try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

class DocumentSummarizer:
    def __init__(self, api_key, output_lang='en'):
        self.api_key = api_key
        self.output_lang = output_lang
        self.lang_names = {'en': 'English', 'bn': 'Bengali', 'ar': 'Arabic'}
        self.logger = setup_logger()

    def read_pdf(self, path):
        text = ""
        try:
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    t = page.extract_text()
                    if t: text += t + "\n\n"
            if len(text.strip()) > 300:
                self.logger.info("PDF is searchable")
                return text
        except Exception as e:
            self.logger.warning(f"Text extract failed: {e}")

        if not OCR_AVAILABLE:
            return "[ERROR: Install OCR → pip install pdf2image pytesseract]"

        self.logger.info("Running OCR on scanned PDF...")
        return self.ocr_pdf(path)

    def ocr_pdf(self, path):
        if not OCR_AVAILABLE: return "[OCR NOT AVAILABLE]"
        try:
            import tempfile
            with tempfile.TemporaryDirectory() as tmp:
                images = convert_from_path(path, dpi=300, output_folder=tmp, fmt='png')
                if not images: return "[OCR FAILED: No pages]"
                lang = 'eng+ben+ara'
                text = ""
                for i, img in enumerate(images):
                    page_text = pytesseract.image_to_string(img, lang=lang)
                    text += page_text + "\n\n"
                    if i % 10 == 0:
                        self.logger.info(f"OCR: {i+1}/{len(images)}")
                return text if text.strip() else "[OCR FAILED: No text detected]"
        except Exception as e:
            return f"[OCR ERROR: {str(e)}]"

    def read_docx(self, path):
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    def read_document(self, path):
        p = Path(path)
        if p.suffix.lower() == '.pdf': return self.read_pdf(p)
        if p.suffix.lower() in {'.docx', '.doc'}: return self.read_docx(p)
        raise ValueError("Only PDF/DOCX supported")

    def detect_chapters(self, text):
        patterns = [
            r'(?:Chapter|CHAPTER|Ch\.?)\s*(\d+[A-Za-z]?)[:\-\.\s]*(.*?)(?:\n|$)',
            r'(\d+)\.\s+([A-Z][^\n]{5,100})',
            r'(?:Section|SECTION)\s*(\d+)[:\-\.\s]*(.*?)(?:\n|$)',
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
                    end = start + 20000
                    for j in range(i + 1, min(i + 100, len(lines))):
                        if any(re.search(p, lines[j]) for p in patterns):
                            end = text.find(lines[j])
                            break
                    content = text[start:end].strip()
                    if len(content) > 100:
                        chapters.append({"num": num, "title": title, "content": content})
                    i = j
                    matched = True
                    break
            if not matched:
                i += 1
        if not chapters:
            chunks = [text[i:i+15000] for i in range(0, len(text), 15000)]
            for idx, chunk in enumerate(chunks, 1):
                if chunk.strip():
                    chapters.append({"num": str(idx), "title": f"Part {idx}", "content": chunk})
        return chapters

    def translate(self, txt, target):
        if target == 'en' or not txt.strip(): return txt
        try:
            tr = GoogleTranslator(source='auto', target=target)
            chunks = [txt[i:i+4500] for i in range(0, len(txt), 4500)]
            return " ".join(tr.translate(c) for c in chunks)
        except Exception as e:
            self.logger.warning(f"Translate failed: {e}")
            return txt

    def openrouter(self, prompt, cancel_event=None):
        if cancel_event and cancel_event.is_set():
            raise RuntimeError("Cancelled by user")
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "model": "anthropic/claude-3.5-sonnet",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 3000,
                "temperature": 0.7
            }
            resp = requests.post(url, json=payload, headers=headers, timeout=120)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise RuntimeError(f"API Error: {e}")

    def summarise(self, file_path, doc_type='book', cancel_event=None):
        self.logger.info(f"Processing: {file_path}")
        text = self.read_document(file_path)

        if not text.strip() or text.startswith("[ERROR") or text.startswith("[OCR"):
            raise RuntimeError(f"Failed to read document: {text[:200]}...")

        result = {
            "file": Path(file_path).name,
            "total_chars": len(text),
            "chapters": [],
            "full_summary": "[No full summary]",
            "suggestions": "[No suggestions]",
            "json_path": "",
            "txt_path": ""
        }

        # Chapters
        chapters = self.detect_chapters(text)
        for ch in chapters:
            if cancel_event and cancel_event.is_set():
                result["status"] = "cancelled"
                return result
            try:
                prompt = f"Summarize in {self.lang_names[self.output_lang]}:\nChapter {ch['num']}: {ch['title']}\n\n{ch['content'][:12000]}"
                summ = self.openrouter(prompt, cancel_event)
                summ = self.translate(summ, self.output_lang)
                result["chapters"].append({"num": ch['num'], "title": ch['title'], "summary": summ or "[Empty summary]"})
            except Exception as e:
                result["chapters"].append({"num": ch['num'], "title": ch['title'], "summary": f"[Error: {e}]"})
            time.sleep(1)

        # Full Summary
        try:
            prompt = f"Write a detailed full summary in {self.lang_names[self.output_lang]}:\n{text[:18000]}"
            full = self.openrouter(prompt, cancel_event)
            result["full_summary"] = self.translate(full, self.output_lang) or "[No full summary]"
        except Exception as e:
            result["full_summary"] = f"[Full summary failed: {e}]"

        # Suggestions
        try:
            prompt = f"Give 3 key suggestions from:\n{result['full_summary'][:6000]}"
            sugg = self.openrouter(prompt, cancel_event)
            result["suggestions"] = self.translate(sugg, self.output_lang) or "[No suggestions]"
        except Exception as e:
            result["suggestions"] = f"[Suggestions failed: {e}]"

        # Save Files
        out_dir = Path('outputs')
        out_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = Path(file_path).stem

        json_path = out_dir / f"{ts}_{stem}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        result["json_path"] = str(json_path)

        txt_path = out_dir / f"{ts}_{stem}_summary.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("FULL SUMMARY\n" + "="*50 + "\n\n")
            f.write(result["full_summary"] + "\n\n")
            f.write("CHAPTER SUMMARIES\n" + "-"*50 + "\n")
            for ch in result["chapters"]:
                f.write(f"\nChapter {ch['num']}: {ch['title']}\n")
                f.write(f"{ch['summary']}\n")
                f.write("-" * 40 + "\n")
        result["txt_path"] = str(txt_path)

        self.logger.info("Summarization complete!")
        return result