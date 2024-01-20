import sys
import os
import mongomock
from fastapi.testclient import TestClient
from importlib import import_module


sys.path.append(os.path.dirname(__file__))


data1 = {"name": "data-1", "metadata": {"property-1": {"enabled": "true"}, "property-2": {"property-3": {"enabled": "true", "value": "value-3"}}}}
data2 = {"name": "data-2", "metadata": {"property-1": {"enabled": "true"}, "property-4": {"property-5": {"enabled": "true", "value": "value-5"}}}}
data3 = {"name": "data-3", "metadata": {"property-1": {"enabled": "true"}, "property-6": {"property-7": {"enabled": "true", "value": "value-7"}}}}


app = import_module("api-service").app
client = TestClient(app)


# GET /api/v1/data

@mongomock.patch(servers=(('localhost', 27017),))
def test_get_empty_db():
    response = client.get("/api/v1/data")
    assert response.status_code == 200
    assert response.json() == []


@mongomock.patch(servers=(('localhost', 27017),))
def test_get_full_db():
    for data in [data1, data2, data3]:
        response = client.post(
            "/api/v1/data",
            headers={"Content-Type": "application/json"},
            json=data
        )
    response = client.get("/api/v1/data")
    assert response.status_code == 200
    assert response.json() == [data1, data2, data3]


# POST /api/v1/data

@mongomock.patch(servers=(('localhost', 27017),))
def test_post_data():
    for data in [data1, data2, data3]:
        response = client.post(
            "/api/v1/data",
            headers={"Content-Type": "application/json"},
            json=data
        )
        assert response.status_code == 201
        assert response.json() == data


@mongomock.patch(servers=(('localhost', 27017),))
def test_post_same_data():
    response = client.post(
        "/api/v1/data",
        headers={"Content-Type": "application/json"},
        json=data1
    )
    response = client.post(
        "/api/v1/data",
        headers={"Content-Type": "application/json"},
        json=data1
    )
    assert response.status_code == 409


# GET /api/v1/data/{name}

@mongomock.patch(servers=(('localhost', 27017),))
def test_get_non_existent_data():
    response = client.get("/api/v1/data/fake-data")
    assert response.status_code == 404


@mongomock.patch(servers=(('localhost', 27017),))
def test_get_data():
    for data in [data1, data2, data3]:
        response = client.post(
            "/api/v1/data",
            headers={"Content-Type": "application/json"},
            json=data
        )

    for data in [data1, data2, data3]:
        name = data["name"]
        response = client.get(f"/api/v1/data/{name}")
        assert response.status_code == 200
        assert response.json() == data


# PUT /api/v1/data/{name}

@mongomock.patch(servers=(('localhost', 27017),))
def test_put_non_existent_data():
    name = data1["name"]
    response = client.put(
        f"/api/v1/data/{name}",
        headers={"Content-Type": "application/json"},
        json=data1
    )
    assert response.status_code == 404


@mongomock.patch(servers=(('localhost', 27017),))
def test_put_overwriting_existing_data():
    for data in [data1, data2]:
        response = client.post(
            "/api/v1/data",
            headers={"Content-Type": "application/json"},
            json=data
        )

    name = data1["name"]
    response = client.put(
        f"/api/v1/data/{name}",
        headers={"Content-Type": "application/json"},
        json=data2
    )
    assert response.status_code == 409


@mongomock.patch(servers=(('localhost', 27017),))
def test_put_data():
    response = client.post(
        "/api/v1/data",
        headers={"Content-Type": "application/json"},
        json=data1
    )

    name = data1["name"]
    response = client.put(
        f"/api/v1/data/{name}",
        headers={"Content-Type": "application/json"},
        json=data2
    )
    assert response.status_code == 200
    assert response.json() == data2


# DELETE /api/v1/data/{name}

@mongomock.patch(servers=(('localhost', 27017),))
def test_delete_non_existent_data():
    response = client.delete("/api/v1/data/fake-data")
    assert response.status_code == 404


@mongomock.patch(servers=(('localhost', 27017),))
def test_delete_data():
    response = client.post(
        "/api/v1/data",
        headers={"Content-Type": "application/json"},
        json=data1
    )
    name = data1["name"]
    response = client.delete(f"/api/v1/data/{name}")
    assert response.status_code == 200
    assert response.json() == data1


# GET /api/v1/search

@mongomock.patch(servers=(('localhost', 27017),))
def test_search_empty_db():
    response = client.get("/api/v1/search?metadata.property-1.enabled=true")
    assert response.status_code == 200
    assert response.json() == []


@mongomock.patch(servers=(('localhost', 27017),))
def test_search_invalid_query():
    response = client.get("/api/v1/search?meta.property-1.enabled=true")
    assert response.status_code == 400

    response = client.get("/api/v1/search?metadataa.property-1.enabled=true")
    assert response.status_code == 400

    response = client.get("/api/v1/search?metadata.property-1.enabled")
    assert response.status_code == 400

    response = client.get("/api/v1/search?metadata.property-1.enabled=")
    assert response.status_code == 400

    response = client.get("/api/v1/search?metadata.property-1.enabled=true&metadata.property-2.enabled=true")
    assert response.status_code == 400


@mongomock.patch(servers=(('localhost', 27017),))
def test_search_data():
    for data in [data1, data2]:
        response = client.post(
            "/api/v1/data",
            headers={"Content-Type": "application/json"},
            json=data
        )

    response = client.get("/api/v1/search?metadata.property-1.enabled=true")
    assert response.status_code == 200
    assert response.json() == [data1, data2]
