import json
from unittest import TestCase

import pytest
from django.test import Client
from django.urls import reverse

from companies.models import Company


@pytest.mark.django_db
class BasicCompanyApiTestCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.companies_url = reverse("companies-list")

    def tearDown(self) -> None:
        pass


class TestGetCompanies(BasicCompanyApiTestCase):
    def test_zero_companies_should_return_empty_list(self) -> None:
        response = self.client.get(self.companies_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [])

    def test_one_company_exists_should_succeed(self) -> None:
        test_company = Company.objects.create(name="Amazon")
        response = self.client.get(self.companies_url)
        response_content = json.loads(response.content)[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content.get("name"), test_company.name)
        self.assertEqual(response_content.get("status"), "Hiring")
        self.assertEqual(response_content.get("application_link"), "")
        self.assertEqual(response_content.get("notes"), "")

        test_company.delete()


class TestPostCompanies(BasicCompanyApiTestCase):
    def test_create_company_without_arguments_should_fail(self):
        response = self.client.post(path=self.companies_url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content), {"name": ["This field is required."]}
        )

    def test_create_existing_company_should_fail(self):
        Company.objects.create(name="Apple")

        response = self.client.post(path=self.companies_url, data={"name": "Apple"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content),
            {"name": ["company with this name already exists."]},
        )

    def test_create_company_with_only_name_all_fields_should_be_default(self):
        response = self.client.post(
            path=self.companies_url, data={"name": "Test_company_name"}
        )
        self.assertEqual(response.status_code, 201)
        response_content = json.loads(response.content)
        self.assertEqual(response_content.get("name"), "Test_company_name")
        self.assertEqual(response_content.get("status"), "Hiring")
        self.assertEqual(response_content.get("application_link"), "")
        self.assertEqual(response_content.get("notes"), "")

    def test_create_company_with_layoffs_status_should_succeed(self):
        response = self.client.post(
            path=self.companies_url,
            data={"name": "Test_company_name", "status": "Layoffs"},
        )
        self.assertEqual(response.status_code, 201)
        response_content = json.loads(response.content)
        self.assertEqual(response_content.get("status"), "Layoffs")

    def test_create_company_with_wrong_status_should_fail(self):
        response = self.client.post(
            path=self.companies_url,
            data={"name": "Test_company_name", "status": "WrongStatus"},
        )
        self.assertEqual(response.status_code, 400)
        response_content = json.loads(response.content)
        self.assertIn("WrongStatus", str(response.content))
        self.assertIn("is not a valid choice", str(response.content))
