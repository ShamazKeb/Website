#!/bin/bash
# ============================================================
# Pi 3B+ Deployment Script for Website Project
# ============================================================
# This script sets up all Docker services on a Raspberry Pi 3B+
# 
# Prerequisites:
#   - Raspberry Pi OS 64-bit (recommended for better Docker compatibility)
#
# Usage:
#   chmod +x deploy-pi.sh
#   ./deploy-pi.sh
# ============================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   Website Project - Pi 3B+ Deployment${NC}"
echo -e "${BLUE}================================================${NC}"

# Get script directory (where the project is)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "\n${YELLOW}📁 Working directory: $SCRIPT_DIR${NC}"

# ============================================================
# Step 0: Check & Install Docker
# ============================================================
if ! command -v docker &> /dev/null; then
    echo -e "\n${BLUE}[0/5] Docker not found. Installing...${NC}"
    echo -e "${YELLOW}This will download and run the official Docker install script.${NC}"
    read -p "Press Enter to continue or Ctrl+C to cancel..."
    
    curl -fsSL https://get.docker.com | sh
    
    echo -e "${GREEN}✅ Docker installed.${NC}"
    echo -e "${YELLOW}Adding current user ($USER) to 'docker' group...${NC}"
    sudo usermod -aG docker $USER
    
    echo -e "${RED}⚠️  You must log out and back in for group changes to take effect!${NC}"
    echo -e "${RED}⚠️  Please reboot your Pi or log out/in, then run this script again.${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Docker is already installed${NC}"
fi

# Check for Docker Compose
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not available!${NC}"
    echo -e "${YELLOW}Make sure you have Docker Compose v2 installed.${NC}"
    # Try to install plugin if missing but docker exists (common on RPi)
    echo -e "${YELLOW}Attempting to install docker-compose-plugin...${NC}"
    sudo apt-get update && sudo apt-get install -y docker-compose-plugin
    if ! docker compose version &> /dev/null; then
         echo -e "${RED}❌ still failed. Please install docker-compose manually.${NC}"
         exit 1
    fi
    echo -e "${GREEN}✅ Docker Compose installed${NC}"
fi

# ============================================================
# Step 0.5: Check & Setup Environment Files
# ============================================================
echo -e "\n${BLUE}[0.5/5] Checking configuration files...${NC}"
ENV_MISSING=0

check_and_create_env() {
    local dir=$1
    local name=$2
    if [ -d "$dir" ]; then
        if [ ! -f "$dir/.env" ]; then
            if [ -f "$dir/.env.example" ]; then
                echo -e "${YELLOW}⚠️  Creating .env for $name from example...${NC}"
                cp "$dir/.env.example" "$dir/.env"
                echo -e "${RED}❗ ACTION REQUIRED: You need to edit $dir/.env${NC}"
                ENV_MISSING=1
            else
                echo -e "${RED}❌ Missing .env and .env.example for $name!${NC}"
            fi
        else
            echo -e "${GREEN}✅ .env exists for $name${NC}"
        fi
    fi
}

check_and_create_env "infrastructure" "Infrastructure"
check_and_create_env "keto-monitor" "Keto Monitor"
check_and_create_env "handball-tracker" "Handball Tracker (Legacy)"
check_and_create_env "Handball_DB" "Handball DB (Complex App)"

if [ $ENV_MISSING -eq 1 ]; then
    echo -e "\n${RED}STOPPING DEPLOYMENT${NC}"
    echo -e "${YELLOW}Please edit the created .env files with your actual API keys and secrets.${NC}"
    echo -e "Use 'nano <filepath>' to edit."
    echo -e "Example: nano infrastructure/.env"
    echo -e "\n${GREEN}Run this script again when you are done.${NC}"
    exit 0
fi

# ============================================================
# Step 1: Create Docker network
# ============================================================
echo -e "\n${BLUE}[1/8] Creating Docker network 'web-public'...${NC}"

if docker network inspect web-public &> /dev/null; then
    echo -e "${GREEN}✅ Network 'web-public' already exists${NC}"
else
    docker network create web-public
    echo -e "${GREEN}✅ Network 'web-public' created${NC}"
fi

# ============================================================
# Step 2: Setup Infrastructure (Nginx Proxy Manager + DDNS)
# ============================================================
echo -e "\n${BLUE}[2/8] Setting up Infrastructure (NPM + DDNS)...${NC}"

if [ -d "infrastructure" ]; then
    cd infrastructure
    docker compose up -d --build
    echo -e "${GREEN}✅ Infrastructure started${NC}"
    cd "$SCRIPT_DIR"
else
    echo -e "${YELLOW}⚠️  infrastructure/ directory not found, skipping${NC}"
