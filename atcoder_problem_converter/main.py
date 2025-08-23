#!/usr/bin/env python3
"""AtCoder Problem HTML to Markdown Converter package module."""

import re
import sys
from pathlib import Path
from typing import Optional, Dict
from bs4 import BeautifulSoup, Tag


class AtCoderProblemParser:
    def __init__(self, html_content: str, language: str = 'ja'):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.markdown_content = []
        self.language = language

    def parse(self) -> str:
        title = self._extract_title()
        if title:
            self.markdown_content.append(f"# {title}\n")
        limits = self._extract_limits()
        if limits:
            self.markdown_content.append(f"**Time Limit:** {limits['time']}")
            self.markdown_content.append(f"**Memory Limit:** {limits['memory']}\n")
        task_statement = self.soup.find('div', id='task-statement')
        if task_statement:
            lang_content = task_statement.find('span', class_=f'lang-{self.language}')
            if lang_content:
                self._parse_problem_content(lang_content)
            else:
                self._parse_problem_content(task_statement)
        return '\n'.join(self.markdown_content)

    def _extract_title(self) -> Optional[str]:
        title_tag = self.soup.find('title')
        if title_tag and title_tag.text:
            return title_tag.text.strip()
        h2_tag = self.soup.find('span', class_='h2')
        if h2_tag:
            return h2_tag.text.strip()
        return None

    def _extract_limits(self) -> Optional[Dict[str, str]]:
        limits_p = self.soup.find('p', string=re.compile(r'実行時間制限|Time Limit'))
        if limits_p and limits_p.text:
            match = re.search(r'実行時間制限[：:]\s*(\d+(?:\.\d+)?\s*sec).*メモリ制限[：:]\s*(\d+\s*\w+)', limits_p.text)
            if not match:
                match = re.search(r'Time\s+Limit[：:]\s*(\d+(?:\.\d+)?\s*sec).*Memory\s+Limit[：:]\s*(\d+\s*\w+)', limits_p.text)
            if match:
                return {'time': match.group(1), 'memory': match.group(2)}
        return None

    def _parse_problem_content(self, content_tag: Tag):
        sections = content_tag.find_all('section')
        if sections:
            for section in sections:
                self._parse_section(section)
        else:
            self._parse_section(content_tag)

    def _parse_section(self, section_tag: Tag):
        for element in section_tag.children:
            if not isinstance(element, Tag):
                continue
            if element.name == 'h3':
                self.markdown_content.append(f"\n## {element.text.strip()}\n")
            elif element.name == 'p':
                if '配点' in element.text or 'Score' in element.text:
                    self.markdown_content.append(f"\n**{element.text.strip()}**\n")
                else:
                    text = self._convert_text_with_variables(element)
                    if text:
                        self.markdown_content.append(text)
            elif element.name == 'ul':
                self._parse_list(element)
                self.markdown_content.append("")
            elif element.name == 'pre':
                code_text = element.text.strip()
                if code_text:
                    self.markdown_content.append("```")
                    self.markdown_content.append(code_text)
                    self.markdown_content.append("```\n")
            elif element.name == 'div':
                self._parse_section(element)

    def _parse_list(self, ul_tag: Tag, indent_level: int = 0):
        indent = "  " * indent_level
        for li in ul_tag.find_all('li', recursive=False):
            li_text = self._convert_text_with_variables(li)
            if li_text:
                self.markdown_content.append(f"{indent}- {li_text}")
            nested_ul = li.find('ul', recursive=False)
            if nested_ul:
                self._parse_list(nested_ul, indent_level + 1)

    def _convert_text_with_variables(self, element: Tag) -> str:
        text_parts = []
        for child in element.children:
            if isinstance(child, str):
                text_parts.append(child)
            elif child.name == 'var':
                var_text = child.text.strip()
                var_text = re.sub(r'_(\w+)', r'_{\1}', var_text)
                text_parts.append(f"${var_text}$")
            elif child.name == 'code':
                text_parts.append(f"`{child.text.strip()}`")
            elif child.name in ['ul', 'ol']:
                continue
            elif child.name == 'strong':
                text_parts.append(f"**{child.text.strip()}**")
            elif child.name == 'em':
                text_parts.append(f"*{child.text.strip()}*")
            else:
                text_parts.append(self._convert_text_with_variables(child))
        return ''.join(text_parts).strip()


def convert_file(input_path: str, output_path: Optional[str] = None, language: str = 'ja') -> None:
    input_file = Path(input_path)
    if not input_file.exists():
        print(f"Error: File '{input_path}' not found")
        sys.exit(1)
    html_content = input_file.read_text(encoding='utf-8')
    parser = AtCoderProblemParser(html_content, language)
    markdown_content = parser.parse()
    if output_path is None:
        output_file = input_file.with_suffix('.md')
    else:
        output_file = Path(output_path)
    output_file.write_text(markdown_content, encoding='utf-8')
    print(f"Successfully converted '{input_path}' to '{output_file}'")
    print(f"Language: {language}")


def _default_output_from_url(url: str) -> Path:
    tail = url.rstrip('/').rsplit('/', 1)[-1]
    # Ensure it has .md suffix
    if not tail:
        tail = 'problem'
    if not tail.endswith('.md'):
        tail += '.md'
    return Path(tail)


def convert_url(url: str, output_path: Optional[str] = None, language: str = 'ja') -> None:
    """Fetch an AtCoder problem page via HTTP(S) and convert it to Markdown.

    Parameters
    ----------
    url : str
        The full URL to the AtCoder task (e.g. https://atcoder.jp/contests/abc419/tasks/abc419_e)
    output_path : Optional[str]
        Destination markdown file path. If omitted, derive from the last path segment.
    language : str
        'ja' or 'en'
    """
    try:
        import requests  # type: ignore
    except ImportError:  # pragma: no cover - defensive
        print("Error: 'requests' package is required for URL input. Please install dependencies.", file=sys.stderr)
        sys.exit(1)

    try:
        resp = requests.get(url, timeout=10)
    except Exception as e:  # pragma: no cover - network failure path
        print(f"Error: Failed to fetch URL: {e}", file=sys.stderr)
        sys.exit(1)
    if resp.status_code != 200:
        print(f"Error: HTTP {resp.status_code} when fetching URL", file=sys.stderr)
        sys.exit(1)
    html_content = resp.text
    parser = AtCoderProblemParser(html_content, language)
    markdown_content = parser.parse()
    if output_path is None:
        output_file = _default_output_from_url(url)
    else:
        output_file = Path(output_path)
    output_file.write_text(markdown_content, encoding='utf-8')
    print(f"Successfully converted '{url}' to '{output_file}'")
    print(f"Language: {language}")


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Convert AtCoder problem HTML to Markdown format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog='''\nExamples:\n  uv run apc problem.html\n  uv run apc problem.html output.md\n  uv run apc problem.html -l en\n'''
    )
    parser.add_argument('input_html', help='Path to the input HTML file or an AtCoder problem URL')
    parser.add_argument('output_md', nargs='?', help='Path to the output Markdown file (optional)')
    parser.add_argument('-l', '--language', default='ja', choices=['ja', 'en'], help='Language to extract (default: ja)')
    args = parser.parse_args()
    # Detect URL (http/https)
    if re.match(r'^https?://', args.input_html):
        convert_url(args.input_html, args.output_md, args.language)
    else:
        convert_file(args.input_html, args.output_md, args.language)


if __name__ == '__main__':  # pragma: no cover
    main()
