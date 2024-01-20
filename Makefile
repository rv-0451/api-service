VERSION ?= latest
IMAGE_TAG_BASE ?= 192.168.33.16:5000/api-service
IMG ?= $(IMAGE_TAG_BASE):$(VERSION)  

SHELL = /usr/bin/env bash -o pipefail
.SHELLFLAGS = -ec

PIP_PROXY = https://pypi.python.org/simple
SERVE_PORT ?= 8000

##@ General

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Code analyzer tools

.PHONY: flake
flake: ## Run flake8
	python3 -m venv venv
	source venv/bin/activate && \
	pip install flake8 -i ${PIP_PROXY} && \
	flake8 --extend-ignore E501 app/

.PHONY: mypy
mypy: ## Run mypy
	python3 -m venv venv
	source venv/bin/activate && \
	pip install mypy -i ${PIP_PROXY} && \
	cd app && \
	mypy api-service.py

##@ Build

.PHONY: docker-build
docker-build: ## Build docker image
	docker build -t ${IMG} .

.PHONY: docker-rmi
docker-rmi: ## Delete docker image
	docker rmi ${IMG}

.PHONY: docker-push
docker-push: ## Push docker image
	docker push ${IMG}

##@ Development

.PHONY: dependencies
dependencies: ## Install python dependencies
	python3 -m venv venv
	source venv/bin/activate && \
	pip install --no-cache-dir --upgrade -r requirements.txt -i ${PIP_PROXY}

.PHONY: mongo-kill
mongo-kill: ## Kill mongo container
	docker stop mongodb && \
	docker rm mongodb

.PHONY: mongo-run
mongo-run: ## Run mongo container for local development
	docker run -d \
		--name mongodb \
		--mount source=mongodb-volume,target=/data/db \
		-p 27017:27017 \
		mongo:7.0.5

.PHONY: run
run: dependencies ## Run the service locally
	source venv/bin/activate && \
	cd app && \
	SERVE_PORT=${SERVE_PORT} python3 api-service.py

.PHONY: docker-run
docker-run: ## Run the service with docker
	docker compose up --attach api-service

.PHONY: docker-rm
docker-rm: ## Stop and remove all service's docker containers
	docker compose rm --stop --force

##@ Testing

.PHONY: test
test: ## Test the service
	python3 -m venv venv
	source venv/bin/activate && \
	pip install pytest httpx mongomock -i ${PIP_PROXY} && \
	cd app && \
	SERVE_PORT=${SERVE_PORT} pytest

##@ Deployment

.PHONY: helm-deploy
helm-deploy:  ## Deploy the service to the K8s cluster with helm
	helm upgrade --install --wait myservice -n myservice --create-namespace helm/myservice

.PHONY: helm-undeploy
helm-undeploy: ## Undeploy the service from the K8s cluster with helm
	helm uninstall myservice -n myservice

