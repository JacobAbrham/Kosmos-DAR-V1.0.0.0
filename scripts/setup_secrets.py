#!/usr/bin/env python3
import os
import sys
import base64


def get_input(prompt, default=None):
    """Get input from user with optional default."""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()


def generate_k8s_secret(secrets):
    """Generate Kubernetes Secret YAML."""
    yaml_content = """apiVersion: v1
kind: Secret
metadata:
  name: kosmos-secrets
type: Opaque
stringData:
"""
    for key, value in secrets.items():
        if value:
            # Indent and add to stringData
            yaml_content += f"  {key}: \"{value}\"\n"

    return yaml_content


def generate_env_file(secrets):
    """Generate .env file content."""
    env_content = "# KOSMOS Environment Variables\n"

    # Map k8s secret keys to env var names
    key_mapping = {
        "openai-api-key": "OPENAI_API_KEY",
        "anthropic-api-key": "ANTHROPIC_API_KEY",
        "huggingface-api-key": "HUGGINGFACE_API_KEY",
        "huggingface-endpoint-url": "HUGGINGFACE_ENDPOINT_URL"
    }

    for key, value in secrets.items():
        if value and key in key_mapping:
            env_content += f"{key_mapping[key]}={value}\n"

    return env_content


def main():
    print("=== KOSMOS Secret Configuration Setup ===")
    print("This script will generate k8s/secrets.yaml and .env for your deployment.")
    print("Press Enter to skip any optional secrets.\n")

    secrets = {}

    # 1. OpenAI
    secrets["openai-api-key"] = get_input("Enter OpenAI API Key")

    # 2. Anthropic
    secrets["anthropic-api-key"] = get_input("Enter Anthropic API Key")

    # 3. Hugging Face
    secrets["huggingface-api-key"] = get_input("Enter Hugging Face API Key")
    secrets["huggingface-endpoint-url"] = get_input(
        "Enter Hugging Face Endpoint URL (optional)", default="")

    # Generate files
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    k8s_dir = os.path.join(base_dir, "k8s")

    # Write k8s/secrets.yaml
    k8s_secret_path = os.path.join(k8s_dir, "secrets.yaml")
    with open(k8s_secret_path, "w") as f:
        f.write(generate_k8s_secret(secrets))
    print(f"\n[+] Generated Kubernetes secrets at: {k8s_secret_path}")

    # Write .env
    env_path = os.path.join(base_dir, ".env")
    with open(env_path, "w") as f:
        f.write(generate_env_file(secrets))
    print(f"[+] Generated local environment file at: {env_path}")

    print("\nSetup complete! You can now deploy using:")
    print("  kubectl apply -f k8s/secrets.yaml")
    print("  kubectl apply -f k8s/backend.yaml")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSetup cancelled.")
        sys.exit(1)
