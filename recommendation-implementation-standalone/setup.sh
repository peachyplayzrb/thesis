#!/bin/bash
# Setup script for macOS/Linux environments

set -e

echo "=== Recommendation System Setup ==="
echo ""
echo "Creating Python virtual environment..."
python3 -m venv .venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo ""
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the environment: source .venv/bin/activate"
echo "2. Download the Music4All dataset and extract it"
echo "3. Run: python main.py --dataset-root /path/to/music4all/ --validate-only"
echo ""
