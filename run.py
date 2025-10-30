# run.py
from Main import DocumentSummarizer
import os
from dotenv import load_dotenv

load_dotenv()
bot = DocumentSummarizer(api_key=os.getenv("ANTHROPIC_API_KEY"), output_lang='en')
result = bot.summarise("sample.pdf", doc_type='research')
print(f"Summary saved: {result['json_path']}")