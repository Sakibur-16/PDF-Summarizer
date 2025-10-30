<<<<<<< HEAD
# run.py
from Main import DocumentSummarizer
import os
from dotenv import load_dotenv

load_dotenv()
bot = DocumentSummarizer(api_key=os.getenv("ANTHROPIC_API_KEY"), output_lang='en')
result = bot.summarise("sample.pdf", doc_type='research')
=======
# run.py
from Main import DocumentSummarizer
import os
from dotenv import load_dotenv

load_dotenv()
bot = DocumentSummarizer(api_key=os.getenv("OPENROUTER_API_KEY"), output_lang='en')
result = bot.summarise("sample.pdf", doc_type='research')
>>>>>>> 6eba3e2c2e9d74fa056fb34225dca1ec88e4a3be
print(f"Summary saved: {result['json_path']}")