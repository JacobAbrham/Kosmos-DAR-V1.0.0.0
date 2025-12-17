#!/usr/bin/env python3
"""
KOSMOS Documentation Validation Suite
Validates all documentation for completeness, broken links, and compliance
"""

import re
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Base directory
BASE_DIR = Path(__file__).parent.parent
DOCS_DIR = BASE_DIR / "docs"
AIBOM_DIR = BASE_DIR / "aibom"
SCHEMAS_DIR = BASE_DIR / "schemas"

class ValidationResult:
    """Container for validation results, storing errors, warnings, and info messages.

    This class offers helper methods to add messages and print a summary of
    the collected validation results.
    """
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []

    def add_error(self, msg: str):
        self.errors.append(f"❌ ERROR: {msg}")

    def add_warning(self, msg: str):
        self.warnings.append(f"⚠️  WARNING: {msg}")

    def add_info(self, msg: str):
        self.info.append(f"ℹ️  INFO: {msg}")

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def print_results(self):
        if self.errors:
            print("\n" + "="*60)
            print("ERRORS")
            print("="*60)
            for error in self.errors:
                print(error.encode('utf-8', 'ignore').decode('utf-8'))

        if self.warnings:
            print("\n" + "="*60)
            print("WARNINGS")
            print("="*60)
            for warning in self.warnings:
                print(warning.encode('utf-8', 'ignore').decode('utf-8'))

        if self.info:
            print("\n" + "="*60)
            print("INFO")
            print("="*60)
            for info in self.info:
                print(info.encode('utf-8', 'ignore').decode('utf-8'))

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Errors:   {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"Info:     {len(self.info)}")
        print("="*60)

        if self.has_errors():
            print("\n❌ VALIDATION FAILED")
            return 1
        print("\n✅ VALIDATION PASSED")
        return 0

def validate_markdown_files(result: ValidationResult):
    """Validate all markdown files exist and have content"""
    md_files = list(DOCS_DIR.glob("**/*.md"))
    result.add_info(f"Found {len(md_files)} markdown files")

    for md_file in md_files:
        # Check file is not empty
        size = md_file.stat().st_size
        if size == 0:
            result.add_error(f"Empty file: {md_file.relative_to(BASE_DIR)}")
        elif size < 100:
            result.add_warning(f"Very small file (<100 bytes): {md_file.relative_to(BASE_DIR)}")

        # Check for basic markdown structure
        content = md_file.read_text(encoding='utf-8')
        if not content.startswith('#'):
            result.add_warning(f"No title heading in: {md_file.relative_to(BASE_DIR)}")

def validate_internal_links(result: ValidationResult):
    """Validate internal markdown links"""
    md_files = list(DOCS_DIR.glob("**/*.md"))

    # Pattern to match markdown links: [text](link)
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')

    for md_file in md_files:
        # Skip template files
        if 'template' in md_file.name.lower():
            continue
            
        content = md_file.read_text(encoding='utf-8')
        matches = link_pattern.findall(content)

        for link_text, link_url in matches:
            # Skip external links
            if link_url.startswith(('http://', 'https://', 'mailto:', '#')):
                continue

            # Skip anchors only
            if link_url.startswith('#'):
                continue

            # Remove anchor from link
            link_path = link_url.split('#')[0]

            if not link_path:
                continue

            # Resolve relative path
            target = (md_file.parent / link_path).resolve()

            if not target.exists():
                result.add_warning(
                    f"Broken link in {md_file.relative_to(BASE_DIR)}: "
                    f"[{link_text}]({link_url})"
                )

def validate_required_files(result: ValidationResult):
    """Validate that required documentation files exist"""
    required_files = [
        "docs/index.md",
        "docs/01-governance/index.md",
        "docs/01-governance/ethics-scorecard.md",
        "docs/01-governance/risk-registry.md",
        "docs/01-governance/legal-framework.md",
        "docs/01-governance/raci-matrix.md",
        "docs/01-governance/kill-switch-protocol.md",
        "docs/02-architecture/index.md",
        "docs/03-engineering/index.md",
        "docs/04-operations/index.md",
        "docs/05-human-factors/index.md",
        "mkdocs.yml",
        "requirements.txt",
    ]

    for required_file in required_files:
        file_path = BASE_DIR / required_file
        if not file_path.exists():
            result.add_error(f"Required file missing: {required_file}")
        else:
            result.add_info(f"✓ Found: {required_file}")

