import os

# Map agent names to their entry point scripts relative to the project root
AGENT_REGISTRY = {
    "hermes": "src/agents/hermes/main.py",
    "chronos": "src/agents/chronos/main.py",
    "aegis": "src/agents/aegis/main.py",
    "memorix": "src/agents/memorix/main.py",
    "athena": "src/agents/athena/main.py",
    "hephaestus": "src/agents/hephaestus/main.py",
    "nur_prometheus": "src/agents/nur_prometheus/main.py",
    "iris": "src/agents/iris/main.py",
    "hestia": "src/agents/hestia/main.py",
    "morpheus": "src/agents/morpheus/main.py"
}

def get_agent_path(agent_name: str) -> str:
    """Get the absolute path to an agent's main.py"""
    if agent_name not in AGENT_REGISTRY:
        raise ValueError(f"Agent {agent_name} not found in registry")
    
    # Assuming this code runs from project root or we can resolve it
    # For now, let's assume CWD is project root
    return os.path.abspath(AGENT_REGISTRY[agent_name])
