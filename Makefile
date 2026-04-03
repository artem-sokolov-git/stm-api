.PHONY: $(MAKECMDGOALS)

RED=\033[31m
GREEN=\033[32m
YELLOW=\033[33m
CYAN=\033[36m
RESET=\033[0m

EXEC=docker compose exec -it api
IGNORE_FLAG=-W ignore

# DOCKER
run: ## Start container in detached mode (rebuild image)
	@echo "$(CYAN)>>> Starting containers...$(RESET)"
	@docker compose up -d api --build

down: ## Stop and remove container
	@echo "$(YELLOW)>>> Stopping containers...$(RESET)"
	@docker compose down
	@echo "$(GREEN)[✓] Containers stopped$(RESET)"

clear: ## Stop container and remove all volumes
	@echo "$(RED)>>> Clearing volumes...$(RESET)"
	@docker compose down -v
	@echo "$(GREEN)[✓] Volumes cleared$(RESET)"

logs: ## Show container logs
	@echo "$(CYAN)>>> Streaming logs...$(RESET)"
	@docker compose logs -f

# CHECKS
check: ## Ruff lint and format check
	@echo "$(CYAN)>>> Running ruff checks$(RESET)"
	@uv run ruff format
	@uv run ruff check --fix
	@uv run ty check
	@echo "$(GREEN)>>> Checks passed$(RESET)"

tests: ## Run tests
	@echo "$(CYAN)>>> Running tests...$(RESET)"
	@uv run pytest tests/
	@echo "$(GREEN)>>> Tests passed$(RESET)"

## DEVELOPMENT
rebuild: ## Dev rebuild project
	@$(MAKE) clear
	@$(MAKE) run

.DEFAULT_GOAL := help

help: ## Show available commands
	@echo "$(GREEN)============================================================================================$(RESET)"
	@echo "$(GREEN)>>> List of commands:$(RESET)"
	@echo "$(GREEN)============================================================================================$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "$(CYAN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo "$(GREEN)============================================================================================$(RESET)"
