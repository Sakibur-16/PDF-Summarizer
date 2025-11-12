# 📚 Document Summarizer Bot (OpenRouter Edition)

> AI-powered document summarization bot with OCR support for Bengali, English, and Arabic languages

## 🌟 Features

### Core Capabilities
- ✅ **Multi-format Support**: PDF (text & scanned), DOCX
- ✅ **OCR Built-in**: Automatic text extraction from scanned documents
- ✅ **3 Languages**: Bengali (বাংলা), English, Arabic (العربية)
- ✅ **Elaborate Summaries**: Comprehensive, human-like summaries (not brief)
- ✅ **Chapter-wise Analysis**: Individual chapter summaries + full document summary
- ✅ **Academic Paper Mode**: Special processing for research papers (IEEE, Springer, etc.)
- ✅ **Smart Suggestions**: Content-based recommendations and insights
- ✅ **Comprehensive Logging**: Track all processing steps

### Academic Paper Features
- 📄 **Section Detection**: Automatically identifies Abstract, Introduction, Methodology, Results, Conclusion
- 🔬 **Detailed Analysis**: Elaborate summaries of each section
- 📊 **Key Findings Extraction**: Highlights main discoveries and contributions
- 📈 **Methodology Overview**: Detailed explanation of research methods
- 🎯 **Results Summary**: Comprehensive analysis of findings

### Advanced Features
- 🔄 **Automatic Language Detection**: Works with any source language
- 📝 **Natural Language Output**: Human-like, fluent summaries
- 🗂️ **Multiple Output Formats**: JSON (structured) + TXT (readable)
- 📋 **Detailed Logging**: JSON and text logs for tracking
- ⚡ **Smart Chunking**: Handles large documents efficiently
- 💾 **Progress Tracking**: Real-time processing updates

## 🚀 Quick Start

### 1. Installation
```bash
# Clone or download the project
cd document_summarizer_bot

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR (see INSTALLATION_GUIDE.md)
```

### 2. Configuration
```bash
# Create .env file
echo "OPENROUTER_API_KEY=your_key_here" > .env

# Update Tesseract path in config.py
# Windows: C:\Program Files\Tesseract-OCR\tesseract.exe
# Linux: /usr/bin/tesseract
# macOS: /usr/local/bin/tesseract
```

