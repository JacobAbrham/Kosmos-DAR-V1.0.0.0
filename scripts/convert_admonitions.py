#!/usr/bin/env python3
"""
Convert MkDocs admonitions to Docusaurus format.

MkDocs: !!! type "Title"
        content

Docusaurus: :::type Title
            content
            :::
"""

import os
import re
import glob

def convert_admonition(match):
    admonition_type = match.group(1)
    title = match.group(2) if match.group(2) else ""
    # Remove quotes from title if present
    title = title.strip('"')
    return f":::{admonition_type} {title}"

def convert_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match !!! type "title" and convert to :::type title
    pattern = r'^!!!\s+(\w+)\s*(?:"([^"]*)")?'
    new_content = re.sub(pattern, convert_admonition, content, flags=re.MULTILINE)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Converted: {filepath}")
        return True
    return False

def main():
    docs_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
    docs_dir = os.path.abspath(docs_dir)

    converted_count = 0
    for filepath in glob.glob(os.path.join(docs_dir, '**', '*.md'), recursive=True):
        if convert_file(filepath):
            converted_count += 1

    print(f"Total files converted: {converted_count}")

if __name__ == '__main__':
    main()