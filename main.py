# main.py
import json
import sys
from pathlib import Path
from datetime import datetime
from config import Config
from document_processor import DocumentProcessor
from summarizer import Summarizer
from academic_parser import AcademicPaperParser
from logger_module import DocumentLogger

class DocumentSummarizerBot:
    """Main bot for document summarization"""
    
    def __init__(self):
        # Validate configuration
        Config.validate()
        self.logger = None
    
    def process_document(self, file_path, language='en', is_academic=False):
        """
        Main method to process a document
        
        Args:
            file_path: Path to PDF or DOCX file
            language: Target language ('en', 'bn', 'ar')
            is_academic: Whether to treat as academic paper
        """
        # Initialize logger
        file_name = Path(file_path).stem
        self.logger = DocumentLogger(file_name)
        
        try:
            print(f"\n{'='*60}")
            print(f"📚 Document Summarizer Bot")
            print(f"{'='*60}\n")
            
            # Step 1: Process Document
            print(f"📄 Processing document: {file_path}")
            print(f"🌐 Target language: {Config.LANGUAGE_NAMES[language]}")
            print(f"🔍 Academic paper mode: {'Yes' if is_academic else 'No'}\n")
            
            processor = DocumentProcessor(file_path, language, self.logger)
            doc_data = processor.process()
            
            print(f"✅ Document processed successfully!")
            print(f"   📊 Total characters: {doc_data['metadata']['total_characters']:,}")
            print(f"   📝 Total words: {doc_data['metadata']['total_words']:,}")
            print(f"   📑 Chapters found: {len(doc_data['chapters'])}\n")
            
            # Step 2: Initialize Summarizer
            summarizer = Summarizer(language, self.logger)
            
            # Step 3: Check if academic paper
            if is_academic:
                print("🎓 Processing as academic paper...\n")
                result = self._process_academic_paper(
                    doc_data['text'],
                    doc_data['metadata'],
                    summarizer
                )
            else:
                print("📖 Processing as general document...\n")
                result = self._process_general_document(
                    doc_data['chapters'],
                    doc_data['metadata'],
                    summarizer
                )
            
            # Step 4: Save Results
            output_file = self._save_results(result, file_name, language)
            
            # Step 5: Finalize Logger
            log_file = self.logger.finalize()
            
            print(f"\n{'='*60}")
            print(f"✨ Processing Complete!")
            print(f"{'='*60}")
            print(f"📁 Results saved to: {output_file}")
            print(f"📋 Log saved to: {log_file}")
            print(f"\n⏱️  Total time: {self.logger.json_data['duration_seconds']:.2f} seconds\n")
            
            return result
            
        except Exception as e:
            if self.logger:
                self.logger.log_event(f"Critical error: {str(e)}", "CRITICAL")
                self.logger.finalize()
            
            print(f"\n❌ Error: {str(e)}")
            raise
    
    def _process_general_document(self, chapters, metadata, summarizer):
        """Process general document (book, article, etc.)"""
        result = {
            'metadata': metadata,
            'type': 'general_document',
            'chapter_summaries': [],
            'full_summary': '',
            'suggestions': ''
        }
        
        # Summarize each chapter
        print("📝 Generating chapter summaries...\n")
        for i, chapter in enumerate(chapters):
            print(f"   [{i+1}/{len(chapters)}] Summarizing: {chapter['title']}")
            summary = summarizer.summarize_chapter(chapter)
            result['chapter_summaries'].append({
                'chapter_number': chapter['number'],
                'chapter_title': chapter['title'],
                'word_count': chapter['word_count'],
                'summary': summary
            })
        
        print("\n✅ All chapters summarized!\n")
        
        # Generate full document summary
        print("📚 Generating full document summary...\n")
        result['full_summary'] = summarizer.summarize_full_document(chapters, metadata)
        print("✅ Full summary generated!\n")
        
        # Generate suggestions
        print("💡 Generating suggestions and insights...\n")
        result['suggestions'] = summarizer.generate_suggestions(
            result['full_summary'],
            metadata
        )
        print("✅ Suggestions generated!\n")
        
        return result
    
    def _process_academic_paper(self, text, metadata, summarizer):
        """Process academic paper"""
        result = {
            'metadata': metadata,
            'type': 'academic_paper',
            'sections': {},
            'academic_report': {}
        }
        
        # Parse academic paper
        print("🔬 Parsing academic paper sections...\n")
        parser = AcademicPaperParser(text, summarizer.language, self.logger)
        sections = parser.parse()
        
        if sections:
            print(f"✅ Found {len(sections)} academic sections\n")
            
            # Generate academic report
            print("📊 Generating comprehensive academic report...\n")
            report = parser.generate_academic_report()
            result['academic_report'] = report
            
            print("✅ Academic report generated!\n")
        else:
            print("⚠️  Not detected as academic paper, processing as general document...\n")
            # Fall back to general processing
            processor = DocumentProcessor(Path(metadata['file_name']), summarizer.language, self.logger)
            doc_data = processor.process()
            return self._process_general_document(
                doc_data['chapters'],
                metadata,
                summarizer
            )
        
        return result
    
    def _save_results(self, result, file_name, language):
        """Save processing results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = Config.OUTPUT_DIR / f"{file_name}_{language}_{timestamp}.json"
        
        # Also create a readable text file
        text_file = Config.OUTPUT_DIR / f"{file_name}_{language}_{timestamp}.txt"
        
        # Save JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Save readable text
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(f"{'='*70}\n")
            f.write(f"Document Summary Report\n")
            f.write(f"{'='*70}\n\n")
            
            f.write(f"Document: {result['metadata'].get('title', 'Unknown')}\n")
            f.write(f"File: {result['metadata']['file_name']}\n")
            f.write(f"Language: {Config.LANGUAGE_NAMES[language]}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            if result['type'] == 'general_document':
                f.write(f"{'='*70}\n")
                f.write(f"FULL DOCUMENT SUMMARY\n")
                f.write(f"{'='*70}\n\n")
                f.write(result['full_summary'])
                f.write("\n\n")
                
                f.write(f"{'='*70}\n")
                f.write(f"CHAPTER-WISE SUMMARIES\n")
                f.write(f"{'='*70}\n\n")
                
                for chapter_summary in result['chapter_summaries']:
                    f.write(f"\n{'-'*70}\n")
                    f.write(f"Chapter {chapter_summary['chapter_number']}: {chapter_summary['chapter_title']}\n")
                    f.write(f"{'-'*70}\n\n")
                    f.write(chapter_summary['summary'])
                    f.write("\n\n")
                
                f.write(f"{'='*70}\n")
                f.write(f"SUGGESTIONS AND INSIGHTS\n")
                f.write(f"{'='*70}\n\n")
                f.write(result['suggestions'])
                
            elif result['type'] == 'academic_paper':
                report = result['academic_report']
                
                f.write(f"{'='*70}\n")
                f.write(f"OVERALL SUMMARY\n")
                f.write(f"{'='*70}\n\n")
                f.write(report['overall_summary'])
                f.write("\n\n")
                
                f.write(f"{'='*70}\n")
                f.write(f"KEY FINDINGS\n")
                f.write(f"{'='*70}\n\n")
                f.write(report['key_findings'])
                f.write("\n\n")
                
                f.write(f"{'='*70}\n")
                f.write(f"SECTION SUMMARIES\n")
                f.write(f"{'='*70}\n\n")
                
                for section_name, summary in report['sections'].items():
                    f.write(f"\n{'-'*70}\n")
                    f.write(f"{section_name}\n")
                    f.write(f"{'-'*70}\n\n")
                    f.write(summary)
                    f.write("\n\n")
        
        return output_file

def main():
    """Main entry point"""
    print("\n🤖 Document Summarizer Bot - OpenRouter Edition")
    print("=" * 70)
    
    # Check if file path provided
    if len(sys.argv) < 2:
        print("\nUsage: python main.py <file_path> [language] [--academic]")
        print("\nLanguages: en (English), bn (Bengali), ar (Arabic)")
        print("Add --academic flag for academic papers\n")
        print("Example: python main.py document.pdf bn")
        print("Example: python main.py paper.pdf en --academic\n")
        return
    
    file_path = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] in ['en', 'bn', 'ar'] else 'en'
    is_academic = '--academic' in sys.argv
    
    # Validate file exists
    if not Path(file_path).exists():
        print(f"\n❌ Error: File not found: {file_path}\n")
        return
    
    # Create bot and process
    bot = DocumentSummarizerBot()
    
    try:
        result = bot.process_document(file_path, language, is_academic)
        print("\n✨ Success! Check the outputs folder for results.\n")
        
    except Exception as e:
        print(f"\n❌ Processing failed: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()