import json
from typing import List

import pytest

from django.urls import reverse

from companies.models import Company

companies_url = reverse("companies-list")
pytestmark = pytest.mark.django_db


def test_zero_companies_should_return_empty_list(client) -> None:
    response = client.get(companies_url)
    assert response.status_code == 200
    assert json.loads(response.content) == []


@pytest.fixture
def amazon() -> Company:
    return Company.objects.create(name='amazon')


def test_one_company_exists_should_succeed(client, amazon) -> None:
    response = client.get(companies_url)
    response_content = json.loads(response.content)[0]
    assert response.status_code == 200
    assert response_content.get("name") == amazon.name
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

# ______________Learn about fixtures tests______________________

@pytest.fixture()
def companies(request, company) -> List[Company]:
    companies = []
    names = request.param
    for name in names:
        companies.append(company(name=name))
    return companies


@pytest.fixture()
def company(**kwargs):
    def _company_factory(**kwargs) -> Company:
        company_name = kwargs.pop('name', 'Test Company')
        return Company.objects.create(name=company_name, **kwargs)
    return _company_factory


@pytest.mark.parametrize(
    'companies',
    [
        ['avito', 'wildberries'],
        ['facebook', 'insta']
    ],
    indirect=True
)
def test_multiple_companies_exist_should_succeed(client, companies) -> None:
    companies_names = set(map(lambda x: x.name, companies)) # set in order not to care about the order
    response_companies = client.get(companies_url).json()
    assert len(companies_names) == len(response_companies)
    response_companies_names = set(map(lambda company: company.get('name'), response_companies))
    assert companies_names == response_companies_names
