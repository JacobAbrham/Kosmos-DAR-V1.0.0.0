#!/usr/bin/env python3
"""
KOSMOS Living Constitution - Scaffolding Script
Generates the complete directory structure and initial files for all 5 volumes.
"""

import os
from pathlib import Path
from datetime import datetime

# Directory structure definition
STRUCTURE = {
    "docs": {
        "01-governance": [
            "index.md",
            "raci-matrix.md",
            "ethics-scorecard.md",
            "risk-registry.md",
            "kill-switch-protocol.md",
            "legal-framework.md"
        ],
        "02-architecture": {
            "": ["index.md", "topology.md", "data-lineage.md"],
            "c4-diagrams": ["README.md"],
            "adr": ["README.md", "template.md"]
        },
        "03-engineering": {
            "": [
                "index.md",
                "prompt-standards.md",
                "canary-playbooks.md",
                "aibom.md",
                "watermarking-standard.md",
            ],
            "model-cards": ["README.md", "template.md"],
        },
        "04-operations": {
            "": ["index.md", "finops-metrics.md", "drift-detection.md", "sla-slo.md"],
            "incident-response": ["README.md", "prompt-injection.md", "loop-detection.md"]
        },
        "05-human-factors": [
            "index.md",
            "red-herring-protocols.md",
            "amnesia-protocol.md",
            "business-continuity.md",
            "training.md"
        ],
        "appendices": {
            "": ["glossary.md"],
            "templates": ["model-card-template.md", "adr-template.md", "dpia-template.md"]
        }
    },
    "scripts": [
        "generate_lineage.py",
        "generate_c4.py",
        "extract_metrics.py",
        "sync_prometheus_alerts.py",
        "sync_aibom.py",
        "validate_all.py",
        "validate_volume.py",
        "validate_schemas.py"
    ],
    "schemas": [
        "prompt-schema.json",
        "aibom-schema.json",
        "model-card-schema.json"
    ],
    ".github": {
        "workflows": [
            "build-docs.yml",
            "validate.yml",
            "deploy.yml"
        ]
    }
}

def create_structure(base_path: Path, structure: dict, parent_path: str = ""):
    """Recursively create directory structure and files."""
    for key, value in structure.items():
        current_path = base_path / parent_path / key if parent_path else base_path / key

        if isinstance(value, dict):
            # It's a directory with subdirectories
            current_path.mkdir(parents=True, exist_ok=True)
            create_structure(base_path, value, f"{parent_path}/{key}" if parent_path else key)
        elif isinstance(value, list):
            # It's a directory with files
            current_path.mkdir(parents=True, exist_ok=True)
            for file in value:
                file_path = current_path / file
                if not file_path.exists():
                    file_path.touch()
                    print(f"✓ Created: {file_path.relative_to(base_path)}")

def create_gitkeep(base_path: Path):
    """Create .gitkeep files in empty directories."""
    for root, _dirs, files in os.walk(base_path):
        root_path = Path(root)
        if not files and not any(root_path.iterdir()):
            gitkeep = root_path / ".gitkeep"
            gitkeep.touch()
            print(f"✓ Created .gitkeep in: {root_path.relative_to(base_path)}")

def main():
    """Main scaffolding execution."""
    print("=" * 60)
    print("KOSMOS Living Constitution - Scaffolding")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    base_path = Path(__file__).parent.parent

    # Create main structure
    print("Creating directory structure...")
    create_structure(base_path, STRUCTURE)

    # Create .gitkeep for empty dirs
    print("\nCreating .gitkeep files...")
    create_gitkeep(base_path / "docs")

    # Create index.md
    index_path = base_path / "docs" / "index.md"
    if not index_path.exists():
        should_create_index = True
    else:
        should_create_index = not index_path.read_text().strip()

    if should_create_index:
        index_lines = [
            "# KOSMOS Living Constitution",
            "",
            "Welcome to the **KOSMOS AI-Native Operating System** documentation -",
            "your single source of truth for governance, architecture, engineering,",
            "operations, and human factors.",
            "",
            "## Quick Navigation",
            "",
            "- **[Volume I: Governance & Legal](01-governance/index.md)** -",
            "  The \"Why\": Strategy, Ethics, Liability",
            "- **[Volume II: Architecture & Data](02-architecture/index.md)** -",
            "  The \"What\": System Topology, Decision History",
            "- **[Volume III: Engineering Handbook](03-engineering/index.md)** -",
            "  The \"How\": SDLC, Standards, Testing",
            "- **[Volume IV: Operations & FinOps](04-operations/index.md)** -",
            "  The \"Run\": Observability, Cost Control, Security",
            "- **[Volume V: Human Factors](05-human-factors/index.md)** -",
            "  The \"Who\": Training, Adoption, Safety",
            "",
            "## Core Philosophy",
            "",
            "> \"If it isn't in the repo, it doesn't exist.\"",
            "> \"If it isn't automated, it is out of date.\"",
            "",
            "This is a **Living Documentation** system:",
            "- ✅ **Immutable** - All decisions tracked via Git history",
            "- ✅ **Auditable** - Complete traceability from source to deployment",
            "- ✅ **Automated** - CI/CD-driven updates, not manual editing",
            "- ✅ **Compliant** - NIST AI RMF, ISO 42001, EU AI Act aligned",
            "",
            "## Getting Started",
            "",
            "1. **New to KOSMOS?** Start with [Volume I: Governance](01-governance/index.md)",
            "2. **Technical Team?** Jump to [Volume II: Architecture](02-architecture/index.md)",
            "3. **Operations?** See [Volume IV: Operations](04-operations/index.md)",
            "4. **Looking for Templates?** Check [Appendices](appendices/templates/)",
            "",
            "---",
            "",
            "**Last Updated:** {generated_date}  ",
            "**Version:** 1.1 Enhanced  ",
            "**Status:** Production-Ready",
        ]
        index_content = "\n".join(index_lines)
        generated_date = datetime.now().strftime("%Y-%m-%d")
        index_path.write_text(index_content.replace("{generated_date}", generated_date))
        print("✓ Created main index: docs/index.md")

    print("\n" + "=" * 60)
    print("✅ Scaffolding complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Review generated structure: tree docs/")
    print("3. Start documentation: mkdocs serve")
    print("4. Begin with Volume I: edit docs/01-governance/raci-matrix.md")

if __name__ == "__main__":
    main()
