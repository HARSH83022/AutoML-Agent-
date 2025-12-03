#!/bin/bash

# AutoML Platform Setup Script
# This script sets up the complete development environment

set -e

echo "========================================="
echo "AutoML Platform - Setup Script"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python
echo -e "${BLUE}Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.10+${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python found${NC}"

# Check Node.js
echo -e "${BLUE}Checking Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed. Please install Node.js 18+${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found${NC}"

# Setup Backend
echo ""
echo -e "${BLUE}Setting up Backend...${NC}"

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Backend dependencies installed${NC}"

# Setup environment file
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Environment file created${NC}"
    echo -e "${BLUE}Please edit .env with your configuration${NC}"
fi

# Create directories
mkdir -p artifacts data
echo -e "${GREEN}✓ Directories created${NC}"

# Setup Frontend
echo ""
echo -e "${BLUE}Setting up Frontend...${NC}"
cd frontend

# Install Node dependencies
npm install
echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

cd ..

# Setup Git hooks (optional)
echo ""
echo -e "${BLUE}Setting up Git hooks...${NC}"
if [ -d ".git" ]; then
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Run linting before commit
cd frontend && npm run lint
EOF
    chmod +x .git/hooks/pre-commit
    echo -e "${GREEN}✓ Git hooks configured${NC}"
fi

# Final instructions
echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure your environment:"
echo "   ${BLUE}nano .env${NC}"
echo ""
echo "2. Start the backend:"
echo "   ${BLUE}source venv/bin/activate${NC}"
echo "   ${BLUE}uvicorn app.main:app --reload${NC}"
echo ""
echo "3. Start the frontend (in another terminal):"
echo "   ${BLUE}cd frontend${NC}"
echo "   ${BLUE}npm run dev${NC}"
echo ""
echo "4. Or use Docker:"
echo "   ${BLUE}docker-compose up${NC}"
echo ""
echo "Access the application at:"
echo "   Frontend: ${GREEN}http://localhost:3000${NC}"
echo "   Backend:  ${GREEN}http://localhost:8000${NC}"
echo "   Docs:     ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${BLUE}Happy coding! 🚀${NC}"
