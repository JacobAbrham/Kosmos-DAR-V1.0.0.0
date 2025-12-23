#!/usr/bin/env python3
"""
Tutorial Generation Script for KOSMOS Documentation

This script generates basic tutorial stubs for the academy section.
It can be used to create new tutorials or update existing ones.
"""

import os
import yaml
from pathlib import Path

def generate_tutorial_stub(title: str, filename: str, description: str = "") -> str:
    """Generate a basic tutorial markdown stub."""
    content = f"""# {title}

**Estimated Time:** 30 minutes  
**Difficulty:** Beginner  
**Prerequisites:** None  

---

## Overview

{description or "This tutorial will guide you through [topic]."}

## Learning Objectives

By the end of this tutorial, you will be able to:

- Understand [concept]
- Implement [feature]
- Troubleshoot [issue]

## Prerequisites

- [Prerequisite 1]
- [Prerequisite 2]

## Step-by-Step Guide

### Step 1: [First Step]

[Instructions for first step]

```bash
# Example command
echo "Hello World"
```

### Step 2: [Second Step]

[Instructions for second step]

## Next Steps

- [Link to next tutorial](next-tutorial.md)
- [Related documentation](../../section/file.md)

## Troubleshooting

### Common Issues

**Issue:** [Common problem]  
**Solution:** [How to fix it]

## Additional Resources

- [Official Documentation](https://docs.example.com)
- [Community Forum](https://forum.example.com)
"""
    return content

def main():
    """Main function to generate tutorials."""
    tutorials_dir = Path("docs/academy/tutorials")

    # Ensure directory exists
    tutorials_dir.mkdir(parents=True, exist_ok=True)

    # Tutorial definitions
    tutorials = [
        {
            "title": "Creating Your First Agent",
            "filename": "create-agent.md",
            "description": "Learn how to create and configure your first AI agent in the KOSMOS platform."
        },
        {
            "title": "Adding a Custom MCP Tool",
            "filename": "add-mcp-tool.md",
            "description": "Extend your agent's capabilities by integrating custom MCP (Model Context Protocol) tools."
        },
        {
            "title": "Debugging Agent Interactions",
            "filename": "debugging.md",
            "description": "Master debugging techniques for agent-to-agent and agent-to-human interactions."
        },
        {
            "title": "Customizing Governance Logic",
            "filename": "governance-logic.md",
            "description": "Implement custom governance rules and policies for your agents."
        },
        {
            "title": "Scaling Infrastructure",
            "filename": "scaling.md",
            "description": "Scale your agent infrastructure to handle increased load and complexity."
        },
        {
            "title": "Security Hardening",
            "filename": "security-hardening.md",
            "description": "Implement security best practices to protect your agents and data."
        }
    ]

    for tutorial in tutorials:
        filepath = tutorials_dir / tutorial["filename"]

        if not filepath.exists():
            content = generate_tutorial_stub(
                tutorial["title"],
                tutorial["filename"],
                tutorial["description"]
            )

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"Generated: {filepath}")
        else:
            print(f"Skipped (exists): {filepath}")

if __name__ == "__main__":
    main()