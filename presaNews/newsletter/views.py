from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from .models import Article, Newsletter, Publisher


def create_article(request):
    '''Renders edit article page with article information'''
    user = request.user
    if user.has_perms(["newsletter.create_article"]):

        if request.method == "POST":
            title = request.POST.get("=title")
            content = request.POST.get("=content")

            if not title or not content:
                return render(
                    request,
                    "newsletter/edit_article.html",
                    {"error": "Title and Content are required."}
                    )

            article = Article.objects.create(
                title=title,
                content=content,
                author=user,
                created_at=datetime.now(),
                approved=False,
                publisher=Publisher.objects.get()

            )


            return redirect(reverse("newsletter:list_articles"))

        # Show form when page is first loaded (GET request)
        return render(
            request, "newsletter/edit_article.html", {"article": article}
        )

    else:
        return render(
            request,
            "newsletter/list_articles.html",
            {"error": "You do not have permission to create articles."}
        )


def delete_article(request, article_id):
    '''deletes requested article'''
    user = request.user
    if user.has_perms(["newsletter.delete_article"]):
        try:
            article = Article.objects.get(id=article_id)
            article.delete()
            return HttpResponseRedirect(reverse("newsletter:list_articles"))

        except Article.DoesNotExist:
            return render(
                request,
                "newsletter/list_articles.html",
                {"error": "The article does not exist."}
            )


def edit_article(request, article_id):
    '''Renders edit article page with article information'''
    user = request.user
    if user.has_perms(["newsletter.change_article"]):
        try:
            article = Article.objects.get(id=article_id)

        except Article.DoesNotExist:
            return render(
                request,
                "newsletter/list_articles.html",
                {"error": "The article does not exist."}
            )

        if request.method == "POST":
            new_title = request.POST.get("new_title")
            new_content = request.POST.get("new_content")
            approve = request.POST.get("approve")

            if not new_title or not new_content:
                return render(
                    request,
                    "newsletter/edit_article.html",
                    {"error": "Title and Content are required."}
                    )

            article.title = new_title
            article.content = new_content
            article.approved = approve
            article.save()

            return redirect(reverse("newsletter:list_articles"))

        # Show form when page is first loaded (GET request)
        return render(
            request, "newsletter/edit_article.html", {"article": article}
        )

    else:
        return render(
            request,
            "newsletter/list_articles.html",
            {"error": "You do not have permission to edit articles."}
        )


def list_articles(request):
    '''Renders list of all articles on the page'''
    user = request.user

    if user.has_perms(["newsletter.view_article"]):
        temp = Article.objects.all()
        edit_perm = False
        if user.has_perms(["newsletter.change_article"]):
            edit_perm = True
            articles = temp
        else:
            articles = []
            for item in temp:
                if item.approved:
                    articles.append(item)

        return render(
            request, "newsletter/list_articles.html", {
                "articles": articles, "edit_perm": edit_perm}
        )
    else:
        return render(
            request,
            "grabsomore/welcome.html",
            {"error": "You do not have permission to view articles."},
        )


def display_article(request, article_id):
    '''Renders a requested article page with article information'''
    article = Article.objects.get(id=article_id)

    return render(
        request, "newsletter/article.html", {"article": article}
    )