fi

# ============================================================
# Step 3: Setup Landing Page
# ============================================================
echo -e "\n${BLUE}[3/8] Setting up Landing Page...${NC}"

if [ -d "landing-page" ]; then
    cd landing-page
    docker compose up -d --build
    echo -e "${GREEN}✅ Landing Page started${NC}"
    cd "$SCRIPT_DIR"
else
    echo -e "${YELLOW}⚠️  landing-page/ directory not found, skipping${NC}"
fi

# ============================================================
# Step 4: Setup Keto Monitor
# ============================================================
echo -e "\n${BLUE}[4/8] Setting up Keto Monitor...${NC}"

if [ -d "keto-monitor" ]; then
    cd keto-monitor
    # Create config directory and empty db file if missing (prevents Docker directory issue)
    mkdir -p config
    if [ ! -f "keto.db" ] && [ ! -d "keto.db" ]; then
        touch keto.db
        echo -e "${YELLOW}Created empty keto.db file${NC}"
    fi
    
    docker compose up -d --build
    echo -e "${GREEN}✅ Keto Monitor started${NC}"
    cd "$SCRIPT_DIR"
else
    echo -e "${YELLOW}⚠️  keto-monitor/ directory not found, skipping${NC}"
fi

# ============================================================
# Step 5: Setup Handball Tracker (Legacy)
# ============================================================
echo -e "\n${BLUE}[5/8] Setting up Handball Tracker (Legacy)...${NC}"

if [ -d "handball-tracker" ]; then
    cd handball-tracker
    docker compose up -d --build
    echo -e "${GREEN}✅ Handball Tracker started${NC}"
    cd "$SCRIPT_DIR"
else
    echo -e "${YELLOW}⚠️  handball-tracker/ directory not found, skipping${NC}"
fi

# ============================================================
# Step 6: Setup Handball DB (Complex App)
# ============================================================
echo -e "\n${BLUE}[6/8] Setting up Handball DB (Complex App)...${NC}"

if [ -d "Handball_DB" ]; then
    cd Handball_DB
    # Ensure database file exists as file, not directory
    if [ ! -f "handball.db" ] && [ ! -d "handball.db" ]; then
        touch handball.db
        echo -e "${YELLOW}Created empty handball.db file${NC}"
    fi
    
    docker compose up -d --build
    echo -e "${GREEN}✅ Handball DB started${NC}"
    cd "$SCRIPT_DIR"
else
    echo -e "${YELLOW}⚠️  Handball_DB/ directory not found, skipping${NC}"
fi

# ============================================================
# Step 7: Setup Caro Website
# ============================================================
echo -e "\n${BLUE}[7/8] Setting up Caro Website...${NC}"

if [ -d "caro-website" ]; then
    cd caro-website
    docker compose up -d --build
    echo -e "${GREEN}✅ Caro Website started${NC}"
    cd "$SCRIPT_DIR"
else
    echo -e "${YELLOW}⚠️  caro-website/ directory not found, skipping${NC}"
fi

# ============================================================
# Step 8: Setup UPE Website
# ============================================================
echo -e "\n${BLUE}[8/8] Setting up UPE Website...${NC}"

if [ -d "UPE-website" ]; then
    cd UPE-website
    docker compose up -d --build
    echo -e "${GREEN}✅ UPE Website started${NC}"
    cd "$SCRIPT_DIR"
else
    echo -e "${YELLOW}⚠️  UPE-website/ directory not found, skipping${NC}"
fi

# ============================================================
# Summary
# ============================================================
echo -e "\n${BLUE}================================================${NC}"
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo -e "${BLUE}================================================${NC}"

echo -e "\n${YELLOW}Running containers:${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n${YELLOW}Service URLs (local network):${NC}"
PI_IP=$(hostname -I | awk '{print $1}')
echo -e "  Nginx Proxy Manager:  http://$PI_IP:81"
echo -e "  Landing Page:         via NPM proxy"
echo -e "  Keto Monitor:         http://$PI_IP:5000"
echo -e "  Handball Tracker:     http://$PI_IP:8000"
echo -e "  Handball DB Backend:  http://$PI_IP:8001 (Complex)"
echo -e "  Caro Website:         http://$PI_IP:8080 (via NPM with domain)"
echo -e "  UPE Website:          http://$PI_IP:8087 (with backend)"

echo -e "\n${YELLOW}NPM Default Login:${NC}"
echo -e "  Email:    admin@example.com"
echo -e "  Password: changeme"

echo -e "\n${BLUE}Tip: Configure your domain proxies in NPM at http://$PI_IP:81${NC}"
