#!/usr/bin/env python3
"""
KOSMOS Web Setup Dashboard
A web-based interactive setup interface
"""

from flask import Flask, render_template, jsonify, request, session
from flask_socketio import SocketIO, emit
import subprocess
import threading
import os
from pathlib import Path
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store active setup processes
active_setups = {}


@app.route('/')
def index():
    """Main setup page"""
    return render_template('setup.html')


@app.route('/api/environments', methods=['GET'])
def get_environments():
    """Get list of available environments"""
    environments = [
        {
            "id": 1,
            "name": "Local Docker Compose",
            "icon": "🐳",
            "description": "Run everything on your local machine using Docker",
            "requirements": ["Docker Desktop", "8GB RAM", "20GB disk space"],
            "cost": "FREE",
            "skill_level": "Beginner",
            "setup_time": "10-15 minutes",
            "best_for": "Individual developers, offline work",
            "script": "scripts/setup-local-docker.ps1"
        },
        {
            "id": 2,
            "name": "GitHub Codespaces",
            "icon": "☁️",
            "description": "Cloud-based development environment from GitHub",
            "requirements": ["GitHub account", "Web browser"],
            "cost": "Free tier (60 hrs/month), then $0.18/hr",
            "skill_level": "Beginner",
            "setup_time": "3-5 minutes",
            "best_for": "Quick setup, any device",
            "script": "scripts/setup-codespaces.ps1"
        },
        {
            "id": 3,
            "name": "Remote Development Server",
            "icon": "🖥️",
            "description": "Connect to a shared development server",
            "requirements": ["SSH access", "Remote server with Docker", "VS Code Remote SSH"],
            "cost": "Variable (server costs)",
            "skill_level": "Intermediate",
            "setup_time": "15-20 minutes",
            "best_for": "Team collaboration",
            "script": "scripts/setup-remote-server.ps1"
        },
        {
            "id": 4,
            "name": "Shared Kubernetes Cluster",
            "icon": "☸️",
            "description": "Production-like environment with K8s",
            "requirements": ["kubectl", "Helm", "K8s cluster access"],
            "cost": "$50-200/month (shared)",
            "skill_level": "Advanced",
            "setup_time": "20-30 minutes",
            "best_for": "Production-like development",
            "script": "scripts/setup-k8s-dev.ps1"
        },
        {
            "id": 5,
            "name": "Gitpod Cloud IDE",
            "icon": "🌐",
            "description": "Browser-based IDE with automatic configuration",
            "requirements": ["GitHub account", "Web browser"],
            "cost": "Free tier (50 hrs/month), then $0.36/hr",
            "skill_level": "Beginner",
            "setup_time": "3-5 minutes",
            "best_for": "Quick demos, POCs",
            "script": "scripts/setup-gitpod.ps1"
        }
    ]
    
    return jsonify(environments)


@app.route('/api/env-variables', methods=['GET'])
def get_env_variables():
    """Get list of environment variables to configure"""
    variables = [
        {"name": "POSTGRES_DB", "default": "kosmos", "description": "PostgreSQL database name", "required": True},
        {"name": "POSTGRES_USER", "default": "kosmos", "description": "PostgreSQL username", "required": True},
        {"name": "POSTGRES_PASSWORD", "default": "kosmos_dev_password", "description": "PostgreSQL password", "required": True},
        {"name": "REDIS_PASSWORD", "default": "redis_dev_password", "description": "Redis password", "required": True},
        {"name": "MINIO_ROOT_USER", "default": "minioadmin", "description": "MinIO admin username", "required": True},
        {"name": "MINIO_ROOT_PASSWORD", "default": "minioadmin123", "description": "MinIO admin password", "required": True},
        {"name": "NATS_USER", "default": "kosmos", "description": "NATS username", "required": True},
        {"name": "NATS_PASSWORD", "default": "nats_dev_password", "description": "NATS password", "required": True},
        {"name": "GITHUB_TOKEN", "default": "", "description": "GitHub Personal Access Token (optional)", "required": False},
        {"name": "OPENAI_API_KEY", "default": "", "description": "OpenAI API Key (optional)", "required": False},
        {"name": "ANTHROPIC_API_KEY", "default": "", "description": "Anthropic API Key (optional)", "required": False},
        {"name": "SLACK_WEBHOOK_URL", "default": "", "description": "Slack webhook for notifications (optional)", "required": False},
        {"name": "ENVIRONMENT", "default": "development", "description": "Environment name", "required": True},
        {"name": "LOG_LEVEL", "default": "INFO", "description": "Logging level (DEBUG/INFO/WARNING/ERROR)", "required": True},
    ]
    
    # Try to load existing .env
    existing_values = {}
    if Path(".env").exists():
        try:
            with open(".env", "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        existing_values[key] = value
        except:
            pass
    
    # Merge with existing values
    for var in variables:
        if var["name"] in existing_values:
            var["current"] = existing_values[var["name"]]
        else:
            var["current"] = var["default"]
    
    return jsonify(variables)


@app.route('/api/save-env', methods=['POST'])
def save_env_variables():
    """Save environment variables to .env file"""
    data = request.get_json()
    variables = data.get('variables', {})
    
    try:
        env_content = "# KOSMOS Environment Configuration\n"
        env_content += "# Generated by KOSMOS Web Setup\n\n"
        
        for key, value in variables.items():
            if value.strip():
                env_content += f"{key}={value}\n"
        
        with open(".env", "w") as f:
            f.write(env_content)
        
        return jsonify({"success": True, "message": "Environment variables saved"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/start-setup', methods=['POST'])
def start_setup():
    """Start setup process"""
    data = request.get_json()
    env_id = data.get('environment_id')
    session_id = secrets.token_hex(8)
    
    # Get environment details
    environments = get_environments().get_json()
    env = next((e for e in environments if e['id'] == env_id), None)
    
    if not env:
        return jsonify({'error': 'Invalid environment'}), 400
        
    # Start setup in background
    thread = threading.Thread(
        target=run_setup,
        args=(session_id, env['script'])
    )
    thread.daemon = True
    thread.start()
    
    active_setups[session_id] = {
        'environment': env['name'],
        'status': 'running'
    }
    
    return jsonify({
        'session_id': session_id,
        'message': f'Setup started for {env["name"]}'
    })


def run_setup(session_id, script_path):
    """Run setup script and stream output"""
    try:
        socketio.emit('setup_started', {
            'session_id': session_id
        })
        
        # Run PowerShell script
        process = subprocess.Popen(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Stream output
        for line in process.stdout:
            socketio.emit('setup_output', {
                'session_id': session_id,
                'output': line.rstrip()
            })
            
        # Wait for completion
        process.wait()
        
        if process.returncode == 0:
            active_setups[session_id]['status'] = 'completed'
            socketio.emit('setup_completed', {
                'session_id': session_id,
                'success': True
            })
        else:
            error = process.stderr.read()
            active_setups[session_id]['status'] = 'failed'
            socketio.emit('setup_completed', {
                'session_id': session_id,
                'success': False,
                'error': error
            })
            
    except Exception as e:
        active_setups[session_id]['status'] = 'failed'
        socketio.emit('setup_error', {
            'session_id': session_id,
            'error': str(e)
        })


@app.route('/api/setup-status/<session_id>', methods=['GET'])
def get_setup_status(session_id):
    """Get status of setup"""
    status = active_setups.get(session_id, {'status': 'not_found'})
    return jsonify(status)


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'message': 'Connected to setup server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🚀 KOSMOS Web Setup Dashboard")
    print("=" * 50)
    print("Starting server at: http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
