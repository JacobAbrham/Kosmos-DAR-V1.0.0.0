#!/bin/bash
# KOSMOS Development Environment Setup Script
# This script sets up a safe development environment without exposing secrets

set -e

echo "🚀 KOSMOS Development Environment Setup"
echo "========================================"

# Check if .env already exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    echo "   For security, please verify it doesn't contain real secrets."
    echo "   If it contains real API keys, delete it and run this script again."
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Creating .env from template..."
    cp .env.example .env
    echo "   .env created from .env.example"
fi

echo ""
echo "🔧 Installing Python dependencies..."
pip install -r requirements-dev.txt

echo ""
echo "🐳 Starting infrastructure services..."
# Check if docker-compose exists in config
if [ -f "config/environments/development/docker-compose.yml" ]; then
    echo "   Starting services with docker-compose..."
    docker-compose -f config/environments/development/docker-compose.yml up -d postgres redis minio
    echo "   Waiting for services to be ready..."
    sleep 10
else
    echo "   ⚠️  Docker compose file not found in config/environments/development/"
    echo "   Please start services manually or check infrastructure setup"
fi

echo ""
echo "🗄️  Setting up database..."
# Run database migrations if alembic is configured
if [ -f "database/alembic.ini" ]; then
    echo "   Running database migrations..."
    cd database
    alembic upgrade head
    cd ..
else
    echo "   ⚠️  Alembic not configured, skipping migrations"
fi

echo ""
echo "🏗️  Building frontend dependencies..."
if [ -d "frontend" ]; then
    cd frontend
    npm install
    cd ..
else
    echo "   ⚠️  Frontend directory not found"
fi

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "🚀 Next steps:"
echo "   1. Edit .env file with your API keys (never commit real keys!)"
echo "   2. Start the API server: python src/main.py"
echo "   3. Start the frontend: cd frontend && npm run dev"
echo "   4. Run tests: pytest tests/"
echo ""
echo "📚 Useful commands:"
echo "   • View logs: docker-compose -f config/environments/development/docker-compose.yml logs -f"
echo "   • Stop services: docker-compose -f config/environments/development/docker-compose.yml down"
echo "   • Reset database: docker-compose -f config/environments/development/docker-compose.yml down -v"
echo ""
echo "🔒 Security reminder:"
echo "   • Never commit .env files with real secrets"
echo "   • Use .env.example as a template"
echo "   • Rotate any exposed API keys immediately"