def validate_schemas(result: ValidationResult):
    """Validate JSON schemas exist"""
    schema_dir = BASE_DIR / "schemas"
    if not schema_dir.exists():
        result.add_error("schemas/ directory not found")
        return

    required_schemas = [
        "aibom-schema.json",
        "model-card-schema.json",
        "prompt-schema.json"
    ]

    for schema_file in required_schemas:
        schema_path = schema_dir / schema_file
        if not schema_path.exists():
            result.add_warning(f"Schema missing: {schema_file}")
        else:
            result.add_info(f"✓ Found schema: {schema_file}")

def validate_volume_structure(result: ValidationResult):
    """Validate volume directory structure"""
    expected_volumes = [
        "01-governance",
        "02-architecture",
        "03-engineering",
        "04-operations",
        "05-human-factors"
    ]

    for volume in expected_volumes:
        volume_dir = DOCS_DIR / volume
        if not volume_dir.exists():
            result.add_error(f"Volume directory missing: {volume}")
        elif not (volume_dir / "index.md").exists():
            result.add_warning(f"Volume index missing: {volume}/index.md")


def validate_model_cards(result: ValidationResult):
    """Validate that model cards exist and follow naming convention"""
    model_cards_dir = DOCS_DIR / "03-engineering" / "model-cards"

    if not model_cards_dir.exists():
        result.add_error("Model cards directory not found")
        return

    # Find actual model card files (not template or README)
    model_cards = list(model_cards_dir.glob("MC-*.md"))

    if len(model_cards) == 0:
        result.add_error("No model card files found (expected MC-*.md files)")
    else:
        result.add_info(f"Found {len(model_cards)} model card files")
        for mc in model_cards:
            result.add_info(f"  ✓ {mc.name}")


def validate_aibom_directory(result: ValidationResult):
    """Validate AIBOM directory structure exists"""
    if not AIBOM_DIR.exists():
        result.add_error("aibom/ directory missing")
        return

    required_subdirs = ["production", "development", "deprecated"]
    for subdir in required_subdirs:
        subdir_path = AIBOM_DIR / subdir
        if not subdir_path.exists():
            result.add_warning(f"aibom/{subdir}/ directory missing")
        else:
            # Count YAML files
            yaml_files = list(subdir_path.glob("*.yaml")) + list(subdir_path.glob("*.yml"))
            result.add_info(f"aibom/{subdir}/: {len(yaml_files)} AIBOM files")


def validate_adr_count(result: ValidationResult):
    """Validate that sufficient ADRs exist"""
    adr_dir = DOCS_DIR / "02-architecture" / "adr"

    if not adr_dir.exists():
        result.add_error("ADR directory not found")
        return

    adrs = list(adr_dir.glob("ADR-*.md"))

    if len(adrs) < 5:
        result.add_warning(
            f"Only {len(adrs)} ADRs found. "
            "Consider documenting more architectural decisions."
        )
    else:
        result.add_info(f"Found {len(adrs)} ADRs")


def validate_runbooks(result: ValidationResult):
    """Validate that incident response runbooks exist"""
    runbook_dir = DOCS_DIR / "04-operations" / "incident-response"

    if not runbook_dir.exists():
        result.add_error("Incident response directory not found")
        return

    required_runbooks = [
        "prompt-injection.md",
        "loop-detection.md",
        "model-degradation.md",
        "cost-spike.md",
        "data-pipeline-failure.md",
        "third-party-api-outage.md",
        "high-error-rate.md"
    ]

    for runbook in required_runbooks:
        if not (runbook_dir / runbook).exists():
            result.add_warning(f"Runbook missing: incident-response/{runbook}")
        else:
            result.add_info(f"  ✓ {runbook}")


