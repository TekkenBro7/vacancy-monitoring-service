UV = uv run
UVICORN = uv run uvicorn

GREEN = \033[0;32m
RED = \033[0;31m
YELLOW = \033[1;33m
NC = \033[0m

HOST ?= 0.0.0.0
PORT ?= 8000

.PHONY: help runserver lint seed_data clean_data test

help:
	@echo "$(YELLOW)Available targets:$(NC)"
	@echo "  $(GREEN)runserver$(NC)      - Start FastAPI development server"
	@echo "  $(GREEN)lint$(NC)           - Run black, isort, ruff, mypy linters"
	@echo "  $(GREEN)seed_data$(NC)      - Seed the database"
	@echo "  $(GREEN)clean_db$(NC)       - Clean the database"
	@echo "  $(GREEN)test$(NC)           - Start tests"

runserver:
	@echo "$(GREEN)Starting FastAPI server...$(NC)"
	$(UVICORN) src.main:app --reload --host $(HOST) --port $(PORT)

lint:
	@echo "$(GREEN)Running linters...$(NC)"
	$(UV) black .
	$(UV) isort .
	$(UV) ruff check
	$(UV) ruff format
	$(UV) mypy .

seed_data:
	@echo "$(GREEN)Seeding database...$(NC)"
	$(UV) python -m scripts.seed_db

clean_data:
	@echo "$(GREEN)Cleaning database...$(NC)"
	$(UV) python -m scripts.clean_db

test:
	@echo "$(GREEN)Starting tests...$(NC)"
	$(UV) pytest -s
