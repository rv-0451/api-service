# Description

This is a simple HTTP service that stores and returns data.

## Endpoints

The following endpoints are implemented:

| Name   | Method      | URL
| ---    | ---         | ---
| List   | `GET`       | `/api/v1/data`
| Create | `POST`      | `/api/v1/data`
| Get    | `GET`       | `/api/v1/data/{name}`
| Update | `PUT`       | `/api/v1/data/{name}`
| Delete | `DELETE`    | `/api/v1/data/{name}`
| Query  | `GET`       | `/api/v1/search?metadata.key=value`

## Schema:

- **Data**
  - Name (string)
  - Metadata (nested key:value pairs)

# Quickstart

Clone this repo on your local linux machine.

## Deploying to kubernetes

Requirements for deploying to kubernetes:

- `api-service.vagrant.local` dns hostname should resolve to kubernetes apiserver IP (or update ingress host in `helm/myservice/values.yaml`)
- kubernetes cluster should have access to DockerHub to pull images
- `helm` installed on the local machine
- kubernetes cluster should be accessible from the local machine
- `kubeconfig` file with sufficient permissions (create namespaces + all verbs on deployment/service/ingress resources)

```bash
export KUBECONFIG=/path/to/kubeconfig
make helm-deploy
```

## Running locally

Requirements for running:

- `docker` with `compose` plugin
- current user should be able to run docker commands (i.e. be a member of `docker` group)

```bash
make docker-run
```

## Try it:

The examples below are for the kubernetes deployment. If running locally with `docker compose` replace hostname `api-service.vagrant.local` with `0.0.0.0:8000` in the `curl` command below

```bash
curl -s -H "Content-Type: application/json" -X POST http://api-service.vagrant.local/api/v1/data -d '{"name": "data-1", "metadata": {"property-1": {"enabled": "true"}, "property-2": {"property-3": {"enabled": "true", "value": "value-3"}}}}' | jq
{
  "name": "data-1",
  "metadata": {
    "property-1": {
      "enabled": "true"
    },
    "property-2": {
      "property-3": {
        "enabled": "true",
        "value": "value-3"
      }
    }
  }
}

curl -s http://api-service.vagrant.local/api/v1/search\?metadata.property-3.enabled\=true | jq
[
  {
    "name": "data-1",
    "metadata": {
      "property-1": {
        "enabled": "true"
      },
      "property-2": {
        "property-3": {
          "enabled": "true",
          "value": "value-3"
        }
      }
    }
  }
]
```

## Auto-generated documentation:

- `Swagger` http://api-service.vagrant.local/docs
- `ReDoc`: http://api-service.vagrant.local/redoc


# Local development

Requirements for local development:

- `python3` in your `$PATH` with `3.8+` version
- access to default pip repositories from your local machine (otherwise update `PIP_PROXY` variable in the `Makefile` with your local proxy)
- mongo image stored locally or access to DockerHub

All the scripts for local development are wrapped in the `Makefile`.

## Code analyzer tools

To run flake8 and mypy:

```bash
make flake
make mypy
```

## Building container

To build a container specify desired image tag with `VERSION` and `IMAGE_TAG_BASE` variables in `Makefile`

```bash
make docker-build
make docker-push # push to remote registry if necessary
```

## Running code locally

To run the service directly without building a docker container

```bash
make mongo-run # first spin up mongo container
make run # then run the service application
```

## Testing the code

Tests are implemented with fastapi `TestClient` which is based on `pytest` and `httpx` (based on `requests`). MongoDB is mocked with `mongomock`.

To run the tests

```bash
make test
```

## Misc

For other available options see the help

```bash
make help
```
