#!/bin/bash
# Verification and setup script for Endee RAG System

echo "=========================================="
echo "Endee RAG System - Project Verification"
echo "=========================================="
echo ""

# Check Python version
echo "1. Checking Python installation..."
python_version=$(python --version 2>&1)
if [[ $? -eq 0 ]]; then
    echo "   ✓ Python found: $python_version"
else
    echo "   ✗ Python not found. Please install Python 3.9+"
    exit 1
fi

# Check if venv exists
echo ""
echo "2. Checking virtual environment..."
if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python -m venv venv
    echo "   ✓ Virtual environment created"
else
    echo "   ✓ Virtual environment exists"
fi

# Activate venv
echo ""
echo "3. Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
echo "   ✓ Virtual environment activated"

# Install dependencies
echo ""
echo "4. Checking/installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
    echo "   ✓ Dependencies installed"
else
    echo "   ✗ requirements.txt not found"
    exit 1
fi

# Check .env file
echo ""
echo "5. Checking configuration..."
if [ ! -f ".env" ]; then
    echo "   Creating .env from template..."
    cp .env.example .env
    echo "   ✓ .env created (customize as needed)"
else
    echo "   ✓ .env file exists"
fi

# Verify file structure
echo ""
echo "6. Verifying project structure..."
required_files=(
    "src/main.py"
    "src/endee_client.py"
    "src/embedding_service.py"
    "src/rag_service.py"
    "src/config.py"
    "scripts/ingest_samples.py"
    "scripts/example_search.py"
    "README.md"
    "QUICK_START.md"
)

all_files_exist=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file"
    else
        echo "   ✗ $file NOT FOUND"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = false ]; then
    echo ""
    echo "   ✗ Some files are missing"
    exit 1
fi

# Project summary
echo ""
echo "=========================================="
echo "✓ PROJECT VERIFICATION COMPLETE"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Make sure Endee is running:"
echo "   docker run -p 8080:8080 -v endee-data:/data endeeio/endee-server:latest"
echo ""
echo "2. (Optional) Ingest sample data:"
echo "   python -m scripts.ingest_samples"
echo ""
echo "3. Start the API server:"
echo "   python -m uvicorn src.main:app --reload"
echo ""
echo "4. Open in browser:"
echo "   http://localhost:8000/docs"
echo ""
echo "For detailed instructions, see QUICK_START.md"
echo ""
