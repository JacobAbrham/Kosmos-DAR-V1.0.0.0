#!/usr/bin/env python3
"""
Content Freshness Check Script for KOSMOS Documentation

This script checks and updates content freshness markers in documentation files.
It can automatically update "Last Updated" dates and flag stale content.
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path

def find_markdown_files(directory: str = "docs") -> list[Path]:
    """Find all markdown files in the given directory."""
    path = Path(directory)
    return list(path.rglob("*.md"))

def extract_last_updated(content: str) -> str:
    """Extract the Last Updated date from content."""
    patterns = [
        r'\*\*Last Updated:\*\*\s*(\d{4}-\d{2}-\d{2})',
        r'Last Updated:\s*(\d{4}-\d{2}-\d{2})',
        r'Updated:\s*(\d{4}-\d{2}-\d{2})'
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

def update_last_updated(content: str, new_date: str) -> str:
    """Update the Last Updated date in content."""
    patterns = [
        (r'(\*\*Last Updated:\*\*\s*)\d{4}-\d{2}-\d{2}', r'\g<1>' + new_date),
        (r'(Last Updated:\s*)\d{4}-\d{2}-\d{2}', r'\g<1>' + new_date),
        (r'(Updated:\s*)\d{4}-\d{2}-\d{2}', r'\g<1>' + new_date)
    ]

    for pattern, replacement in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return re.sub(pattern, replacement, content, flags=re.IGNORECASE)

    return content

def check_file_freshness(filepath: Path, max_age_days: int = 90) -> dict:
    """Check if a file is fresh based on modification time."""
    stat = filepath.stat()
    modified_time = datetime.fromtimestamp(stat.st_mtime)
    age_days = (datetime.now() - modified_time).days

    return {
        'path': filepath,
        'modified': modified_time.strftime('%Y-%m-%d'),
        'age_days': age_days,
        'is_stale': age_days > max_age_days
    }

def main():
    """Main function to check and update content freshness."""
    max_age_days = 90
    auto_update = os.getenv('AUTO_UPDATE', 'false').lower() == 'true'

    print(f"Checking content freshness (max age: {max_age_days} days)")
    print(f"Auto-update: {auto_update}")
    print("-" * 60)

    files = find_markdown_files()
    stale_files = []
    updated_files = []

    for filepath in files:
        freshness = check_file_freshness(filepath, max_age_days)

        if freshness['is_stale']:
            stale_files.append(freshness)

            if auto_update:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Update the content with new date
                    new_content = update_last_updated(content, freshness['modified'])

                    if new_content != content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        updated_files.append(filepath)
                        print(f"✅ Updated: {filepath}")
                    else:
                        print(f"⚠️  No date marker found: {filepath}")

                except Exception as e:
                    print(f"❌ Error updating {filepath}: {e}")
            else:
                print(f"⚠️  Stale: {filepath} ({freshness['age_days']} days old)")

    print("-" * 60)
    print(f"Total files checked: {len(files)}")
    print(f"Stale files: {len(stale_files)}")
    if auto_update:
        print(f"Files updated: {len(updated_files)}")

    if stale_files and not auto_update:
        print("\nTo auto-update stale files, run:")
        print("AUTO_UPDATE=true python scripts/check_freshness.py")

if __name__ == "__main__":
    main()