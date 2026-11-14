from django.urls import path
from . import views

app_name = "newsletter"

urlpatterns = [
    path("", views.list_articles, name="list_articles"),
    path(
        "article/<int:article_id>/",
        views.display_article,
        name="article",
        ),
    path(
        "edit_article/<int:article_id>/",
        views.edit_article,
        name="edit_article"
        ),
    path(
        "delete_article/<int:article_id>/",
        views.delete_article,
        name="delete_article"
    ),
]
