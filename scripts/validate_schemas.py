#!/usr/bin/env python3
"""Validate AIBOM YAML files against JSON Schema and check schema validity."""

import sys
import json
import yaml
from pathlib import Path
from jsonschema import validate, ValidationError, Draft202012Validator

# Directories
BASE_DIR = Path(__file__).parent.parent
SCHEMAS_DIR = BASE_DIR / "schemas"
AIBOM_DIR = BASE_DIR / "aibom"


def validate_schema_syntax(schema_path: Path) -> tuple[bool, str]:
    """Validate that a JSON schema file is valid JSON and valid schema."""
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        # Check if it's a valid JSON Schema
        Draft202012Validator.check_schema(schema)
        return True, f"✓ {schema_path.name} is valid"
    except json.JSONDecodeError as e:
        return False, f"✗ {schema_path.name}: Invalid JSON - {e}"
    except Exception as e:
        return False, f"✗ {schema_path.name}: Invalid schema - {e}"


def validate_aibom_file(aibom_path: Path, schema: dict) -> tuple[bool, str]:
    """Validate an AIBOM YAML file against the schema."""
    try:
        with open(aibom_path, 'r', encoding='utf-8') as f:
            aibom_data = yaml.safe_load(f)
        
        validate(instance=aibom_data, schema=schema)
        return True, f"✓ {aibom_path.relative_to(BASE_DIR)}"
    except yaml.YAMLError as e:
        return False, f"✗ {aibom_path.relative_to(BASE_DIR)}: Invalid YAML - {e}"
    except ValidationError as e:
        return False, f"✗ {aibom_path.relative_to(BASE_DIR)}: Schema violation - {e.message}"
    except Exception as e:
        return False, f"✗ {aibom_path.relative_to(BASE_DIR)}: {e}"


def main() -> int:
    """Entry point for schema validation script."""
    print("=" * 60)
    print("KOSMOS SCHEMA VALIDATION")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # Step 1: Validate schema files themselves
    print("\n1. Validating JSON Schema Files...")
    schema_files = list(SCHEMAS_DIR.glob("*.json"))
    
    if not schema_files:
        errors.append("No schema files found in schemas/")
    
    for schema_file in schema_files:
        success, message = validate_schema_syntax(schema_file)
        if success:
            print(f"  {message}")
        else:
            print(f"  {message}")
            errors.append(message)
    
    # Step 2: Validate AIBOM files against schema
    print("\n2. Validating AIBOM Files Against Schema...")
    
    aibom_schema_path = SCHEMAS_DIR / "aibom-schema.json"
    if not aibom_schema_path.exists():
        errors.append("aibom-schema.json not found")
        print("  ✗ Cannot validate AIBOMs - schema missing")
    else:
        with open(aibom_schema_path, 'r', encoding='utf-8') as f:
            aibom_schema = json.load(f)
        
        aibom_files = list(AIBOM_DIR.glob("**/*.yaml")) + list(AIBOM_DIR.glob("**/*.yml"))
        
        if not aibom_files:
            warnings.append("No AIBOM files found")
        
        for aibom_file in aibom_files:
            if aibom_file.name == "README.md":
                continue
            success, message = validate_aibom_file(aibom_file, aibom_schema)
            if success:
                print(f"  {message}")
            else:
                print(f"  {message}")
                errors.append(message)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Errors:   {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    print("=" * 60)
    
    if errors:
        print("\n✗ SCHEMA VALIDATION FAILED")
        return 1
    
    print("\n✓ SCHEMA VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())

