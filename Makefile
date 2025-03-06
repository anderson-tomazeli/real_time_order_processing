DOCKER_COMPOSE := docker-compose

# Logs target (with fix for always running)
.PHONY: logs logs-all help logs-rabbitmq logs-web up FORCE

FORCE: ;

logs: FORCE
	@$(DOCKER_COMPOSE) logs -f --tail 40 $(service-name)

logs-all:
	@$(DOCKER_COMPOSE) logs -f --tail 40

logs-rabbitmq:
	@$(DOCKER_COMPOSE) logs -f --tail 40 rabbitmq

logs-web:
	@$(DOCKER_COMPOSE) logs -f --tail 40 web

# New "up" target
up:
	@$(DOCKER_COMPOSE) up -d

# Help target
help:
	@echo "Usage:"
	@echo "  make logs service-name=<service_name>  (for specific service logs)"
	@echo "  make logs-all                          (for logs of all services)"
	@echo "  make logs-<service_name>               (for specific service logs, e.g., make logs-rabbitmq)"
	@echo "  make up                                (to start the services in detached mode)"
	@echo "  make help                              (for this help message)"
