# Document Summarizer Bot - Usage Examples

## 📖 Basic Examples

### Example 1: English Book
```bash
python main.py "Harry_Potter.pdf" en
```

**Output:** Creates elaborate chapter-by-chapter summaries + full book summary + suggestions

### Example 2: Bengali Article (বাংলা)
```bash
python main.py "রবীন্দ্রনাথের_গল্প.pdf" bn
```

**Output:** সম্পূর্ণ বাংলায় বিস্তারিত সারাংশ

### Example 3: Arabic Book (العربية)
```bash
python main.py "الكتاب_العربي.pdf" ar
```

**Output:** ملخص مفصل باللغة العربية

## 🎓 Academic Paper Examples

### Example 4: IEEE Research Paper
```bash
python main.py "ML_Research_2024.pdf" en --academic
```

**Output:**
- Abstract summary
- Introduction summary
- Methodology detailed explanation
- Results analysis
- Conclusion summary
- Key findings extraction
- Overall research summary

### Example 5: Springer Journal Article
```bash
python main.py "journal_article.pdf" en --academic
```

**Features:**
- Automatically detects academic sections
- Summarizes each section separately
- Extracts methodology, results, conclusions
- Provides comprehensive academic report

## 📚 Document Types

### Example 6: DOCX Document
```bash
python main.py "report.docx" en
```

### Example 7: Scanned PDF (OCR)
```bash
python main.py "scanned_book.pdf" bn
```
**Note:** Automatically uses OCR for scanned documents

### Example 8: Multi-language Document
```bash
# Document in English, summary in Bengali
python main.py "english_book.pdf" bn
```

## 🔍 Advanced Features

### Example 9: Large Book Processing
```bash
python main.py "war_and_peace.pdf" en
```
**Features:**
- Automatically chunks large documents
- Processes chapter by chapter
- Combines into coherent summaries
- Progress tracking in logs

### Example 10: Academic Paper with Graphs
```bash
python main.py "research_with_graphs.pdf" en --academic
```
**Note:** OCR will extract text from images/graphs if needed

## 📊 Output Examples

### General Document Output Structure:
```json
{
  "metadata": {
    "title": "Document Title",
    "file_name": "document.pdf",
    "total_words": 50000,
    "chapter_count": 15
  },
  "chapter_summaries": [
    {
      "chapter_number": "1",
      "chapter_title": "Introduction",
      "summary": "Elaborate summary..."
    }
  ],
  "full_summary": "Complete book summary...",
  "suggestions": "Reading suggestions and insights..."
}
```

### Academic Paper Output Structure:
```json
{
  "metadata": {...},
  "academic_report": {
    "overall_summary": "Research overview...",
    "key_findings": "Main discoveries...",
    "sections": {
      "Abstract": "Summary...",
      "Methodology": "Detailed method explanation...",
      "Results": "Findings analysis...",
      "Conclusion": "Final thoughts..."
    }
  }
}
```

## 🌍 Language-Specific Examples

### Bengali (বাংলা) Example:

**Input:**
```bash
python main.py "বাংলা_সাহিত্য.pdf" bn
```

**Output Sample:**
```
অধ্যায় ১: পরিচয়

এই অধ্যায়ে লেখক বাংলা সাহিত্যের ইতিহাস এবং এর বিবর্তন সম্পর্কে বিস্তারিত আলোচনা করেছেন। 
প্রাচীন যুগ থেকে শুরু করে আধুনিক যুগ পর্যন্ত বাংলা সাহিত্যের নানা দিক তুলে ধরা হয়েছে...
```

### Arabic (العربية) Example:

**Input:**
```bash
python main.py "كتاب_عربي.pdf" ar
```

**Output Sample:**
```
الفصل الأول: المقدمة

في هذا الفصل، يناقش المؤلف تاريخ الأدب العربي وتطوره بالتفصيل...
```

## 🎯 Use Cases

### Use Case 1: Student Reading Textbooks
```bash
# Summarize entire textbook
python main.py "biology_textbook.pdf" en

# Result: Chapter summaries for exam preparation
```

### Use Case 2: Researcher Reviewing Papers
```bash
# Quick academic paper review
python main.py "research_paper.pdf" en --academic

# Result: Methodology, results, and conclusions extracted
```

### Use Case 3: Author Analyzing Books
```bash
# Analyze competitor's book
python main.py "competitor_book.pdf" en

# Result: Structure analysis + suggestions
```

### Use Case 4: Translator Preparing Translation
```bash
# Understand Bengali book in English summary
python main.py "bengali_novel.pdf" en

# Result: English summary of Bengali content
```

### Use Case 5: News Article Summarization
```bash
# Summarize long news article
python main.py "news_article.pdf" bn

# Result: Elaborate Bengali summary
```

## 📝 Tips for Best Results

### Tip 1: Clean PDFs Work Best
- Use PDFs with good text extraction
- Scanned PDFs will use OCR (slower but works)

### Tip 2: Chapter Detection
- Clear chapter headings improve results
- Format: "Chapter 1: Title" or "1. Title"

### Tip 3: Academic Papers
- Always use `--academic` flag for research papers
- Works best with standard academic format

### Tip 4: Language Selection
- Choose output language, not input language
- Bot can summarize any language content in your preferred language

### Tip 5: Large Documents
- Processing time: ~1-2 minutes per 50 pages
- Logs show progress in real-time

## 🔄 Batch Processing Example

### Process Multiple Files:
```bash
# Create batch script (Windows)
for %%f in (*.pdf) do python main.py "%%f" en

# Linux/macOS
for file in *.pdf; do python main.py "$file" en; done
```

## 📦 Output Management

### Find Your Results:
```bash
# All summaries
cd outputs/

# All processing logs
cd logs/

# Latest summary
# outputs/document_name_en_20240112_143022.txt
```

### Read Results:
```bash
# View text summary
cat outputs/latest_summary.txt

# View JSON data
python -m json.tool outputs/latest_summary.json
```

## 🐛 Common Issues & Solutions

### Issue: "No chapters detected"
**Solution:** Document treated as single chapter - still works!

### Issue: "OCR taking too long"
**Solution:** Normal for scanned PDFs - wait or use pre-processed text PDF

### Issue: "Summary too brief"
**Solution:** Already using "elaborate" mode - this is comprehensive!

### Issue: "Wrong language output"
**Solution:** Check language parameter: en/bn/ar

## 🚀 Performance Tips

1. **Use text PDFs** (not scanned) for faster processing
2. **Close other applications** for large documents
3. **Check logs** for progress tracking
4. **Process overnight** for very large books (500+ pages)

## 💡 Creative Uses

1. **Book Club Prep**: Summarize before discussions
2. **Research Paper Review**: Quick literature review
3. **Content Analysis**: Analyze writing style and structure
4. **Study Notes**: Generate comprehensive study materials
5. **Translation Prep**: Understand content before translating

---

**Happy Summarizing!** 📚✨

For support, check logs or raise an issue on GitHub.