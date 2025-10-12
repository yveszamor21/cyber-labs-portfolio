# Convenience tasks
.PHONY: up down logs test

up:
	docker compose -f labs-src/bind9/docker-compose.yml up -d

down:
	docker compose -f labs-src/bind9/docker-compose.yml down

logs:
	docker compose -f labs-src/bind9/docker-compose.yml logs -f bind9

test:
	dig @127.0.0.1 A example.com +dnssec
