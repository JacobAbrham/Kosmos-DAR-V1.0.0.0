#!/usr/bin/env python3
"""Validate per-volume content and structure requirements."""

import sys
from pathlib import Path
from typing import List, Tuple

# Directories
BASE_DIR = Path(__file__).parent.parent
DOCS_DIR = BASE_DIR / "docs"


class VolumeValidator:
    """Validator for specific volume requirements."""
    
    def __init__(self, volume_path: Path):
        self.volume_path = volume_path
        self.volume_name = volume_path.name
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self) -> bool:
        """Run all validations for this volume."""
        if self.volume_name == "01-governance":
            self.validate_governance()
        elif self.volume_name == "02-architecture":
            self.validate_architecture()
        elif self.volume_name == "03-engineering":
            self.validate_engineering()
        elif self.volume_name == "04-operations":
            self.validate_operations()
        elif self.volume_name == "05-human-factors":
            self.validate_human_factors()
        
        return len(self.errors) == 0
    
    def validate_governance(self):
        """Validate Volume I: Governance & Legal."""
        required_files = [
            "index.md",
            "raci-matrix.md",
            "ethics-scorecard.md",
            "risk-registry.md",
            "legal-framework.md",
            "kill-switch-protocol.md"
        ]
        
        for file in required_files:
            if not (self.volume_path / file).exists():
                self.errors.append(f"Missing required file: {self.volume_name}/{file}")
    
    def validate_architecture(self):
        """Validate Volume II: Architecture & Data."""
        required_files = ["index.md", "topology.md", "data-lineage.md"]
        required_dirs = ["adr", "c4-diagrams"]
        
        for file in required_files:
            if not (self.volume_path / file).exists():
                self.errors.append(f"Missing required file: {self.volume_name}/{file}")
        
        for dir_name in required_dirs:
            if not (self.volume_path / dir_name).exists():
                self.errors.append(f"Missing required directory: {self.volume_name}/{dir_name}/")
        
        # Check ADR count
        adr_dir = self.volume_path / "adr"
        if adr_dir.exists():
            adrs = list(adr_dir.glob("ADR-*.md"))
            if len(adrs) < 3:
                self.warnings.append(f"Only {len(adrs)} ADRs found. Consider adding more architectural decisions.")
    
    def validate_engineering(self):
        """Validate Volume III: Engineering Handbook."""
        required_files = [
            "index.md",
            "aibom.md",
            "prompt-standards.md",
            "watermarking-standard.md"
        ]
        required_dirs = ["model-cards"]
        
        for file in required_files:
            if not (self.volume_path / file).exists():
                self.errors.append(f"Missing required file: {self.volume_name}/{file}")
        
        for dir_name in required_dirs:
            if not (self.volume_path / dir_name).exists():
                self.errors.append(f"Missing required directory: {self.volume_name}/{dir_name}/")
        
        # Check model cards
        mc_dir = self.volume_path / "model-cards"
        if mc_dir.exists():
            model_cards = list(mc_dir.glob("MC-*.md"))
            if len(model_cards) == 0:
                self.warnings.append("No model cards found. Add MC-*.md files.")
    
    def validate_operations(self):
        """Validate Volume IV: Operations & FinOps."""
        required_files = [
            "index.md",
            "sla-slo.md",
            "drift-detection.md",
            "finops-metrics.md"
        ]
        required_dirs = ["incident-response", "infrastructure"]
        
        for file in required_files:
            if not (self.volume_path / file).exists():
                self.errors.append(f"Missing required file: {self.volume_name}/{file}")
        
        for dir_name in required_dirs:
            if not (self.volume_path / dir_name).exists():
                self.errors.append(f"Missing required directory: {self.volume_name}/{dir_name}/")
    
    def validate_human_factors(self):
        """Validate Volume V: Human Factors."""
        required_files = [
            "index.md",
            "training.md",
            "amnesia-protocol.md",
            "business-continuity.md",
            "red-herring-protocols.md"
        ]
        
        for file in required_files:
            if not (self.volume_path / file).exists():
                self.errors.append(f"Missing required file: {self.volume_name}/{file}")


def main() -> int:
    """Entry point for volume validation script."""
    print("=" * 60)
    print("KOSMOS VOLUME VALIDATION")
    print("=" * 60)
    
    volumes = [
        "01-governance",
        "02-architecture",
        "03-engineering",
        "04-operations",
        "05-human-factors"
    ]
    
    all_errors: List[str] = []
    all_warnings: List[str] = []
    
    for volume in volumes:
        volume_path = DOCS_DIR / volume
        
        print(f"\nValidating {volume}...")
        
        if not volume_path.exists():
            error = f"Volume directory missing: {volume}/"
            print(f"  ✗ {error}")
            all_errors.append(error)
            continue
        
        validator = VolumeValidator(volume_path)
        validator.validate()
        
        if validator.errors:
            all_errors.extend(validator.errors)
            for error in validator.errors:
                print(f"  ✗ {error}")
        
        if validator.warnings:
            all_warnings.extend(validator.warnings)
            for warning in validator.warnings:
                print(f"  ⚠ {warning}")
        
        if not validator.errors and not validator.warnings:
            print(f"  ✓ {volume} is valid")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Errors:   {len(all_errors)}")
    print(f"Warnings: {len(all_warnings)}")
    print("=" * 60)
    
    if all_errors:
        print("\n✗ VOLUME VALIDATION FAILED")
        return 1
    
    print("\n✓ VOLUME VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())


