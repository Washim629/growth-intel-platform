import io
import uuid
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db
from app.api import auth as auth_api

init_db()
client = TestClient(app)
test_user_email = None


def _register_verified(monkeypatch, email, organization_name, full_name, password):
    delivered = []
    monkeypatch.setattr(auth_api, "send_login_code", lambda recipient, code: delivered.append((recipient, code)))
    monkeypatch.setattr(auth_api, "get_settings", lambda: SimpleNamespace(
        SMTP_HOST="smtp.example.com",
        SMTP_FROM_EMAIL="noreply@example.com",
        LOGIN_OTP_RESEND_SECONDS=0,
        LOGIN_OTP_EXPIRE_MINUTES=10,
        JWT_SECRET_KEY="test-secret",
    ))
    request = client.post("/api/auth/register/otp/request", json={"email": email})
    assert request.status_code == 200, request.text
    assert delivered and delivered[0][0] == email
    verify = client.post("/api/auth/register/otp/verify", json={"email": email, "code": delivered[0][1]})
    assert verify.status_code == 200, verify.text
    return client.post("/api/auth/register", json={
        "organization_name": organization_name,
        "full_name": full_name,
        "email": email,
        "password": password,
    })


@pytest.fixture
def auth_headers(monkeypatch):
    global test_user_email
    email = f"founder-{uuid.uuid4().hex}@example.com"
    test_user_email = email
    resp = _register_verified(monkeypatch, email, "Acme Inc", "Founder", "supersecret123")
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_check():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_register_requires_verified_email_before_creating_account(monkeypatch):
    email = f"jane-{uuid.uuid4().hex}@example.com"
    delivered = []
    monkeypatch.setattr(auth_api, "send_login_code", lambda recipient, code: delivered.append(code))
    monkeypatch.setattr(auth_api, "get_settings", lambda: SimpleNamespace(
        SMTP_HOST="smtp.example.com",
        SMTP_FROM_EMAIL="noreply@example.com",
        LOGIN_OTP_RESEND_SECONDS=0,
        LOGIN_OTP_EXPIRE_MINUTES=10,
        JWT_SECRET_KEY="test-secret",
    ))
    unverified = client.post("/api/auth/register", json={
        "organization_name": "Test Org",
        "full_name": "Jane Doe",
        "email": email,
        "password": "password123",
    })
    assert unverified.status_code == 400

    request = client.post("/api/auth/register/otp/request", json={"email": email})
    assert request.status_code == 200
    code = delivered[0]
    invalid_code = "000000" if code != "000000" else "000001"
    invalid = client.post("/api/auth/register/otp/verify", json={"email": email, "code": invalid_code})
    assert invalid.status_code == 400

    verify = client.post("/api/auth/register/otp/verify", json={"email": email, "code": code})
    assert verify.status_code == 200
    resp = client.post("/api/auth/register", json={
        "organization_name": "Test Org",
        "full_name": "Jane Doe",
        "email": email,
        "password": "password123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["user"]["email"] == email

    login = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    assert login.status_code == 200
    assert "access_token" in login.json()

    bad_login = client.post("/api/auth/login", json={"email": email, "password": "wrong"})
    assert bad_login.status_code == 401


def test_email_otp_login_is_single_use_and_rejects_wrong_codes(monkeypatch):
    email = f"otp-{uuid.uuid4().hex}@example.com"
    register = _register_verified(monkeypatch, email, "OTP Test Org", "OTP User", "password123")
    assert register.status_code == 201

    delivered = []
    monkeypatch.setattr(auth_api, "send_login_code", lambda recipient, code: delivered.append((recipient, code)))
    monkeypatch.setattr(auth_api, "get_settings", lambda: SimpleNamespace(
        SMTP_HOST="smtp.example.com",
        SMTP_FROM_EMAIL="noreply@example.com",
        LOGIN_OTP_RESEND_SECONDS=60,
        LOGIN_OTP_EXPIRE_MINUTES=10,
        JWT_SECRET_KEY="test-secret",
    ))

    request = client.post("/api/auth/login/otp/request", json={"email": email})
    assert request.status_code == 200
    assert delivered[0][0] == email
    code = delivered[0][1]

    invalid = client.post("/api/auth/login/otp/verify", json={"email": email, "code": "000000" if code != "000000" else "000001"})
    assert invalid.status_code == 401

    verified = client.post("/api/auth/login/otp/verify", json={"email": email, "code": code})
    assert verified.status_code == 200
    assert verified.json()["user"]["email"] == email
    assert verified.json()["access_token"]

    replay = client.post("/api/auth/login/otp/verify", json={"email": email, "code": code})
    assert replay.status_code == 401


def test_email_otp_request_requires_smtp_configuration(monkeypatch):
    monkeypatch.setattr(auth_api, "get_settings", lambda: SimpleNamespace(
        SMTP_HOST="",
        SMTP_FROM_EMAIL="",
    ))

    response = client.post("/api/auth/register/otp/request", json={"email": "nobody@example.com"})
    assert response.status_code == 503


def test_registration_email_request_requires_smtp_app_password(monkeypatch):
    monkeypatch.setattr(auth_api, "get_settings", lambda: SimpleNamespace(
        SMTP_HOST="smtp.gmail.com",
        SMTP_FROM_EMAIL="growthanalyzer@gmail.com",
        SMTP_USERNAME="growthanalyzer@gmail.com",
        SMTP_PASSWORD="",
    ))

    response = client.post("/api/auth/register/otp/request", json={"email": "new-user@example.com"})
    assert response.status_code == 503
    assert "SMTP_PASSWORD is missing" in response.json()["detail"]


def test_email_otp_is_locked_after_five_incorrect_attempts(monkeypatch):
    email = f"otp-lock-{uuid.uuid4().hex}@example.com"
    register = _register_verified(monkeypatch, email, "OTP Lock Test Org", "OTP Lock User", "password123")
    assert register.status_code == 201

    delivered = []
    monkeypatch.setattr(auth_api, "send_login_code", lambda recipient, code: delivered.append(code))
    monkeypatch.setattr(auth_api, "get_settings", lambda: SimpleNamespace(
        SMTP_HOST="smtp.example.com",
        SMTP_FROM_EMAIL="noreply@example.com",
        LOGIN_OTP_RESEND_SECONDS=60,
        LOGIN_OTP_EXPIRE_MINUTES=10,
        JWT_SECRET_KEY="test-secret",
    ))
    request = client.post("/api/auth/login/otp/request", json={"email": email})
    assert request.status_code == 200

    for _ in range(5):
        invalid = client.post("/api/auth/login/otp/verify", json={"email": email, "code": "000000" if delivered[0] != "000000" else "000001"})
        assert invalid.status_code == 401

    locked = client.post("/api/auth/login/otp/verify", json={"email": email, "code": delivered[0]})
    assert locked.status_code == 401


def test_change_password_requires_current_password(auth_headers):
    response = client.post(
        "/api/auth/change-password",
        json={"current_password": "supersecret123", "new_password": "newsecret456"},
        headers=auth_headers,
    )
    assert response.status_code == 200

    old_login = client.post("/api/auth/login", json={
        "email": test_user_email,
        "password": "supersecret123",
    })
    assert old_login.status_code == 401

    new_login = client.post("/api/auth/login", json={
        "email": test_user_email,
        "password": "newsecret456",
    })
    assert new_login.status_code == 200


def test_change_password_rejects_incorrect_current_password(auth_headers):
    response = client.post(
        "/api/auth/change-password",
        json={"current_password": "wrong-password", "new_password": "newsecret456"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Current password is incorrect."


def test_upload_requires_auth():
    csv_bytes = b"lead_id,email,revenue\nL1,a@x.com,100\n"
    resp = client.post("/api/datasets/upload", files={"file": ("test.csv", io.BytesIO(csv_bytes), "text/csv")})
    assert resp.status_code == 401


def test_upload_and_run_analysis(auth_headers):
    import time

    csv_content = "lead_id,email,signup_date,source,revenue,payment_date\n"
    for i in range(50):
        payment = f"2024-02-{(i % 28) + 1:02d}" if i % 3 == 0 else ""
        csv_content += f"L{i},user{i}@x.com,2024-01-{(i % 28) + 1:02d},google,{10*i},{payment}\n"

    resp = client.post(
        "/api/datasets/upload",
        files={"file": ("leads.csv", io.BytesIO(csv_content.encode()), "text/csv")},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    preview = resp.json()
    dataset_id = preview["dataset_id"]
    assert preview["total_rows"] == 50

    mapping = {k: v for k, v in preview["suggested_mapping"].items() if v}
    map_resp = client.post(f"/api/datasets/{dataset_id}/mapping", json={"mapping": mapping}, headers=auth_headers)
    assert map_resp.status_code == 200

    run_resp = client.post(f"/api/analysis/{dataset_id}", headers=auth_headers)
    assert run_resp.status_code == 202
    run_id = run_resp.json()["id"]

    # Poll for completion (background thread)
    for _ in range(30):
        status_resp = client.get(f"/api/analysis/{run_id}", headers=auth_headers)
        status = status_resp.json()["status"]
        if status in ("completed", "failed"):
            break
        time.sleep(0.2)
    assert status == "completed", status_resp.json()

    kpi_resp = client.get(f"/api/kpis/{dataset_id}", headers=auth_headers)
    assert kpi_resp.status_code == 200
    kpis = {item["metric"]: item["value"] for item in kpi_resp.json()["kpis"]}
    assert kpis["leads"] == 50

    funnel_resp = client.get(f"/api/funnel/{dataset_id}", headers=auth_headers)
    assert funnel_resp.status_code == 200
    assert len(funnel_resp.json()["stages"]) > 0
