import pytest
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()

URL = "/api/users/register"
PAYLOAD = {"email": "nowy@example.com", "password": "bardzoTajneHaslo123"}


@pytest.mark.django_db
class TestRegister:
    def test_registers_user_201(self, client: Client) -> None:
        response = client.post(URL, PAYLOAD, content_type="application/json")

        assert response.status_code == 201
        assert set(response.json()) == {"access", "refresh"}
        assert User.objects.get(email=PAYLOAD["email"]).check_password(PAYLOAD["password"])

    def test_can_log_in_after_register_200(self, client: Client) -> None:
        client.post(URL, PAYLOAD, content_type="application/json")

        response = client.post(
            "/api/token/pair",
            {"username": PAYLOAD["email"], "password": PAYLOAD["password"]},
            content_type="application/json",
        )

        assert response.status_code == 200
        assert "access" in response.json()

    def test_rejects_duplicate_email_409(self, client: Client) -> None:
        client.post(URL, PAYLOAD, content_type="application/json")

        response = client.post(URL, PAYLOAD, content_type="application/json")

        assert response.status_code == 409

    def test_rejects_weak_password_400(self, client: Client) -> None:
        response = client.post(URL, {"email": "a@example.com", "password": "abc"}, content_type="application/json")

        assert response.status_code == 400

    def test_rejects_invalid_email_400(self, client: Client) -> None:
        response = client.post(
            URL, {"email": "nie-email", "password": PAYLOAD["password"]}, content_type="application/json"
        )

        assert response.status_code == 400
