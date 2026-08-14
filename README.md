# 🤖 AI Research Agent

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-24+-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> An autonomous, multi-agent research system that performs deep research on any topic using AI — in minutes, not hours.

## 🎯 What It Does

Give it a topic, and the AI Research Agent:

1. 🔍 **Searches** the web for relevant information
2. 📊 **Analyzes** and extracts key insights
3. 📝 **Synthesizes** findings into a structured, cited report
4. ✅ **Reviews** and self-corrects for quality

## ✨ Features

### 🤖 6 Specialized AI Agents

| Agent | Role |
|-------|------|
| **Planner** | Creates research strategy and search queries |
| **Researcher** | Gathers information from web sources (Tavily API) |
| **Analyst** | Extracts insights and patterns |
| **Synthesizer** | Builds knowledge graphs and finds connections |
| **Editor** | Writes comprehensive research reports |
| **Reviewer** | Quality control and self-correction (max 3 loops) |

### 🔍 Web Search Integration
- Tavily API for AI-optimized search results
- Extracts relevant content with source attribution

### 📊 Report Generation
- 600-800 word structured reports
- Automatic citations with source links
- Professional formatting

### ✅ Self-Correction
- Reviewer agent scores each report (0-100)
- Forces refinements if score < 70
- Maximum 3 improvement iterations

## 🏗️ Architecture

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI, Python 3.11+ |
| **LLM** | Groq AI (Llama 3.3 70B) |
| **Web Search** | Tavily API |
| **Database** | PostgreSQL (Supabase) |
| **Frontend** | React 18, Tailwind CSS |
| **Containerization** | Docker |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Groq API Key
- Tavily API Key

### Installation

```bash
# Clone the repository
git clone https://github.com/simhadriuttareni/AI-Research-Agent.git
cd AI-Research-Agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your API keys

# Run with Docker
docker-compose up --build -d

# Or run locally
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Research Report: Quantum Computing

## Executive Summary
Quantum computing is a revolutionary technology that uses quantum mechanics...

## Key Findings
- Quantum computers use qubits instead of classical bits
- Potential applications in cryptography, drug discovery, optimization
- Major companies: IBM, Google, Microsoft, Rigetti

## References
[1] Quantum Computing - Wikipedia
[2] Quantum Computing: A New Era - Nature
AI-Research-Agent/
├── app/
│   ├── api/          # API routes
│   ├── agents/       # 6 specialized agents
│   ├── models/       # Database models
│   └── utils/        # Utilities
├── frontend/
│   └── src/
├── Dockerfile
├── requirements.txt
└── README.md
