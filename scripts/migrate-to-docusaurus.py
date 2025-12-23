#!/usr/bin/env python3
"""
Migrate MkDocs markdown files to Docusaurus format.
Handles frontmatter conversion, admonition syntax, and link updates.
"""

import os
import re
import yaml
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import argparse


class DocusaurusMigrator:
    """Migrate MkDocs documentation to Docusaurus."""

    def __init__(self, source_dir: str, target_dir: str, verbose: bool = False):
        self.source_dir = Path(source_dir).resolve()
        self.target_dir = Path(target_dir).resolve()
        self.verbose = verbose
        self.stats = {
            'total': 0,
            'migrated': 0,
            'errors': 0,
            'skipped': 0
        }

    def log(self, message: str, level: str = 'INFO'):
        """Log message if verbose mode is enabled."""
        if self.verbose or level == 'ERROR':
            print(f"[{level}] {message}")

    def migrate_frontmatter(self, content: str) -> str:
        """Convert MkDocs frontmatter to Docusaurus format."""
        if not content.startswith('---'):
            return content

        # Extract frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            return content

        try:
            frontmatter = yaml.safe_load(parts[1])
            body = parts[2]
        except yaml.YAMLError as e:
            self.log(f"YAML parse error: {e}", 'ERROR')
            return content

        if not isinstance(frontmatter, dict):
            return content

        # Convert to Docusaurus format
        docusaurus_fm = {}

        # Map common fields
        if 'id' in frontmatter:
            docusaurus_fm['id'] = frontmatter['id']
        if 'title' in frontmatter:
            docusaurus_fm['title'] = frontmatter['title']
        if 'sidebar_label' in frontmatter:
            docusaurus_fm['sidebar_label'] = frontmatter['sidebar_label']
        if 'description' in frontmatter:
            docusaurus_fm['description'] = frontmatter['description']
        if 'keywords' in frontmatter:
            if isinstance(frontmatter['keywords'], list):
                docusaurus_fm['keywords'] = frontmatter['keywords']
            else:
                docusaurus_fm['keywords'] = [frontmatter['keywords']]
        if 'tags' in frontmatter:
            docusaurus_fm['tags'] = frontmatter['tags']

        # Remove empty values
        docusaurus_fm = {k: v for k, v in docusaurus_fm.items() if v}

        # Reconstruct
        if docusaurus_fm:
            new_frontmatter = yaml.dump(
                docusaurus_fm, default_flow_style=False, sort_keys=False)
            return f"---\n{new_frontmatter}---\n{body}"
        else:
            return body

    def convert_admonitions(self, content: str) -> str:
        """Convert MkDocs admonitions to Docusaurus format."""
        # MkDocs: !!! type "Title"
        # Docusaurus: :::type Title

        # Pattern for admonitions with title
        content = re.sub(
            r'!!! (\w+) "([^"]*)"',
            r':::\1 \2',
            content
        )

        # Pattern for admonitions without title
        content = re.sub(
            r'!!! (\w+)\s*$',
            r':::\1',
            content,
            flags=re.MULTILINE
        )

        # Map MkDocs types to Docusaurus types
        type_mapping = {
            'note': 'note',
            'abstract': 'info',
            'info': 'info',
            'tip': 'tip',
            'success': 'tip',
            'question': 'info',
            'warning': 'warning',
            'failure': 'danger',
            'danger': 'danger',
            'bug': 'danger',
            'example': 'info',
            'quote': 'note',
        }

        for mkdocs_type, docusaurus_type in type_mapping.items():
            content = re.sub(
                f':::{mkdocs_type}',
                f':::{docusaurus_type}',
                content
            )

        # Close admonitions (simple heuristic - may need manual review)
        # This is a basic implementation
        lines = content.split('\n')
        result = []
        in_admonition = False

        for i, line in enumerate(lines):
            if line.startswith(':::') and not line.startswith(':::'):
                in_admonition = True
                result.append(line)
            elif in_admonition and (line.strip() == '' or (i + 1 < len(lines) and not lines[i + 1].startswith('    '))):
                result.append(line)
                if i + 1 < len(lines) and not lines[i + 1].startswith('    ') and not lines[i + 1].startswith(':::'):
                    result.append(':::')
                    in_admonition = False
            else:
                result.append(line)

        return '\n'.join(result)

    def update_links(self, content: str, source_file: Path) -> str:
        """Update internal links to Docusaurus format."""
        # Convert relative links: [text](../path/file.md) → [text](../path/file)
        content = re.sub(
            r'\[([^\]]+)\]\(([^)]+)\.md(#[^\)]*?)?\)',
            r'[\1](\2\3)',
            content
        )

        # Update image paths
        # docs/images/... → /img/...
        content = re.sub(
            r'!\[([^\]]*)\]\(\.\.\/images\/([^)]+)\)',
            r'![\1](/img/\2)',
            content
        )

        # docs/assets/... → /assets/...
        content = re.sub(
            r'!\[([^\]]*)\]\(\.\.\/assets\/([^)]+)\)',
            r'![\1](/assets/\2)',
            content
        )

        return content

    def migrate_file(self, source_file: Path) -> bool:
        """Migrate a single file."""
        try:
            # Read content
            content = source_file.read_text(encoding='utf-8')

            # Apply transformations
            content = self.migrate_frontmatter(content)
            content = self.convert_admonitions(content)
            content = self.update_links(content, source_file)

            # Determine target path
            rel_path = source_file.relative_to(self.source_dir)
            target_file = self.target_dir / rel_path

            # Create directories
            target_file.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            target_file.write_text(content, encoding='utf-8')

            self.log(f"Migrated: {rel_path}")
            self.stats['migrated'] += 1
            return True

        except Exception as e:
            self.log(f"Error migrating {source_file}: {e}", 'ERROR')
            self.stats['errors'] += 1
            return False

    def copy_assets(self):
        """Copy static assets (images, etc.)"""
        self.log("Copying static assets...")

        # Define asset directories
        asset_mappings = {
            'images': 'img',
            'assets': 'assets',
        }

        static_dir = self.target_dir.parent / 'static'
        static_dir.mkdir(exist_ok=True)

        for source_name, target_name in asset_mappings.items():
            source_asset = self.source_dir / source_name
            if source_asset.exists():
                target_asset = static_dir / target_name
                if target_asset.exists():
                    shutil.rmtree(target_asset)
                shutil.copytree(source_asset, target_asset)
                self.log(f"Copied: {source_name} → {target_name}")

    def migrate_all(self) -> None:
        """Migrate all markdown files."""
        self.log(f"Source: {self.source_dir}")
        self.log(f"Target: {self.target_dir}")

        # Find all markdown files
        md_files = list(self.source_dir.rglob('*.md'))
        self.stats['total'] = len(md_files)

        self.log(f"Found {len(md_files)} markdown files")

        # Migrate each file
        for md_file in md_files:
            # Skip certain directories
            skip_dirs = ['docusaurus-new', 'node_modules', '.git', 'htmlcov']
            if any(skip_dir in md_file.parts for skip_dir in skip_dirs):
                self.stats['skipped'] += 1
                continue

            self.migrate_file(md_file)

        # Copy assets
        self.copy_assets()

        # Print summary
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        print(f"Total files found:    {self.stats['total']}")
        print(f"Successfully migrated: {self.stats['migrated']}")
        print(f"Skipped:              {self.stats['skipped']}")
        print(f"Errors:               {self.stats['errors']}")
        print("="*60)

        if self.stats['errors'] > 0:
            print("\n⚠️  Some files had errors. Please review the logs above.")
        else:
            print("\n✅ Migration complete!")

        print("\nNext steps:")
        print("1. Review migrated content manually")
        print("2. Update sidebars.ts with navigation structure")
        print("3. Test the documentation site: npm start")
        print("4. Fix any broken links or formatting issues")


