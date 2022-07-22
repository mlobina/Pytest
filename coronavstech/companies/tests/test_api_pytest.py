import json
import pytest

from django.urls import reverse

from companies.models import Company

companies_url = reverse("companies-list")
pytestmark = pytest.mark.django_db


def test_zero_companies_should_return_empty_list(client) -> None:
    response = client.get(companies_url)
    assert response.status_code == 200
    assert json.loads(response.content) == []


def test_one_company_exists_should_succeed(client) -> None:
    test_company = Company.objects.create(name="Amazon")
    response = client.get(companies_url)
    response_content = json.loads(response.content)[0]
    assert response.status_code == 200
    assert response_content.get("name") == test_company.name
    assert response_content.get("status") == "Hiring"
    assert response_content.get("application_link") == ""
    assert response_content.get("notes") == ""


def test_create_company_without_arguments_should_fail(client):
    response = client.post(path=companies_url)
    assert response.status_code == 400
    assert json.loads(response.content) == {"name": ["This field is required."]}


def test_create_existing_company_should_fail(client):
    Company.objects.create(name="Apple")
    response = client.post(path=companies_url, data={"name": "Apple"})
    assert response.status_code == 400
    assert json.loads(response.content) == {"name": ["company with this name already exists."]}


def test_create_company_with_only_name_all_fields_should_be_default(client):
    response = client.post(
        path=companies_url, data={"name": "Test_company_name"}
        )
    assert response.status_code == 201
    response_content = json.loads(response.content)
    assert response_content.get("name") == "Test_company_name"
    assert response_content.get("status") == "Hiring"
    assert response_content.get("application_link") == ""
    assert response_content.get("notes") == ""


def test_create_company_with_layoffs_status_should_succeed(client):
    response = client.post(
        path=companies_url,
        data={"name": "Test_company_name", "status": "Layoffs"},
        )
    assert response.status_code == 201
    response_content = json.loads(response.content)
    assert response_content.get("status") == "Layoffs"


def test_create_company_with_wrong_status_should_fail(client):
    response = client.post(
        path=companies_url,
        data={"name": "Test_company_name", "status": "WrongStatus"},
        )
    assert response.status_code == 400
    response_content = json.loads(response.content)
    assert "WrongStatus" in str(response.content)
    assert "is not a valid choice" in str(response.content)
