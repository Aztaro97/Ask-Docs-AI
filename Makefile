.PHONY: help dev build test clean install setup sample lint format docker-up docker-down

# Default target
help:
	@echo "Ask-Docs Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup        - Full setup (install deps, download models)"
	@echo "  make install      - Install dependencies only"
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Start development servers"
	@echo "  make backend      - Start backend only"
	@echo "  make frontend     - Start frontend only"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up    - Start all services with Docker Compose"
	@echo "  make docker-down  - Stop all Docker services"
	@echo "  make docker-build - Build Docker images"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run all tests"
	@echo "  make test-backend - Run backend tests"
	@echo "  make test-frontend- Run frontend tests"
	@echo ""
	@echo "Sample:"
	@echo "  make sample       - Index sample docs and run query"
	@echo "  make index        - Index documents from ./docs"
	@echo ""
	@echo "Quality:"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"

# Setup
setup: install download-models
	@echo "Setup complete!"

install:
	cd backend && pip install -e ".[dev]"
	cd frontend && npm install

download-models:
	@echo "Downloading models..."
	./scripts/download-models.sh

# Development
dev:
	@echo "Starting development servers..."
	@make -j2 backend frontend

backend:
	cd backend && python -m uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

# Docker
docker-up:
	docker compose up -d
	@echo "Waiting for Ollama to be ready..."
	@sleep 10
	@echo "Pulling model..."
	docker compose exec ollama ollama pull llama3.2:3b
	@echo "Services started! Backend: http://localhost:8000, Frontend: http://localhost:5173"

docker-down:
	docker compose down

docker-build:
	docker compose build

# Testing
test: test-backend test-frontend

test-backend:
	cd backend && pytest tests/ -v

test-frontend:
	cd frontend && npm test

# Sample workflow
sample: index query

index:
	@echo "Indexing documents from ./docs..."
	curl -X POST http://localhost:8000/index \
		-H "Content-Type: application/json" \
		-d '{"force_reindex": true}'

query:
	@echo "Running sample query..."
	curl -X POST http://localhost:8000/query \
		-H "Content-Type: application/json" \
		-d '{"question": "What is this project about?", "stream": false}' | jq

# Quality
lint:
	cd backend && ruff check app/ tests/
	cd frontend && npm run lint

format:
	cd backend && ruff format app/ tests/
	cd frontend && npm run lint -- --fix

# Clean
clean:
	rm -rf backend/data/index/*
	rm -rf backend/data/cache/*
	rm -rf backend/__pycache__
	rm -rf backend/.pytest_cache
	rm -rf frontend/dist
	rm -rf frontend/node_modules/.cache
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -delete
