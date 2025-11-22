# summarizer.py
import requests
import json
from config import Config
from logger_module import DocumentLogger

class Summarizer:
    """AI-powered summarization using OpenRouter API"""
    
    def __init__(self, language='en', logger=None):
        self.language = language
        self.logger = logger
        self.api_key = Config.OPENROUTER_API_KEY
        self.base_url = Config.OPENROUTER_BASE_URL
        self.model = Config.MODEL_NAME
        
        if not self.api_key:
            raise ValueError("OpenRouter API key not found. Please set it in .env file")
    
    def _make_api_call(self, messages, max_tokens=None):
        """Make API call to OpenRouter"""
        if max_tokens is None:
            max_tokens = Config.MAX_TOKENS
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Document Summarizer Bot"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": Config.TEMPERATURE
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            # Log API call
            if self.logger:
                tokens_used = result.get('usage', {}).get('total_tokens', 0)
                self.logger.log_api_call(self.model, tokens_used)
            
            return result['choices'][0]['message']['content']
        
        except requests.exceptions.RequestException as e:
            if self.logger:
                self.logger.log_event(f"API call failed: {str(e)}", "ERROR")
            raise Exception(f"API call failed: {str(e)}")
    
    def summarize_chapter(self, chapter_data):
        """Generate elaborate summary for a single chapter"""
        chapter_title = chapter_data.get('title', 'Untitled')
        chapter_content = chapter_data.get('content', '')
        
        # Split into chunks if too long
        chunks = self._split_into_chunks(chapter_content)
        
        if len(chunks) == 1:
            summary = self._summarize_single_chunk(chapter_title, chunks[0], "chapter")
        else:
            # Summarize each chunk then combine
            chunk_summaries = []
            for i, chunk in enumerate(chunks):
                if self.logger:
                    self.logger.log_event(f"Summarizing chunk {i+1}/{len(chunks)} of chapter: {chapter_title}", "DEBUG")
                chunk_summary = self._summarize_single_chunk(f"{chapter_title} (Part {i+1})", chunk, "section")
                chunk_summaries.append(chunk_summary)
            
            # Combine chunk summaries
            summary = self._combine_summaries(chapter_title, chunk_summaries)
        
        if self.logger:
            self.logger.log_summary_generated(
                f"Chapter: {chapter_title}",
                len(summary.split()),
                self.language
            )
        
        return summary
    
    def summarize_full_document(self, chapters, metadata):
        """Generate elaborate summary for entire document"""
        # If document is small enough, summarize directly
        full_text = "\n\n".join([ch.get('content', '') for ch in chapters])
        
        if len(full_text) < Config.MAX_CHUNK_SIZE:
            summary = self._summarize_document_direct(full_text, metadata)
        else:
            # Use chapter summaries to create document summary
            chapter_summaries = []
            for chapter in chapters:
                summary = self.summarize_chapter(chapter)
                chapter_summaries.append({
                    'title': chapter.get('title', 'Untitled'),
                    'summary': summary
                })
            
            summary = self._synthesize_document_summary(chapter_summaries, metadata)
        
        if self.logger:
            self.logger.log_summary_generated(
                "Full Document",
                len(summary.split()),
                self.language
            )
        
        return summary
    
    def generate_suggestions(self, document_summary, metadata):
        """Generate suggestions based on document content"""
        lang_instruction = Config.LANGUAGE_INSTRUCTIONS.get(self.language, '')
        
        prompt = f"""{lang_instruction}

Based on this document summary, provide comprehensive suggestions and insights:

Document: {metadata.get('title', 'Unknown')}

Summary:
{document_summary}

Please provide:
1. Key takeaways and main insights
2. Practical applications of the content
3. Related topics the reader might want to explore
4. Questions for deeper understanding
5. Action items or next steps based on the content

Make your suggestions detailed, actionable, and valuable."""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        suggestions = self._make_api_call(messages)
        
        if self.logger:
            self.logger.log_event("Suggestions generated", "INFO")
        
        return suggestions
    
    def _summarize_single_chunk(self, title, content, content_type="chapter"):
        """Summarize a single chunk of text"""
        lang_instruction = Config.LANGUAGE_INSTRUCTIONS.get(self.language, '')
        
        prompt = f"""{lang_instruction}

Please provide an ELABORATE and DETAILED summary of the following {content_type}.

{content_type.title()}: {title}

Content:
{content}

Requirements for the summary:
1. Make it COMPREHENSIVE and DETAILED - readers should understand the full scope and depth of the content
2. Include ALL major points, concepts, arguments, and conclusions
3. Explain the context and significance of key ideas
4. Maintain the logical flow and structure of the original
5. Use clear, natural, and fluent language
6. Include specific details, examples, and data mentioned in the text
7. The summary should be substantial enough that someone reading only the summary can grasp the complete message

This is NOT a brief summary - it should be elaborate and thorough."""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        return self._make_api_call(messages, max_tokens=4000)
    
    def _combine_summaries(self, chapter_title, chunk_summaries):
        """Combine multiple chunk summaries into one coherent chapter summary"""
        lang_instruction = Config.LANGUAGE_INSTRUCTIONS.get(self.language, '')
        
        combined_text = "\n\n".join([f"Part {i+1}:\n{summary}" for i, summary in enumerate(chunk_summaries)])
        
        prompt = f"""{lang_instruction}

The following are summaries of different parts of a chapter titled "{chapter_title}". Please combine them into ONE comprehensive, flowing, and elaborate summary.

{combined_text}

Requirements:
1. Create a single, coherent narrative that flows naturally
2. Eliminate redundancy but preserve all important information
3. Maintain the elaborate and detailed nature of the summaries
4. Ensure logical progression of ideas
5. Keep it comprehensive and substantial"""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        return self._make_api_call(messages, max_tokens=4000)
    
    def _summarize_document_direct(self, full_text, metadata):
        """Directly summarize a complete document"""
        lang_instruction = Config.LANGUAGE_INSTRUCTIONS.get(self.language, '')
        title = metadata.get('title', 'Unknown Document')
        
        prompt = f"""{lang_instruction}

Please provide an ELABORATE and COMPREHENSIVE summary of this entire document.

Document Title: {title}

Full Content:
{full_text}

Requirements:
1. Provide a thorough overview of the ENTIRE document
2. Include all major themes, arguments, and conclusions
3. Explain the structure and flow of the document
4. Highlight key insights and important details
5. Make it detailed enough that a reader can understand the complete scope without reading the original
6. Use natural, fluent language
7. This should be a substantial, elaborate summary"""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        return self._make_api_call(messages, max_tokens=4000)
    
    def _synthesize_document_summary(self, chapter_summaries, metadata):
        """Synthesize document summary from chapter summaries"""
        lang_instruction = Config.LANGUAGE_INSTRUCTIONS.get(self.language, '')
        title = metadata.get('title', 'Unknown Document')
        
        summaries_text = "\n\n".join([
            f"Chapter: {ch['title']}\nSummary: {ch['summary']}"
            for ch in chapter_summaries
        ])
        
        prompt = f"""{lang_instruction}

Based on these chapter summaries, create a COMPREHENSIVE summary of the entire document.

Document: {title}
Total Chapters: {len(chapter_summaries)}

Chapter Summaries:
{summaries_text}

Requirements:
1. Provide an elaborate overview of the entire document
2. Show how chapters connect and build upon each other
3. Identify overarching themes and main arguments
4. Include key insights from all chapters
5. Explain the document's structure and progression
6. Make it comprehensive and detailed
7. Ensure readers can understand the complete scope of the document"""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        return self._make_api_call(messages, max_tokens=4000)
    
    def _split_into_chunks(self, text):
        """Split text into manageable chunks"""
        if len(text) <= Config.MAX_CHUNK_SIZE:
            return [text]
        
        chunks = []
        paragraphs = text.split('\n\n')
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < Config.MAX_CHUNK_SIZE:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks