from rest_framework import serializers
from .models import Article, Newsletter, Publisher
from django.contrib.auth import get_user_model


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            "title",
            "content",
            "author",
            "created_at",
            "publisher",
            "approved"
            ]


class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = [
            "title",
            "description",
            "author",
            "created_at",
            "articles"
        ]


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ["name"]


class UserSerialiser(serializers.ModelSerializer):
    class Meta:
        User = get_user_model()
        model = User
        fields = [
            "username",
            "password",
            "email",
            "publisher",
            "publisher_subscriptions",
            "journalist_subscriptions"
        ]
