#!/usr/bin/env python3
"""
Validate MCP Configuration File
Checks that blackbox_mcp_settings.json is valid and properly configured.
"""

import json
import sys

def validate_mcp_config():
    """Validate the MCP configuration file."""
    print("=== MCP Configuration Validation ===\n")
    
    try:
        # Read the configuration file
        with open('blackbox_mcp_settings.json', 'r') as f:
            config = json.load(f)
        
        print("✓ JSON file is valid and parseable\n")
        
        # Check structure
        if 'mcpServers' not in config:
            print("✗ Missing 'mcpServers' key")
            return False
        
        print("✓ 'mcpServers' key exists\n")
        
        servers = config['mcpServers']
        print(f"Found {len(servers)} MCP server(s) configured:\n")
        
        # Validate each server
        for server_name, server_config in servers.items():
            print(f"Server: {server_name}")
            
            # Check required fields
            if 'command' not in server_config:
                print(f"  ✗ Missing 'command' field")
                return False
            print(f"  ✓ Command: {server_config['command']}")
            
            if 'args' not in server_config:
                print(f"  ✗ Missing 'args' field")
                return False
            print(f"  ✓ Args: {server_config['args']}")
            
            # Validate args is a list
            if not isinstance(server_config['args'], list):
                print(f"  ✗ 'args' must be a list")
                return False
            print(f"  ✓ Args is a valid list with {len(server_config['args'])} item(s)")
            print()
        
        # Check for Sequential Thinking server
        seq_thinking_key = "github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking"
        if seq_thinking_key in servers:
            print("✓ Sequential Thinking server is configured")
            seq_config = servers[seq_thinking_key]
            
            # Verify correct package
            if '@modelcontextprotocol/server-sequential-thinking' in seq_config['args']:
                print("✓ Correct package name configured")
            else:
                print("✗ Package name may be incorrect")
                return False
            
            # Verify npx command
            if seq_config['command'] == 'npx':
                print("✓ Using npx command")
            else:
                print("⚠ Warning: Not using npx command")
        else:
            print("✗ Sequential Thinking server not found in configuration")
            return False
        
        print("\n=== Validation Summary ===")
        print("✓ All checks passed!")
        print("✓ Configuration is valid and ready to use")
        return True
        
    except FileNotFoundError:
        print("✗ Error: blackbox_mcp_settings.json not found")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ Error: Invalid JSON - {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    success = validate_mcp_config()
    sys.exit(0 if success else 1)
