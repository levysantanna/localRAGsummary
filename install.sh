#!/bin/bash

# Local RAG System Installation Script
# This script installs all dependencies and sets up the system

set -e  # Exit on any error

echo "🚀 Installing Local RAG System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.8+ is installed
check_python() {
    print_status "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
        PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_success "Python $PYTHON_VERSION found"
        else
            print_error "Python 3.8+ is required. Found Python $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
}

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="debian"
        elif [ -f /etc/redhat-release ]; then
            OS="redhat"
        else
            OS="linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
    
    print_status "Detected OS: $OS"
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    case $OS in
        "debian")
            print_status "Installing dependencies for Debian/Ubuntu..."
            sudo apt update
            sudo apt install -y python3-pip python3-venv python3-dev
            sudo apt install -y tesseract-ocr tesseract-ocr-por tesseract-ocr-eng
            sudo apt install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1
            sudo apt install -y build-essential
            ;;
        "redhat")
            print_status "Installing dependencies for RedHat/CentOS/Fedora..."
            sudo dnf install -y python3-pip python3-venv python3-devel
            sudo dnf install -y tesseract tesseract-langpack-por tesseract-langpack-eng
            sudo dnf install -y mesa-libGL glib2 libSM libXext libXrender libgomp
            sudo dnf install -y gcc gcc-c++ make
            ;;
        "macos")
            print_status "Installing dependencies for macOS..."
            if command -v brew &> /dev/null; then
                brew install python@3.9 tesseract
                brew install tesseract-lang
            else
                print_warning "Homebrew not found. Please install dependencies manually:"
                print_warning "  - Python 3.8+"
                print_warning "  - Tesseract OCR"
            fi
            ;;
        "windows")
            print_status "Windows detected. Please install dependencies manually:"
            print_warning "  - Python 3.8+ from python.org"
            print_warning "  - Tesseract OCR from GitHub releases"
            print_warning "  - Visual C++ Build Tools"
            ;;
        *)
            print_warning "Unknown OS. Please install dependencies manually:"
            print_warning "  - Python 3.8+"
            print_warning "  - Tesseract OCR"
            print_warning "  - Required system libraries"
            ;;
    esac
}

# Create virtual environment
setup_venv() {
    print_status "Setting up Python virtual environment..."
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists. Removing old one..."
        rm -rf venv
    fi
    
    python3 -m venv venv
    print_success "Virtual environment created"
}

# Activate virtual environment and install Python packages
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_error "requirements.txt not found!"
        exit 1
    fi
}

# Download additional models
download_models() {
    print_status "Downloading additional models..."
    
    source venv/bin/activate
    
    # Download spaCy Portuguese model
    print_status "Downloading spaCy Portuguese model..."
    python -m spacy download pt_core_news_sm || print_warning "Failed to download spaCy model"
    
    # Download NLTK data
    print_status "Downloading NLTK data..."
    python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('portuguese')" || print_warning "Failed to download NLTK data"
    
    print_success "Additional models downloaded"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p documents
    mkdir -p RAGfiles
    mkdir -p vector_db
    
    print_success "Directories created"
}

# Test installation
test_installation() {
    print_status "Testing installation..."
    
    source venv/bin/activate
    
    # Test basic imports
    python -c "
import sys
print('Python version:', sys.version)

try:
    import torch
    print('PyTorch version:', torch.__version__)
    print('CUDA available:', torch.cuda.is_available())
except ImportError as e:
    print('PyTorch import error:', e)

try:
    import transformers
    print('Transformers version:', transformers.__version__)
except ImportError as e:
    print('Transformers import error:', e)

try:
    import chromadb
    print('ChromaDB version:', chromadb.__version__)
except ImportError as e:
    print('ChromaDB import error:', e)

try:
    import sentence_transformers
    print('Sentence Transformers version:', sentence_transformers.__version__)
except ImportError as e:
    print('Sentence Transformers import error:', e)
"
    
    print_success "Installation test completed"
}

# Main installation function
main() {
    echo "🎯 Local RAG System Installation"
    echo "================================="
    
    check_python
    detect_os
    
    # Ask for system dependencies installation
    if [ "$OS" != "windows" ] && [ "$OS" != "unknown" ]; then
        read -p "Install system dependencies? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_system_deps
        else
            print_warning "Skipping system dependencies installation"
        fi
    fi
    
    setup_venv
    install_python_deps
    download_models
    create_directories
    test_installation
    
    echo
    print_success "🎉 Installation completed successfully!"
    echo
    echo "📋 Next steps:"
    echo "1. Activate the virtual environment: source venv/bin/activate"
    echo "2. Place your documents in the 'documents' directory"
    echo "3. Run: python main.py --mode process --directory documents"
    echo "4. Query your documents: python main.py --mode query --question 'Your question here'"
    echo
    echo "📚 For more information, see README.md"
}

# Run main function
main "$@"
