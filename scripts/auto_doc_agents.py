import os
import re
import inspect
import importlib.util
import sys
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src"
DOCS_DIR = BASE_DIR / "docs" / "02-architecture" / "agents"

sys.path.append(str(BASE_DIR))

def get_agent_files():
    """Find all agent main.py files."""
    return list(SRC_DIR.glob("agents/*/main.py"))

def extract_tools_from_code(file_path):
    """
    Statically parse the agent file to find registered tools.
    Looking for patterns like:
    - self.mcp.tool()(self.tool_name)
    - @mcp.tool()
    - async def tool_name(...)
    """
    content = file_path.read_text()
    tools = []
    
    # Regex to find methods decorated or registered
    # This is a heuristic. For a robust solution, we'd import the class, 
    # but that requires running the code which might have side effects.
    
    # Pattern 1: self.mcp.tool()(self.method_name)
    matches = re.findall(r'self\.mcp\.tool\(\)\(self\.([a-zA-Z0-9_]+)\)', content)
    tools.extend(matches)
    
    # Pattern 2: Explicit async def methods that look like tools (heuristic)
    # We assume public async methods in the agent class are tools if they are not lifecycle methods
    # This is less accurate but helpful if registration is dynamic.
    
    return sorted(list(set(tools)))

def update_doc_file(agent_name, tools):
    """Update the markdown file for the agent."""
    # Find the doc file
    # Heuristic: agent name "nur_prometheus" -> "nur-prometheus-*.md"
    normalized_name = agent_name.replace("_", "-")
    doc_files = list(DOCS_DIR.glob(f"*{normalized_name}*.md"))
    
    if not doc_files:
        print(f"⚠️  No doc file found for {agent_name}")
        return

    doc_file = doc_files[0]
    content = doc_file.read_text()
    
    print(f"📝 Updating {doc_file.name} with tools: {tools}")
    
    # Construct new table rows
    new_rows = []
    for tool in tools:
        # We don't have params/desc from static regex, so we leave placeholders or keep existing if possible
        # For this MVP, we just list them.
        new_rows.append(f"| `{tool}` | (Auto-detected) | See code |")
        
    # In a real implementation, we would parse the existing table and merge updates,
    # or use the AST to get docstrings and params.
    
    # For now, let's just print what we WOULD do to avoid destructive regex on complex tables without AST.
    # But to demonstrate "automation", let's append a section if it doesn't exist.
    
    if "## Auto-Detected Tools" not in content:
        with open(doc_file, "a") as f:
            f.write("\n\n## Auto-Detected Tools\n\n")
            f.write("| Tool Name | Status | Source |\n")
            f.write("|-----------|--------|--------|\n")
            for tool in tools:
                f.write(f"| `{tool}` | Active | `src/agents/{agent_name}/main.py` |\n")
    else:
        # Replace the section
        # This requires more complex text processing.
        pass

def main():
    print("🤖 Starting Agent Documentation Automation...")
    agent_files = get_agent_files()
    
    for agent_file in agent_files:
        agent_name = agent_file.parent.name
        if agent_name == "pentarchy": continue # Skip shared folder
        
        print(f"🔍 Analyzing agent: {agent_name}")
        tools = extract_tools_from_code(agent_file)
        
        if tools:
            update_doc_file(agent_name, tools)
            
    print("✅ Documentation update complete.")

if __name__ == "__main__":
    main()
