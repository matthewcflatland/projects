from django.urls import path
from . import views

urlpatterns = [
    path(
        "api/articles/",
        views.api_view_articles,
        name="api_articles"
    ),
    path(
        "api/articles/<int:article_id>/",
        views.api_retrieve_article,
        name="api_article"
    ),
    path(
        "api/articles/subscribed/",
        views.api_view_subscriptions,
        name="api_subscribed"
    ),
    path(
        "api/approved/",
        views.api_approved,
        name="api_approved"
    )
]