def validate_contact_placeholders(result: ValidationResult):
    """Check for placeholder contact information"""
    placeholder_patterns = [
        (r'\+\d{3}-XX-XXXX-XXXX', 'Phone placeholder'),
        (r'\[name\]', 'Name placeholder'),
        (r'\[email\]', 'Email placeholder'),
        (r'YYYY-MM-DD', 'Date placeholder'),
        (r'example\.com', 'Example domain'),
        (r'\bTODO\b', 'TODO marker'),
        (r'\bFIXME\b', 'FIXME marker'),
        (r'\bTBD\b(?![A-Za-z])', 'TBD marker'),
    ]

    placeholder_count = 0
    for md_file in DOCS_DIR.glob("**/*.md"):
        # Skip template files
        if 'template' in md_file.name.lower():
            continue
            
        try:
            content = md_file.read_text(encoding='utf-8')
            # Remove code blocks (```...``` and indented code blocks)
            content = re.sub(r'```[\s\S]*?```', '', content)
            content = re.sub(r'^( {4,}|\t).*', '', content, flags=re.MULTILINE)
            
            for pattern, description in placeholder_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    placeholder_count += len(matches)
                    result.add_warning(
                        f"{description} in {md_file.relative_to(BASE_DIR)}"
                    )
        except (OSError, UnicodeDecodeError) as e:
            result.add_warning(f"Could not read {md_file}: {e}")

    if placeholder_count == 0:
        result.add_info("No placeholder content found")


def validate_last_updated_dates(result: ValidationResult):
    """Check that Last Updated dates are recent"""
    date_pattern = re.compile(r'\*\*Last Updated:\*\*\s*(\d{4}-\d{2}-\d{2})')
    stale_threshold = timedelta(days=180)  # 6 months
    today = datetime.now()

    stale_docs = []
    for md_file in DOCS_DIR.glob("**/*.md"):
        try:
            content = md_file.read_text(encoding='utf-8')
            match = date_pattern.search(content)
            if match:
                date_str = match.group(1)
                try:
                    doc_date = datetime.strptime(date_str, '%Y-%m-%d')
                    if today - doc_date > stale_threshold:
                        stale_docs.append((md_file.relative_to(BASE_DIR), date_str))
                except ValueError:
                    pass
        except (OSError, UnicodeDecodeError):
            pass

    if stale_docs:
        result.add_warning(f"{len(stale_docs)} documents may be stale (>6 months old)")
        for doc, date in stale_docs[:5]:  # Show first 5
            result.add_warning(f"  - {doc}: {date}")


def validate_json_schemas(result: ValidationResult):
    """Validate JSON schemas are valid JSON"""
    if not SCHEMAS_DIR.exists():
        result.add_error("schemas/ directory not found")
        return

    for schema_file in SCHEMAS_DIR.glob("*.json"):
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                json.load(f)
            result.add_info(f"  ✓ {schema_file.name} is valid JSON")
        except json.JSONDecodeError as e:
            result.add_error(f"Invalid JSON in {schema_file.name}: {e}")


def main():
    """Run all validations"""
    # Configure stdout for UTF-8 to handle emojis on Windows
    if sys.platform == 'win32' and hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # type: ignore[union-attr]

    print("="*60)
    print("KOSMOS DOCUMENTATION VALIDATION")
    print("="*60)
    print(f"\nBase directory: {BASE_DIR}")
    print(f"Docs directory: {DOCS_DIR}\n")

    result = ValidationResult()

    print("Running validations...\n")

    print("1. Validating required files...")
    validate_required_files(result)

    print("2. Validating volume structure...")
    validate_volume_structure(result)

    print("3. Validating markdown files...")
    validate_markdown_files(result)

    print("4. Validating internal links...")
    validate_internal_links(result)

    print("5. Validating schemas...")
    validate_schemas(result)

    print("6. Validating model cards...")
    validate_model_cards(result)

    print("7. Validating AIBOM directory...")
    validate_aibom_directory(result)

    print("8. Validating ADR count...")
    validate_adr_count(result)

    print("9. Validating runbooks...")
    validate_runbooks(result)

    print("10. Checking for placeholders...")
    validate_contact_placeholders(result)

    print("11. Checking document freshness...")
    validate_last_updated_dates(result)

    print("12. Validating JSON schemas...")
    validate_json_schemas(result)

    return result.print_results()

if __name__ == "__main__":
    sys.exit(main())
