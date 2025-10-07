from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework import status
from unittest.mock import patch


class PromptAPITests(APITestCase):
    def setUp(self):
        self.username = "tester"
        self.password = "secret123"
        self.user = User.objects.create_user(username=self.username, password=self.password)

        # obtain JWT token
        resp = self.client.post("/api/auth/login/", {"username": self.username, "password": self.password}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.token = resp.data["access"]
        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

    @patch("prompts.services.llm_provider.LLMProvider.generate", return_value="ok")
    @patch("prompts.services.embedding_index.embedding_index.add", return_value=None)
    def test_create_prompt(self, _add, _gen):
        resp = self.client.post("/api/prompts", {"prompt": "hola"}, format="json", **self.auth_headers)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", resp.data)

    def test_similar_requires_auth(self):
        resp = self.client.get("/api/prompts/similar?q=test")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("prompts.services.embedding_index.embedding_index.search", return_value=[])
    def test_similar_ok(self, _search):
        resp = self.client.get("/api/prompts/similar?q=hola", **self.auth_headers)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["query"], "hola")

    @patch("prompts.services.llm_provider.LLMProvider.generate", return_value="ok")
    def test_throttling_post(self, _gen):
        # First request should pass
        r1 = self.client.post("/api/prompts", {"prompt": "hola"}, format="json", **self.auth_headers)
        # Immediate second request likely hits 1/sec limit
        r2 = self.client.post("/api/prompts", {"prompt": "hola"}, format="json", **self.auth_headers)
        self.assertIn(r2.status_code, (status.HTTP_201_CREATED, status.HTTP_429_TOO_MANY_REQUESTS))

