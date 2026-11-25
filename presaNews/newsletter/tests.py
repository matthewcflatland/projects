from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from grabsomore.utils import (
    create_reader,
    create_journalist,
    create_editor
    )
from .models import Article, Newsletter, Publisher
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
        self.url = reverse('api_articles')

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
            'api_article', kwargs={'article_id': self.article1.pk})

    def test_api_display_article(self):
        """testing API endpoint displaying single article"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.article1.title)

    def test_api_edit_article_reader(self):
        """testing API endpoint reader role editing an article"""
        data = {"title": "test Article updated!",
                "content": "test",
                "author": self.journalist.id,
                "created_at": datetime.now(),
                "publisher": self.journalist.publisher.name,
                "approved": False}

        # sending edit request as reader
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data, "You do not have permission to edit articles.")

    def test_api_edit_article_journalist(self):
        """testing API endpoint journalist role editing an article"""
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

    @patch('newsletter.views.approve_article')
    def test_api_edit_article_editor(self, mock_fetch):
        """testing API endpoint editor role editing an article"""
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
        mock_fetch.return_value = {
                "title": "test Article updated!2",
                "content": "test",
                "author": self.journalist.id,
                "created_at": datetime.now(),
                "publisher": self.journalist.publisher.name,
                "approved": True}
        response = self.client.put(self.url, data, format='json')
        updated_response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_fetch.assert_called()
        self.assertEqual(mock_fetch.return_value['approved'], True)

    def test_api_delete_article_reader(self):
        """testing API endpoint reader role deleting an article"""
        response = self.client.delete(self.url)
        updated_response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data, "You do not have permission to delete articles.")
        self.assertEqual(updated_response.data['title'], self.article1.title)

    def test_api_delete_article_journalist(self):
        """testing API endpoint journalist role deleting an article"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_j}")
        response = self.client.delete(self.url)
        updated_response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            updated_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(updated_response.data, "Article does not exist")

    def test_api_delete_article_editor(self):
        """testing API endpoint editor role deleting an article"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_e}")
        response = self.client.delete(self.url)
        updated_response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            updated_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(updated_response.data, "Article does not exist")


class APISubscribeTestCase(APITestCase):
    def setUp(self):
        self.testpublisher = Publisher.objects.create(
            name="testpublisher"
        )
        self.testpublisher2 = Publisher.objects.create(
            name="testpublisher2"
        )
        self.User = get_user_model()
        self.reader = self.User.objects.create_user(
            username='reader',
            email='reader@test.com',
            password='password',
            publisher=None
        )

        self.journalist = self.User.objects.create_user(
            username='journalist',
            email='journalist@test.com',
            password='password',
            publisher=self.testpublisher
        )
        self.journalist2 = self.User.objects.create_user(
            username='journalist2',
            email='journalist2@test.com',
            password='password',
            publisher=self.testpublisher2
        )
        self.journalist3 = self.User.objects.create_user(
            username='journalist3',
            email='journalist3@test.com',
            password='password',
            publisher=self.testpublisher
        )
        self.journalist4 = self.User.objects.create_user(
            username='journalist4',
            email='journalist4@test.com',
            password='password',
            publisher=self.testpublisher2
        )
        self.reader.groups.add(create_reader())
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
            author=self.journalist2,
            created_at=datetime.now(),
            publisher=self.journalist2.publisher,
            approved=True
        )
        self.article3 = Article.objects.create(
            title="test Article 3",
            content="test article",
            author=self.journalist3,
            created_at=datetime.now(),
            publisher=self.journalist3.publisher,
            approved=True
        )
        self.article4 = Article.objects.create(
            title="test Article 4",
            content="test article",
            author=self.journalist4,
            created_at=datetime.now(),
            publisher=self.journalist4.publisher,
            approved=True
        )

        self.url = reverse(
            'api_subscribed')

    def test_journalist_subscription(self):
        """testing API Endpoint pulling articles from journalist"""
        # adding first journalist to subscription
        self.reader.journalist_subscriptions.set([self.journalist])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], self.article1.title)

        # adding another journalist to subscription
        self.reader.journalist_subscriptions.add(self.journalist3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["title"], self.article1.title)
        self.assertEqual(response.data[1]["title"], self.article3.title)

    def test_publisher_subscription(self):
        """testing API Endpoint pulling articles from publisher"""
        # adding publisher to subscription
        self.reader.publisher_subscriptions.set([self.testpublisher2])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["title"], self.article2.title)
        self.assertEqual(response.data[1]["title"], self.article4.title)

    def test_both_subscription(self):
        """testing API Endpoint pulling articles from both publisher
        and journalist"""
        # adding journalist and publisher to subscription
        self.reader.journalist_subscriptions.set([self.journalist])
        self.reader.publisher_subscriptions.set([self.testpublisher2])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]["title"], self.article1.title)
        self.assertEqual(response.data[1]["title"], self.article2.title)
        self.assertEqual(response.data[2]["title"], self.article4.title)


class NewsletterTestCase(TestCase):
    def setUp(self):
        self.client = Client()
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

        self.reader.groups.add(create_reader())

        self.editor.groups.add(create_editor())

        self.newsletter1 = Newsletter.objects.create(
            title="Newsletter 1 Test",
            description="test description",
            author=self.journalist,
            created_at=datetime.now()
        )
        self.newsletter2 = Newsletter.objects.create(
            title="Newsletter 2 Test",
            description="test description",
            author=self.journalist,
            created_at=datetime.now()
        )
        self.newsletter3 = Newsletter.objects.create(
            title="Newsletter 3 Test",
            description="test description",
            author=self.journalist,
            created_at=datetime.now()
        )
        self.newsletter4 = Newsletter.objects.create(
            title="Newsletter 4 Test",
            description="test description",
            author=self.journalist,
            created_at=datetime.now()
        )

    def test_display_newsletter(self):
        """testing newsletters can been displayed"""
        self.client.login(username="reader", password="password")
        response = self.client.get(reverse('newsletter:list_newsletters'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.newsletter1.title, response.content.decode())

    def test_create_newsletter(self):
        """testing creating newsletters based on user role"""
        url = reverse('newsletter:create_newsletter')
        data = {"title": "test newsletter", "description": "description"}
        data2 = {"title": "test newsletter2", "description": "description"}

        self.client.login(username="reader", password="password")
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "You do not have permission to create newsletters.",
            response.content.decode())
        with self.assertRaises(Newsletter.DoesNotExist):
            Newsletter.objects.get(title="test newsletter")
        self.client.logout()

        self.client.login(username="editor", password="password")
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        newsletter = Newsletter.objects.get(title="test newsletter")
        self.assertEqual(newsletter.title, "test newsletter")
        self.client.logout()

        self.client.login(username="journalist", password="password")
        response = self.client.post(url, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        newsletter = Newsletter.objects.get(title="test newsletter2")
        self.assertEqual(newsletter.title, "test newsletter2")

    def test_delete_newsletter(self):
        """testing deleting newsletters based on user role"""
        url = reverse(
            "newsletter:delete_newsletter",
            kwargs={'newsletter_id': self.newsletter4.pk})
        url2 = reverse(
            "newsletter:delete_newsletter",
            kwargs={'newsletter_id': self.newsletter3.pk})

        self.client.login(username="reader", password="password")
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "You do not have permission to delete newsletters",
            response.content.decode())
        newsletter = Newsletter.objects.get(id=self.newsletter4.pk)
        self.assertEqual(newsletter.title, self.newsletter4.title)
        self.client.logout()

        self.client.login(username="editor", password="password")
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        with self.assertRaises(Newsletter.DoesNotExist):
            Newsletter.objects.get(id=self.newsletter4.id)
        self.client.logout()

        self.client.login(username="journalist", password="password")
        response = self.client.post(url2)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        with self.assertRaises(Newsletter.DoesNotExist):
            Newsletter.objects.get(id=self.newsletter3.id)

    def test_edit_newsletter(self):
        """testing editing newsletters based on user role"""
        url = reverse(
            "newsletter:edit_newsletter",
            kwargs={'newsletter_id': self.newsletter4.pk})
        data = {"new_title": "updated1", "new_description": "description"}
        data2 = {"new_title": "updated2", "new_description": "description"}

        self.client.login(username="reader", password="password")
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "You do not have permission to edit newsletters.",
            response.content.decode())
        newsletter = Newsletter.objects.get(id=self.newsletter4.pk)
        self.assertNotEqual(newsletter.title, "updated1")
        self.client.logout()

        self.client.login(username="editor", password="password")
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        newsletter = Newsletter.objects.get(id=self.newsletter4.pk)
        self.assertEqual(newsletter.title, "updated1")
        self.client.logout()

        self.client.login(username="journalist", password="password")
        response = self.client.post(url, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        newsletter = Newsletter.objects.get(id=self.newsletter4.pk)
        self.assertEqual(newsletter.title, "updated2")