### 3. Get API Key
1. Sign up at [OpenRouter](https://openrouter.ai/)
2. Create API key
3. Add to `.env` file

### 4. Run
```bash
# Basic usage
python main.py document.pdf en

# Bengali document
python main.py বই.pdf bn

# Academic paper
python main.py research.pdf en --academic
```

## 📖 Usage

### Command Line Arguments
```bash
python main.py <file_path> [language] [--academic]
```

**Parameters:**
- `file_path`: Path to PDF or DOCX file (required)
- `language`: Target language - `en`, `bn`, or `ar` (default: `en`)
- `--academic`: Flag for academic paper mode (optional)

### Examples

#### General Documents
```bash
# English book
python main.py "Book_Title.pdf" en

# Bengali article
python main.py "নিবন্ধ.pdf" bn

# Arabic document
python main.py "كتاب.pdf" ar

# DOCX file
python main.py "report.docx" en
```

#### Academic Papers
```bash
# Research paper
python main.py "ML_Paper.pdf" en --academic

# Journal article in Bengali
python main.py "গবেষণা_পত্র.pdf" bn --academic
```

## 📊 Output

### Generated Files

**In `outputs/` folder:**
1. `filename_lang_timestamp.json` - Structured data
2. `filename_lang_timestamp.txt` - Human-readable summary

**In `logs/` folder:**
1. `filename_timestamp.log` - Processing log
2. `filename_timestamp.json` - Structured log data

### Output Contents

**General Document:**
- ✅ Full document summary (elaborate)
- ✅ Chapter-wise summaries (each chapter detailed)
- ✅ Suggestions and insights
- ✅ Metadata (word count, chapters, etc.)

**Academic Paper:**
- ✅ Overall research summary
- ✅ Section summaries (Abstract, Intro, Methods, Results, Conclusion)
- ✅ Key findings extraction
- ✅ Methodology detailed explanation
- ✅ Research contributions

## 🏗️ Architecture

### Project Structure
```
document_summarizer_bot/
├── main.py                  # Main application
├── config.py               # Configuration settings
├── document_processor.py   # PDF/DOCX processing + OCR
├── summarizer.py          # AI summarization engine
├── academic_parser.py     # Academic paper processor
├── logger_module.py       # Logging system
├── requirements.txt       # Python dependencies
├── .env                  # API key (create this)
├── logs/                 # Processing logs
└── outputs/              # Generated summaries
```

### Technology Stack
- **AI**: OpenRouter API (Claude, GPT, Gemini, etc.)
- **OCR**: Tesseract (Bengali, English, Arabic)
- **PDF**: PyPDF2, pdf2image
- **DOCX**: python-docx
- **Language**: Python 3.8+

## 🎯 Use Cases

1. **Students**: Summarize textbooks for exam prep
2. **Researchers**: Quick review of academic papers
3. **Readers**: Get book summaries before reading
4. **Professionals**: Analyze reports and documents
5. **Translators**: Understand content before translating
6. **Authors**: Analyze book structure and content
7. **Journalists**: Summarize long articles

## 💰 Cost

OpenRouter charges per token usage:
- **Small document** (50 pages): ~$0.10 - $0.30
- **Medium book** (300 pages): ~$0.50 - $2.00
- **Academic paper**: ~$0.10 - $0.50

Pricing varies by model selected. Claude 3.5 Sonnet recommended for quality.

## 🔧 Configuration

### Supported AI Models
Edit `MODEL_NAME` in `config.py`:
- `anthropic/claude-3.5-sonnet` (recommended)
- `google/gemini-pro-1.5`
- `openai/gpt-4-turbo`
- `meta-llama/llama-3.1-70b-instruct`

### Summary Detail Level
Currently set to **"elaborate"** (comprehensive, detailed summaries).

### Chunk Size
Default: 12,000 characters per chunk. Increase for better context, decrease for faster processing.

## 🌍 Language Support

### Input Languages
- Any language (AI model dependent)
- OCR supports: Bengali, English, Arabic, and many more

### Output Languages
- **Bengali (বাংলা)**: Natural, fluent summaries
- **English**: Clear, comprehensive summaries
- **Arabic (العربية)**: Detailed, well-structured summaries

## 🐛 Troubleshooting

### Common Issues

**"Tesseract not found"**
- Update `TESSERACT_CMD` path in `config.py`
- Verify installation: `tesseract --version`

**"API key not found"**
- Create `.env` file with your OpenRouter API key
- Format: `OPENROUTER_API_KEY=sk-or-...`

**"Out of memory"**
- Reduce `MAX_CHUNK_SIZE` in `config.py`
- Process smaller documents or sections

**"OCR not working for Bengali/Arabic"**
- Reinstall Tesseract with language packs
- Verify: `tesseract --list-langs`

**"Summary too brief"**
- Already using "elaborate" mode
- Summaries are comprehensive by design

## 📝 Requirements

### System Requirements
- Python 3.8+
- 4GB RAM minimum (8GB+ for large documents)
- Internet connection (for API calls)

### Software Dependencies
- Tesseract OCR
- Poppler (for PDF to image)
- Python packages (see requirements.txt)

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional language support
- More AI model options
- UI/web interface
- Batch processing enhancements
- Custom summary templates

## 📄 License

Open source - feel free to use and modify!

## 🆘 Support

1. Check `INSTALLATION_GUIDE.md` for setup help
2. See `USAGE_EXAMPLES.md` for practical examples
3. Review logs in `logs/` folder for debugging
4. Check OpenRouter status if API issues

## 🎓 Documentation

- **INSTALLATION_GUIDE.md**: Complete setup instructions
- **USAGE_EXAMPLES.md**: Practical examples and use cases
- **README.md** (this file): Overview and quick start

## 🔮 Roadmap

- [ ] Web interface
- [ ] Batch processing mode
- [ ] Custom summary templates
- [ ] Audio summarization
- [ ] Multiple AI model comparison
- [ ] Summary quality metrics
- [ ] Epub support
- [ ] Cloud deployment guide

## ⭐ Features in Detail

### Elaborate Summaries
Unlike brief summaries, this bot generates **comprehensive, detailed summaries** that:
- Include all major points and concepts
- Explain context and significance
- Maintain logical flow of the original
- Use natural, fluent language
- Provide enough detail to understand without reading the original

### Chapter-wise Processing
- Automatically detects chapters
- Summarizes each chapter separately
- Generates overall document summary
- Tracks word count per chapter

### Academic Mode
- Detects research paper structure
- Identifies key sections
- Extracts methodology details
- Summarizes experimental results
- Highlights contributions and findings

### Logging System
- Real-time progress tracking
- Detailed event logging
- API usage statistics
- Error tracking
- Processing time metrics

## 🎉 Getting Started

1. **Read**: INSTALLATION_GUIDE.md
2. **Install**: Dependencies and Tesseract
3. **Configure**: API key and paths
4. **Test**: `python main.py sample.pdf en`
5. **Explore**: Check outputs folder

---

**Made with ❤️ for multilingual document understanding**

*Powered by OpenRouter AI & Tesseract OCR*