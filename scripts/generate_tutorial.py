import sys
import os
from pathlib import Path

def generate_tutorial(source_file_path):
    source_path = Path(source_file_path)
    if not source_path.exists():
        print(f"Error: File {source_path} not found.")
        return

    name = source_path.stem
    tutorial_path = Path(f"docs/academy/tutorials/learn-{name}.md")
    
    content = f"""# Tutorial: Mastering {name}

**Auto-generated from:** `{source_file_path}`

## Introduction
This tutorial explains how to use the `{name}` module/agent.

## Code Structure
The module is located at `{source_file_path}`.

## Key Features
*(This section would be populated by an LLM analyzing the code)*

## Usage Example
```python
from {str(source_path.parent).replace('/', '.').replace('src.', '')}.{name} import ...

# Add your usage code here
```

## Next Steps
*   Check the [Architecture Docs](../../02-architecture/index.md)
*   Run the tests in `tests/`
"""

    tutorial_path.parent.mkdir(parents=True, exist_ok=True)
    tutorial_path.write_text(content)
    print(f"✅ Generated tutorial draft: {tutorial_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_tutorial.py <path_to_source_file>")
    else:
        generate_tutorial(sys.argv[1])
