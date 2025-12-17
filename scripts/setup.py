#!/usr/bin/env python3
"""
Setup script for KOSMOS development environment
Run this after cloning the repository
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd: str, description: str) -> bool:
    """Run a shell command and return success status"""
    print(f"\n{'='*60}")
    print(f"▶ {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False


def check_prerequisites():
    """Check if required tools are installed"""
    print("\n🔍 Checking prerequisites...")
    
    required_tools = {
        "python": "python --version",
        "docker": "docker --version",
        "docker compose": "docker compose --version",
        "git": "git --version",
    }
    
    missing_tools = []
    
    for tool, cmd in required_tools.items():
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            print(f"  ✅ {tool} is installed")
        except subprocess.CalledProcessError:
            print(f"  ❌ {tool} is NOT installed")
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"\n❌ Missing required tools: {', '.join(missing_tools)}")
        print("Please install them before continuing.")
        return False
    
    print("\n✅ All prerequisites are installed!")
    return True


def setup_python_environment():
    """Setup Python virtual environment and install dependencies"""
    steps = [
        ("python -m venv .venv", "Creating virtual environment"),
        (".venv\\Scripts\\activate && pip install --upgrade pip", "Upgrading pip"),
        (".venv\\Scripts\\activate && pip install -r requirements.txt", "Installing Python dependencies"),
        (".venv\\Scripts\\activate && pip install pre-commit", "Installing pre-commit"),
        (".venv\\Scripts\\activate && pre-commit install", "Setting up pre-commit hooks"),
    ]
    
    for cmd, desc in steps:
        if not run_command(cmd, desc):
            return False
    return True


def setup_environment_file():
    """Create .env file from .env.example"""
    print("\n📝 Setting up environment file...")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("  ℹ️  .env file already exists, skipping...")
        return True
    
    if not env_example.exists():
        print("  ❌ .env.example not found")
        return False
    
    try:
        env_file.write_text(env_example.read_text())
        print("  ✅ Created .env file from .env.example")
        print("  ⚠️  Please review and update .env with your settings")
        return True
    except Exception as e:
        print(f"  ❌ Failed to create .env file: {e}")
        return False


def setup_docker_environment():
    """Start Docker containers"""
    steps = [
        ("docker compose pull", "Pulling Docker images"),
        ("docker compose up -d", "Starting Docker containers"),
    ]
    
    for cmd, desc in steps:
        if not run_command(cmd, desc):
            return False
    
    print("\n⏳ Waiting for services to be ready...")
    import time
    time.sleep(10)
    
    return run_command("docker compose ps", "Checking container status")


def initialize_database():
    """Initialize database with schema"""
    print("\n💾 Initializing database...")
    
    # Database should be initialized automatically via init.sql
    # This is just a verification step
    
    return run_command(
        "docker compose exec -T postgres psql -U kosmos -d kosmos_dev -c 'SELECT 1'",
        "Verifying database connection"
    )


def run_tests():
    """Run basic tests to verify setup"""
    print("\n🧪 Running verification tests...")
    
    # Skip if test files don't exist yet
    if not Path("tests").exists():
        print("  ℹ️  Tests directory not found, skipping...")
        return True
    
    return run_command(
        ".venv\\Scripts\\activate && pytest tests/ -v --maxfail=3",
        "Running tests"
    )


def print_summary():
    """Print setup summary and next steps"""
    print("\n" + "="*60)
    print("🎉 KOSMOS SETUP COMPLETE!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("  1. Review and update .env file with your settings")
    print("  2. Start development with: make dev")
    print("  3. View documentation: make docs-serve")
    print("  4. Run tests: make test")
    
    print("\n🔗 Useful Commands:")
    print("  • make help              - Show all available commands")
    print("  • make dev              - Start development environment")
    print("  • make dev-logs         - View container logs")
    print("  • make dev-stop         - Stop development environment")
    print("  • make test             - Run tests")
    
    print("\n📚 Services Available:")
    print("  • API:          http://localhost:8000")
    print("  • Docs:         http://localhost:8080")
    print("  • PostgreSQL:   localhost:5432")
    print("  • Redis:        localhost:6379")
    print("  • MinIO:        http://localhost:9001")
    
    print("\n" + "="*60)


def main():
    """Main setup function"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║        KOSMOS Development Environment Setup               ║")
    print("║        AI-Native Enterprise Operating System              ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    # Change to repository root
    repo_root = Path(__file__).parent
    os.chdir(repo_root)
    
    # Run setup steps
    steps = [
        ("Prerequisites Check", check_prerequisites),
        ("Python Environment", setup_python_environment),
        ("Environment File", setup_environment_file),
        ("Docker Environment", setup_docker_environment),
        ("Database Initialization", initialize_database),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            print("Please fix the errors above and run setup again.")
            sys.exit(1)
    
    # Print summary
    print_summary()
    
    print("\n✨ Setup completed successfully!")


if __name__ == "__main__":
    main()
