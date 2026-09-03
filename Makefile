COMPOSE := docker compose

.PHONY: build up down restart logs ps clean backend-shell frontend-shell

build: ## Build the backend and frontend images
	$(COMPOSE) build

up: ## Build (if needed) and start the app in the background
	$(COMPOSE) up -d --build

down: ## Stop and remove the containers
	$(COMPOSE) down

restart: down up ## Restart the app

logs: ## Follow logs from both services
	$(COMPOSE) logs -f

ps: ## Show running containers
	$(COMPOSE) ps

clean: ## Stop containers and remove local images/volumes
	$(COMPOSE) down -v --rmi local

backend-shell: ## Open a shell inside the backend container
	$(COMPOSE) exec backend sh

frontend-shell: ## Open a shell inside the frontend container
	$(COMPOSE) exec frontend sh
