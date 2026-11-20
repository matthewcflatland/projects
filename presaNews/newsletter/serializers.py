from rest_framework import serializers
from .models import Article, Newsletter, Publisher


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
            "create_at",
            "articles"
        ]


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ["name"]
