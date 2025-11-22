# Document Summarizer Bot - Installation Guide

## 📋 Prerequisites

### 1. Python Installation
- Python 3.8 or higher
- Download from: https://www.python.org/downloads/

### 2. Tesseract OCR Installation

#### Windows:
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer
3. During installation, select language data for:
   - English (eng)
   - Bengali (ben)
   - Arabic (ara)
4. Note the installation path (usually `C:\Program Files\Tesseract-OCR`)

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-ben  # Bengali
sudo apt-get install tesseract-ocr-ara  # Arabic
```

#### macOS:
```bash
brew install tesseract
brew install tesseract-lang  # All languages
```

### 3. Poppler (for PDF to Image conversion)

#### Windows:
1. Download from: http://blog.alivate.com.au/poppler-windows/
2. Extract to `C:\Program Files\poppler`
3. Add `C:\Program Files\poppler\bin` to PATH

#### Linux:
```bash
sudo apt-get install poppler-utils
```

#### macOS:
```bash
brew install poppler
```

## 🚀 Installation Steps

### Step 1: Create Project Directory
```bash
mkdir document_summarizer_bot
cd document_summarizer_bot
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Get OpenRouter API Key
1. Go to: https://openrouter.ai/
2. Sign up for an account
3. Navigate to Keys section
4. Create a new API key
5. Copy the key

### Step 5: Configure Environment
Create a `.env` file in the project root:
```bash
OPENROUTER_API_KEY=your_actual_api_key_here
OPENROUTER_SITE_URL=http://localhost:3000
OPENROUTER_APP_NAME=DocumentSummarizerBot
```

### Step 6: Update Tesseract Path
Edit `config.py` and update the `TESSERACT_CMD` path:

**Windows:**
```python
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**Linux:**
```python
TESSERACT_CMD = '/usr/bin/tesseract'
```

**macOS:**
```python
TESSERACT_CMD = '/usr/local/bin/tesseract'
```

### Step 7: Create Required Directories
```bash
mkdir logs
mkdir outputs
```

## 📁 Project Structure
```
document_summarizer_bot/
├── main.py
├── config.py
├── document_processor.py
├── summarizer.py
├── academic_parser.py
├── logger_module.py
├── requirements.txt
├── .env
├── logs/
└── outputs/
```

## 🧪 Testing Installation

### Test 1: Verify Tesseract
```bash
tesseract --version
tesseract --list-langs
```
Should show: ben, eng, ara in the list

### Test 2: Test Python Dependencies
```python
python -c "import pytesseract, PyPDF2, docx; print('All imports successful!')"
```

### Test 3: Run Sample Document
```bash
python main.py sample.pdf en
```

## 🎯 Usage Examples

### Basic Usage (English)
```bash
python main.py document.pdf en
```

### Bengali Document
```bash
python main.py বই.pdf bn
```

### Arabic Document
```bash
python main.py كتاب.pdf ar
```

### Academic Paper
```bash
python main.py research_paper.pdf en --academic
```

### DOCX File
```bash
python main.py article.docx bn
```

## 🔧 Troubleshooting

### Issue: "Tesseract not found"
**Solution:** Update `TESSERACT_CMD` in `config.py` with correct path

### Issue: "OpenRouter API key not found"
**Solution:** Ensure `.env` file exists with valid API key

### Issue: "PDF to image conversion failed"
**Solution:** Install Poppler and ensure it's in PATH

### Issue: "Language data not found for Bengali/Arabic"
**Solution:** Reinstall Tesseract with language packs

### Issue: "Memory error with large PDFs"
**Solution:** Reduce `MAX_CHUNK_SIZE` in `config.py`

## 💰 Cost Estimation

OpenRouter pricing varies by model:
- Claude 3.5 Sonnet: ~$3 per million input tokens, ~$15 per million output tokens
- Average book (300 pages): ~$0.50 - $2.00
- Academic paper: ~$0.10 - $0.50

Check current pricing: https://openrouter.ai/models

## 🎨 Customization

### Change AI Model
Edit `config.py`:
```python
MODEL_NAME = "google/gemini-pro-1.5"  # or any supported model
```

### Adjust Summary Detail Level
Edit `config.py`:
```python
SUMMARY_DETAIL_LEVEL = "brief"  # or "moderate", "elaborate"
MAX_CHUNK_SIZE = 15000  # Increase for longer chunks
```

### Modify Language Instructions
Edit language-specific prompts in `config.py`:
```python
LANGUAGE_INSTRUCTIONS = {
    'bn': 'Your custom Bengali instruction',
    'en': 'Your custom English instruction',
    'ar': 'Your custom Arabic instruction'
}
```

## 📊 Output Files

After processing, you'll find:

### In `outputs/` folder:
- `filename_lang_timestamp.json` - Complete results in JSON
- `filename_lang_timestamp.txt` - Human-readable summary

### In `logs/` folder:
- `filename_timestamp.log` - Detailed processing log
- `filename_timestamp.json` - Structured log data

## 🆘 Support

For issues:
1. Check logs in `logs/` folder
2. Verify all dependencies installed
3. Test Tesseract separately
4. Check OpenRouter API status

## 🔄 Updates

To update the bot:
```bash
git pull  # if using git
pip install --upgrade -r requirements.txt
```

## 📄 License

This project is open-source. Feel free to modify and distribute.

---

**Ready to use!** Start with: `python main.py your_document.pdf en`