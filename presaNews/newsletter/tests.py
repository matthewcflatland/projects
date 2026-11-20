from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from grabsomore.models import CustomUser
from grabsomore.utils import (
    create_reader,
    create_journalist,
    create_editor
    )
from .models import Article, Newsletter, Publisher
from .serializers import ArticleSerializer
from datetime import datetime


# Create your tests here.   
class ArticleListAPITestCase(APITestCase):
    def setUp(self):
        self.testpublisher = Publisher.objects.create(
            name="testpublisher"
        )

        self.User = get_user_model()
        self.journalist = self.User.objects.create_user(
            username='journalist',
            email='journalist@test.com',
            password='password',
            publisher=self.testpublisher
        )
        self.reader = self.User.objects.create_user(
            username='reader',
            email='reader@test.com',
            password='password',
            publisher=None
        )
        self.journalist.groups.add(create_journalist())
        self.token_j = Token.objects.create(user=self.journalist)
        self.token_r = Token.objects.create(user=self.reader)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_r}")

        self.article1 = Article.objects.create(
            title="test Article 1",
            content="test article",
            author=self.journalist,
            created_at=datetime.now(),
            publisher=self.journalist.publisher,
            approved=True
        )
        self.article2 = Article.objects.create(
            title="test Article 2",
            content="test article",
            author=self.journalist,
            created_at=datetime.now(),
            publisher=self.journalist.publisher,
            approved=False
        )
        self.article3 = Article.objects.create(
            title="test Article 3",
            content="test article",
            author=self.journalist,
            created_at=datetime.now(),
            publisher=self.journalist.publisher,
            approved=True
        )
        self.url = reverse('newsletter:api_articles')

    def test_list_articles_endpoint(self):
        """Test GET /api/articles"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], self.article1.title)
        self.assertEqual(response.data[1]['title'], self.article3.title)

    def test_create_article(self):
        """Test POST /api/articles"""
        data = {"title": "test Article 4",
                "content": "test",
                "author": self.journalist.id,
                "created_at": datetime.now(),
                "publisher": self.journalist.publisher.name,
                "approved": False}

        # trying to create article as reader
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # trying to create article as journalist
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_j}")
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'test Article 4')


class SingleArticleAPITestCase(APITestCase):
    def setUp(self):
        self.testpublisher = Publisher.objects.create(
            name="testpublisher"
        )

        self.User = get_user_model()
        self.journalist = self.User.objects.create_user(
            username='journalist',
            email='journalist@test.com',
            password='password',
            publisher=self.testpublisher
        )
        self.reader = self.User.objects.create_user(
            username='reader',
            email='reader@test.com',
            password='password',
            publisher=None
        )
        self.editor = self.User.objects.create_user(
            username='editor',
            email='editor@test.com',
            password='password',
            publisher=self.testpublisher
        )
        self.journalist.groups.add(create_journalist())
        self.token_j = Token.objects.create(user=self.journalist)

        self.reader.groups.add(create_reader())
        self.token_r = Token.objects.create(user=self.reader)

        self.editor.groups.add(create_editor())
        self.token_e = Token.objects.create(user=self.editor)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_r}")

        self.article1 = Article.objects.create(
            title="test Article 1",
            content="test article",
            author=self.journalist,
            created_at=datetime.now(),
            publisher=self.journalist.publisher,
            approved=False
        )

        self.url = reverse(
            'newsletter:api_article', kwargs={'article_id': self.article1.pk})

    def test_api_display_article(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.article1.title)

    def test_api_edit_article_reader(self):
        data = {"title": "test Article updated!",
                "content": "test",
                "author": self.journalist.id,
                "created_at": datetime.now(),
                "publisher": self.journalist.publisher.name,
                "approved": False}

        # sending edit request as reader
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, "You do not have permission to edit articles.")

    def test_api_edit_article_journalist(self):
        data = {"title": "test Article updated!",
                "content": "test",
                "author": self.journalist.id,
                "created_at": datetime.now(),
                "publisher": self.journalist.publisher.name,
                "approved": False}

        # sending edit request as journalist
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_j}")
        response = self.client.put(self.url, data, format='json')
        updated_response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            updated_response.data['title'], "test Article updated!")

        data = {"title": "test Article updated!",
                "content": "test",
                "author": self.journalist.id,
                "created_at": datetime.now(),
                "publisher": self.journalist.publisher.name,
                "approved": True}

        response = self.client.put(self.url, data, format='json')
        updated_response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(updated_response.data['approved'], False)

    def test_api_edit_article_editor(self):
        data = {"title": "test Article updated!2",
                "content": "test",
                "author": self.journalist.id,
                "created_at": datetime.now(),
                "publisher": self.journalist.publisher.name,
                "approved": False}
        # sending edit request as editor
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_e}")
        response = self.client.put(self.url, data, format='json')
        updated_response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            updated_response.data['title'], "test Article updated!2")

        data = {"title": "test Article updated!2",
                "content": "test",
                "author": self.journalist.id,
                "created_at": datetime.now(),
                "publisher": self.journalist.publisher.name,
                "approved": True}
        response = self.client.put(self.url, data, format='json')
        updated_response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_response.data['approved'], True)

    def test_api_delete_article_reader(self):
        response = self.client.delete(self.url)
        updated_response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, "You do not have permission to delete articles.")
        self.assertEqual(updated_response.data['title'], self.article1.title)

    def test_api_delete_article_journalist(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_j}")
        response = self.client.delete(self.url)
        updated_response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(updated_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(updated_response.data, "Article does not exist")

    def test_api_delete_article_editor(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_e}")
        response = self.client.delete(self.url)
        updated_response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(updated_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(updated_response.data, "Article does not exist")
