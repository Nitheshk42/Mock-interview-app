#!/bin/bash

echo "🚀 Mock Interview App Setup"
echo "============================"

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Download spaCy model
echo "📚 Downloading spaCy model..."
python -m spacy download en_core_web_sm

# Create directories if needed
mkdir -p database
mkdir -p services
mkdir -p routes

echo "✅ Setup complete!"
echo ""
echo "To start the server, run:"
echo "source venv/bin/activate"
echo "python main.py"
echo ""
echo "API will be available at: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