def main():
    parser = argparse.ArgumentParser(
        description='Migrate MkDocs documentation to Docusaurus',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic migration
  python migrate-to-docusaurus.py --source ../. --target ./docs
  
  # Verbose output
  python migrate-to-docusaurus.py --source ../. --target ./docs --verbose
        """
    )

    parser.add_argument(
        '--source',
        required=True,
        help='Source directory containing MkDocs documentation'
    )
    parser.add_argument(
        '--target',
        required=True,
        help='Target directory for Docusaurus documentation (usually ./docs)'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Validate paths
    source_path = Path(args.source)
    if not source_path.exists():
        print(f"Error: Source directory does not exist: {source_path}")
        return 1

    target_path = Path(args.target)

    # Confirm overwrite if target exists
    if target_path.exists() and list(target_path.glob('*.md')):
        response = input(
            f"Target directory {target_path} contains markdown files. Overwrite? [y/N]: ")
        if response.lower() != 'y':
            print("Migration cancelled.")
            return 0

    # Run migration
    migrator = DocusaurusMigrator(
        source_dir=str(source_path),
        target_dir=str(target_path),
        verbose=args.verbose
    )

    try:
        migrator.migrate_all()
        return 0
    except KeyboardInterrupt:
        print("\n\nMigration interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
