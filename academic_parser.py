# academic_parser.py
import re
from config import Config
from summarizer import Summarizer

class AcademicPaperParser:
    """Parse and summarize academic papers (IEEE, Springer, etc.)"""
    
    def __init__(self, text, language='en', logger=None):
        self.text = text
        self.language = language
        self.logger = logger
        self.summarizer = Summarizer(language, logger)
        self.sections = {}
    
    def parse(self):
        """Parse academic paper into sections"""
        # Detect if this is an academic paper
        if not self._is_academic_paper():
            if self.logger:
                self.logger.log_event("Document does not appear to be an academic paper", "INFO")
            return None
        
        # Extract sections
        self.sections = self._extract_sections()
        
        if self.logger:
            self.logger.log_event(f"Academic paper parsed: {len(self.sections)} sections found", "INFO")
        
        return self.sections
    
    def summarize_sections(self):
        """Generate summaries for each academic section"""
        if not self.sections:
            self.parse()
        
        if not self.sections:
            return None
        
        summaries = {}
        
        for section_name, content in self.sections.items():
            if self.logger:
                self.logger.log_event(f"Summarizing section: {section_name}", "INFO")
            
            summary = self._summarize_academic_section(section_name, content)
            summaries[section_name] = summary
        
        return summaries
    
    def generate_academic_report(self):
        """Generate comprehensive academic paper report"""
        summaries = self.summarize_sections()
        
        if not summaries:
            return None
        
        report = {
            'sections': summaries,
            'overall_summary': self._generate_overall_summary(summaries),
            'key_findings': self._extract_key_findings(summaries),
            'methodology_summary': summaries.get('methodology', summaries.get('methods', 'Not found')),
            'results_summary': summaries.get('results', summaries.get('findings', 'Not found')),
            'conclusion': summaries.get('conclusion', 'Not found')
        }
        
        return report
    
    def _is_academic_paper(self):
        """Detect if document is an academic paper"""
        academic_indicators = [
            'abstract', 'introduction', 'methodology', 'results',
            'conclusion', 'references', 'keywords', 'doi',
            'ieee', 'springer', 'elsevier', 'acm', 'journal'
        ]
        
        text_lower = self.text.lower()
        matches = sum(1 for indicator in academic_indicators if indicator in text_lower)
        
        return matches >= 3
    
    def _extract_sections(self):
        """Extract sections from academic paper"""
        sections = {}
        
        # Common academic section patterns
        section_patterns = [
            r'(?:^|\n)(?:I{1,3}|[IVX]+|\d+)\.\s*([A-Z][A-Z\s]+)(?:\n)',  # I. INTRODUCTION
            r'(?:^|\n)(\d+\.\d*)\s+([A-Z][A-Za-z\s]+)(?:\n)',  # 1.1 Introduction
            r'(?:^|\n)([A-Z][A-Z\s]{2,})(?:\n)',  # ABSTRACT
        ]
        
        # Try to find section headers
        section_positions = []
        for pattern in section_patterns:
            matches = re.finditer(pattern, self.text, re.MULTILINE)
            for match in matches:
                section_name = match.group(1) if len(match.groups()) == 1 else match.group(2)
                section_name = section_name.strip().lower()
                
                # Check if it's a known academic section
                for known_section in Config.ACADEMIC_SECTIONS:
                    if known_section in section_name:
                        section_positions.append({
                            'name': known_section.title(),
                            'start': match.start(),
                            'matched_text': section_name
                        })
                        break
        
        # Remove duplicates and sort by position
        seen_names = set()
        unique_positions = []
        for pos in sorted(section_positions, key=lambda x: x['start']):
            if pos['name'] not in seen_names:
                unique_positions.append(pos)
                seen_names.add(pos['name'])
        
        # Extract content for each section
        for i, section in enumerate(unique_positions):
            end_pos = unique_positions[i+1]['start'] if i+1 < len(unique_positions) else len(self.text)
            content = self.text[section['start']:end_pos].strip()
            sections[section['name']] = content
        
        # If no sections found, try simpler extraction
        if not sections:
            sections = self._simple_section_extraction()
        
        return sections
    
    def _simple_section_extraction(self):
        """Simple section extraction fallback"""
        sections = {}
        text_lower = self.text.lower()
        
        # Find abstract
        abstract_match = re.search(r'abstract[:\s]+(.*?)(?=introduction|keywords|\n\n[A-Z])', text_lower, re.DOTALL | re.IGNORECASE)
        if abstract_match:
            start = abstract_match.start()
            end = abstract_match.end()
            sections['Abstract'] = self.text[start:end]
        
        # Find introduction
        intro_match = re.search(r'introduction[:\s]+(.*?)(?=related work|methodology|methods|\n\n[A-Z])', text_lower, re.DOTALL | re.IGNORECASE)
        if intro_match:
            start = intro_match.start()
            end = intro_match.end()
            sections['Introduction'] = self.text[start:end]
        
        # Find methodology/methods
        method_match = re.search(r'(?:methodology|methods)[:\s]+(.*?)(?=results|experiments|implementation|\n\n[A-Z])', text_lower, re.DOTALL | re.IGNORECASE)
        if method_match:
            start = method_match.start()
            end = method_match.end()
            sections['Methodology'] = self.text[start:end]
        
        # Find results
        results_match = re.search(r'results[:\s]+(.*?)(?=discussion|conclusion|\n\n[A-Z])', text_lower, re.DOTALL | re.IGNORECASE)
        if results_match:
            start = results_match.start()
            end = results_match.end()
            sections['Results'] = self.text[start:end]
        
        # Find conclusion
        conclusion_match = re.search(r'conclusion[:\s]+(.*?)(?=references|acknowledgment|\Z)', text_lower, re.DOTALL | re.IGNORECASE)
        if conclusion_match:
            start = conclusion_match.start()
            end = conclusion_match.end()
            sections['Conclusion'] = self.text[start:end]
        
        return sections
    
    def _summarize_academic_section(self, section_name, content):
        """Summarize a specific academic section"""
        lang_instruction = Config.LANGUAGE_INSTRUCTIONS.get(self.language, '')
        
        # Customize prompt based on section type
        section_instructions = {
            'Abstract': 'Explain the research problem, approach, and key findings.',
            'Introduction': 'Describe the background, motivation, and research objectives.',
            'Methodology': 'Explain the research methods, techniques, and experimental setup in detail.',
            'Methods': 'Explain the research methods, techniques, and experimental setup in detail.',
            'Results': 'Describe the findings, data, and outcomes with specific details.',
            'Conclusion': 'Summarize the main conclusions, contributions, and future work.',
            'Discussion': 'Explain the interpretation of results and their implications.'
        }
        
        specific_instruction = section_instructions.get(section_name, 'Provide a comprehensive summary of this section.')
        
        prompt = f"""{lang_instruction}

Provide an ELABORATE and DETAILED summary of this academic paper section.

Section: {section_name}

Content:
{content}

Instructions:
{specific_instruction}

Requirements:
1. Be thorough and comprehensive
2. Include all important details, methods, findings, and data
3. Explain technical concepts clearly
4. Maintain academic precision
5. Use natural, fluent language
6. Make it detailed enough for academic understanding"""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        return self.summarizer._make_api_call(messages, max_tokens=3000)
    
    def _generate_overall_summary(self, section_summaries):
        """Generate overall academic paper summary"""
        lang_instruction = Config.LANGUAGE_INSTRUCTIONS.get(self.language, '')
        
        summaries_text = "\n\n".join([
            f"{section}:\n{summary}"
            for section, summary in section_summaries.items()
        ])
        
        prompt = f"""{lang_instruction}

Based on these section summaries, provide a comprehensive overall summary of this academic paper.

Section Summaries:
{summaries_text}

Provide:
1. Research objective and problem statement
2. Methodology overview
3. Key findings and results
4. Main contributions
5. Conclusions and implications

Make it comprehensive and academically precise."""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        return self.summarizer._make_api_call(messages)
    
    def _extract_key_findings(self, section_summaries):
        """Extract key findings from the paper"""
        results = section_summaries.get('Results', '')
        conclusion = section_summaries.get('Conclusion', '')
        
        combined = f"Results:\n{results}\n\nConclusion:\n{conclusion}"
        
        lang_instruction = Config.LANGUAGE_INSTRUCTIONS.get(self.language, '')
        
        prompt = f"""{lang_instruction}

Extract and list the key findings from this academic paper:

{combined}

Provide a clear, bullet-pointed list of the main findings and contributions."""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        return self.summarizer._make_api_call(messages)