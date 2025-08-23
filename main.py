#!/usr/bin/env python3
"""
AtCoder Problem HTML to Markdown Converter
Converts AtCoder problem HTML pages to clean markdown format
"""

import re
import sys
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from html.parser import HTMLParser
from bs4 import BeautifulSoup, Tag


class AtCoderProblemParser:
    def __init__(self, html_content: str, language: str = 'ja'):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.markdown_content = []
        self.language = language
        
    def parse(self) -> str:
        """Parse the HTML and convert to markdown"""
        # Extract problem title
        title = self._extract_title()
        if title:
            self.markdown_content.append(f"# {title}\n")
        
        # Extract time and memory limits
        limits = self._extract_limits()
        if limits:
            self.markdown_content.append(f"**Time Limit:** {limits['time']}")
            self.markdown_content.append(f"**Memory Limit:** {limits['memory']}\n")
        
        # Extract problem content based on language
        task_statement = self.soup.find('div', id='task-statement')
        if task_statement:
            # Find content for specified language
            lang_content = task_statement.find('span', class_=f'lang-{self.language}')
            if lang_content:
                self._parse_problem_content(lang_content)
            else:
                # Fallback to any content found
                self._parse_problem_content(task_statement)
        
        return '\n'.join(self.markdown_content)
    
    def _extract_title(self) -> Optional[str]:
        """Extract problem title"""
        title_tag = self.soup.find('title')
        if title_tag and title_tag.text:
            # Remove contest prefix if present
            title = title_tag.text.strip()
            return title
        
        # Fallback to h2 tag
        h2_tag = self.soup.find('span', class_='h2')
        if h2_tag:
            return h2_tag.text.strip()
        
        return None
    
    def _extract_limits(self) -> Optional[Dict[str, str]]:
        """Extract time and memory limits"""
        limits_p = self.soup.find('p', string=re.compile(r'実行時間制限|Time Limit'))
        if limits_p and limits_p.text:
            match = re.search(r'実行時間制限[：:]\s*(\d+(?:\.\d+)?\s*sec).*メモリ制限[：:]\s*(\d+\s*\w+)', limits_p.text)
            if not match:
                # Try English pattern
                match = re.search(r'Time\s+Limit[：:]\s*(\d+(?:\.\d+)?\s*sec).*Memory\s+Limit[：:]\s*(\d+\s*\w+)', limits_p.text)
            
            if match:
                return {
                    'time': match.group(1),
                    'memory': match.group(2)
                }
        
        return None
    
    def _parse_problem_content(self, content_tag: Tag):
        """Parse problem content sections"""
        # Find all sections
        sections = content_tag.find_all('section')
        if sections:
            for section in sections:
                self._parse_section(section)
        else:
            self._parse_section(content_tag)
    
    def _parse_section(self, section_tag: Tag):
        """Parse a single section"""
        for element in section_tag.children:
            if not isinstance(element, Tag):
                continue
                
            if element.name == 'h3':
                section_title = element.text.strip()
                self.markdown_content.append(f"\n## {section_title}\n")
            
            elif element.name == 'p':
                # Handle score/points
                if '配点' in element.text or 'Score' in element.text:
                    self.markdown_content.append(f"\n**{element.text.strip()}**\n")
                else:
                    # Convert variables in the text
                    text = self._convert_text_with_variables(element)
                    if text:
                        self.markdown_content.append(text)
            
            elif element.name == 'ul':
                # Convert list items
                self._parse_list(element)
                self.markdown_content.append("")
            
            elif element.name == 'pre':
                # Code blocks (input/output examples)
                code_text = element.text.strip()
                if code_text:
                    self.markdown_content.append("```")
                    self.markdown_content.append(code_text)
                    self.markdown_content.append("```\n")
            
            elif element.name == 'div':
                # Recursively parse div content
                self._parse_section(element)
    
    def _parse_list(self, ul_tag: Tag, indent_level: int = 0):
        """Parse list items with proper indentation"""
        indent = "  " * indent_level
        
        for li in ul_tag.find_all('li', recursive=False):
            # Get direct text content
            li_text = self._convert_text_with_variables(li)
            if li_text:
                self.markdown_content.append(f"{indent}- {li_text}")
            
            # Check for nested lists
            nested_ul = li.find('ul', recursive=False)
            if nested_ul:
                self._parse_list(nested_ul, indent_level + 1)
    
    def _convert_text_with_variables(self, element: Tag) -> str:
        """Convert text containing <var> tags to LaTeX format"""
        text_parts = []
        
        # Handle direct children only, stop at nested ul/ol
        for child in element.children:
            if isinstance(child, str):
                text_parts.append(child)
            elif child.name == 'var':
                # Convert variable to LaTeX format
                var_text = child.text.strip()
                # Handle subscripts
                var_text = re.sub(r'_(\w+)', r'_{\1}', var_text)
                text_parts.append(f"${var_text}$")
            elif child.name == 'code':
                text_parts.append(f"`{child.text.strip()}`")
            elif child.name in ['ul', 'ol']:
                # Skip nested lists - they're handled separately
                continue
            elif child.name == 'strong':
                text_parts.append(f"**{child.text.strip()}**")
            elif child.name == 'em':
                text_parts.append(f"*{child.text.strip()}*")
            else:
                # Recursively process other nested elements
                text_parts.append(self._convert_text_with_variables(child))
        
        return ''.join(text_parts).strip()


def convert_file(input_path: str, output_path: Optional[str] = None, language: str = 'ja') -> None:
    """Convert an AtCoder HTML file to markdown"""
    input_file = Path(input_path)
    
    if not input_file.exists():
        print(f"Error: File '{input_path}' not found")
        sys.exit(1)
    
    # Read HTML content
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse and convert
    parser = AtCoderProblemParser(html_content, language)
    markdown_content = parser.parse()
    
    # Determine output path
    if output_path is None:
        output_path = input_file.with_suffix('.md')
    else:
        output_path = Path(output_path)
    
    # Write markdown file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"Successfully converted '{input_path}' to '{output_path}'")
    print(f"Language: {language}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert AtCoder problem HTML to Markdown format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python atcoder_to_markdown.py problem.html
  python atcoder_to_markdown.py problem.html output.md
  python atcoder_to_markdown.py problem.html -l en
  python atcoder_to_markdown.py problem.html output.md --language en
'''
    )
    
    parser.add_argument('input_html', help='Path to the input HTML file')
    parser.add_argument('output_md', nargs='?', help='Path to the output Markdown file (optional)')
    parser.add_argument('-l', '--language', default='ja', choices=['ja', 'en'],
                        help='Language to extract (default: ja)')
    
    args = parser.parse_args()
    
    convert_file(args.input_html, args.output_md, args.language)


if __name__ == "__main__":
    main()