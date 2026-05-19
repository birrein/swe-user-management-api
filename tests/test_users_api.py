from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from src.api.v1.dependencies import get_user_use_cases
from src.application.users.use_cases import UserUseCases
from src.main import app
from tests.fakes import InMemoryUserRepository


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    repository = InMemoryUserRepository()
    use_cases = UserUseCases(repository)
    app.dependency_overrides[get_user_use_cases] = lambda: use_cases

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()


async def test_health(client: AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


async def test_create_user(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/users",
        json={
            "username": "manuel_perez",
            "email": "manuel.perez@example.com",
            "first_name": "Manuel",
            "last_name": "Perez",
            "role": "user",
        },
    )

    assert response.status_code == 201
    assert response.json()["username"] == "manuel_perez"


async def test_reject_invalid_email(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/users",
        json={
            "username": "manuel_perez",
            "email": "not-an-email",
            "first_name": "Manuel",
            "last_name": "Perez",
            "role": "user",
        },
    )

    assert response.status_code == 422


async def test_reject_invalid_username(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/users",
        json={
            "username": "bad username",
            "email": "manuel.perez@example.com",
            "first_name": "Manuel",
            "last_name": "Perez",
            "role": "user",
        },
    )

    assert response.status_code == 422


async def test_reject_invalid_role(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/users",
        json={
            "username": "manuel_perez",
            "email": "manuel.perez@example.com",
            "first_name": "Manuel",
            "last_name": "Perez",
            "role": "superadmin",
        },
    )

    assert response.status_code == 422


async def test_reject_duplicate_username(client: AsyncClient) -> None:
    payload = {
        "username": "manuel_perez",
        "email": "manuel.perez@example.com",
        "first_name": "Manuel",
        "last_name": "Perez",
        "role": "user",
    }
    first_response = await client.post("/api/v1/users", json=payload)
    second_response = await client.post("/api/v1/users", json={**payload, "email": "other@example.com"})

    assert first_response.status_code == 201
    assert second_response.status_code == 409


async def test_reject_duplicate_email(client: AsyncClient) -> None:
    payload = {
        "username": "manuel_perez",
        "email": "manuel.perez@example.com",
        "first_name": "Manuel",
        "last_name": "Perez",
        "role": "user",
    }
    first_response = await client.post("/api/v1/users", json=payload)
    second_response = await client.post("/api/v1/users", json={**payload, "username": "other_user"})

    assert first_response.status_code == 201
    assert second_response.status_code == 409


async def test_get_update_and_delete_user(client: AsyncClient) -> None:
    create_response = await client.post(
        "/api/v1/users",
        json={
            "username": "manuel_perez",
            "email": "manuel.perez@example.com",
            "first_name": "Manuel",
            "last_name": "Perez",
            "role": "user",
        },
    )
    user_id = create_response.json()["id"]

    get_response = await client.get(f"/api/v1/users/{user_id}")
    update_response = await client.patch(f"/api/v1/users/{user_id}", json={"role": "admin"})
    delete_response = await client.delete(f"/api/v1/users/{user_id}")
    deleted_user_response = await client.get(f"/api/v1/users/{user_id}")

    assert get_response.status_code == 200
    assert update_response.status_code == 200
    assert update_response.json()["role"] == "admin"
    assert delete_response.status_code == 204
    assert deleted_user_response.status_code == 200
    assert deleted_user_response.json()["active"] is False


async def test_list_users_filters_active_and_role(client: AsyncClient) -> None:
    active_response = await client.post(
        "/api/v1/users",
        json={
            "username": "active_admin",
            "email": "active@example.com",
            "first_name": "Active",
            "last_name": "Admin",
            "role": "admin",
        },
    )
    inactive_response = await client.post(
        "/api/v1/users",
        json={
            "username": "inactive_guest",
            "email": "inactive@example.com",
            "first_name": "Inactive",
            "last_name": "Guest",
            "role": "guest",
        },
    )
    await client.delete(f"/api/v1/users/{inactive_response.json()['id']}")

    default_list = await client.get("/api/v1/users")
    inactive_guests = await client.get("/api/v1/users?active=false&role=guest")

    assert active_response.status_code == 201
    assert default_list.status_code == 200
    assert default_list.json()["total"] == 1
    assert inactive_guests.status_code == 200
    assert inactive_guests.json()["total"] == 1
    assert inactive_guests.json()["items"][0]["username"] == "inactive_guest"


async def test_list_users_rejects_invalid_pagination(client: AsyncClient) -> None:
    negative_skip_response = await client.get("/api/v1/users?skip=-1")
    excessive_limit_response = await client.get("/api/v1/users?limit=101")

    assert negative_skip_response.status_code == 422
    assert excessive_limit_response.status_code == 422


async def test_get_unknown_user_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/users/11111111-1111-1111-1111-111111111111")

    assert response.status_code == 404


async def test_update_unknown_user_returns_404(client: AsyncClient) -> None:
    response = await client.patch(
        "/api/v1/users/11111111-1111-1111-1111-111111111111",
        json={"first_name": "Unknown"},
    )

    assert response.status_code == 404


async def test_delete_unknown_user_returns_404(client: AsyncClient) -> None:
    response = await client.delete("/api/v1/users/11111111-1111-1111-1111-111111111111")

    assert response.status_code == 404


async def test_delete_inactive_user_returns_404(client: AsyncClient) -> None:
    create_response = await client.post(
        "/api/v1/users",
        json={
            "username": "inactive_user",
            "email": "inactive.user@example.com",
            "first_name": "Inactive",
            "last_name": "User",
            "role": "user",
        },
    )
    user_id = create_response.json()["id"]

    first_delete_response = await client.delete(f"/api/v1/users/{user_id}")
    second_delete_response = await client.delete(f"/api/v1/users/{user_id}")

    assert first_delete_response.status_code == 204
    assert second_delete_response.status_code == 404


async def test_openapi_documents_core_user_responses(client: AsyncClient) -> None:
    response = await client.get("/openapi.json")
    paths = response.json()["paths"]

    assert response.status_code == 200
    assert "409" in paths["/api/v1/users"]["post"]["responses"]
    assert "404" in paths["/api/v1/users/{user_id}"]["get"]["responses"]
    assert "404" in paths["/api/v1/users/{user_id}"]["patch"]["responses"]
    assert "404" in paths["/api/v1/users/{user_id}"]["delete"]["responses"]
