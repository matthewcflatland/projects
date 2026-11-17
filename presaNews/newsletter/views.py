from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from .models import Article, Newsletter, Publisher
from grabsomore.models import CustomUser
from .utils import build_email


def view_subscriptions(request):
    user = request.user
    journalists = user.journalist_subscriptions.all()
    publishers = user.publisher_subscriptions.all()

    j_articles = []
    p_articles = []
    for j in journalists:
        temp = Article.objects.filter(author=j.id)
        j_articles.append(temp)

    for p in publishers:
        temp = Article.objects.filter(publisher=p)
        p_articles.append(temp)

    return render(
        request,
        "newsletter/view_subscriptions.html",
        {"p_articles": p_articles,
         "j_articles": j_articles}
    )


def subscribe_journalist(request, article_id):
    user = request.user
    article = Article.objects.get(id=article_id)
    author = article.author
    journalist = CustomUser.objects.get(id=author.id)
    user.journalist_subscriptions.add(journalist)
    return render(
                request,
                "newsletter/list_articles.html",
                {"notification": f"Subscribed to {journalist}."}
            )


def subscribe_publisher(request, article_id):
    user = request.user
    article = Article.objects.get(id=article_id)
    publisher = Publisher.objects.get(id=article.publisher.id)
    user.publisher_subscriptions.add(publisher)
    return render(
                request,
                "newsletter/list_articles.html",
                {"notification": f"Subscribed to {publisher}."}
            )


def approve_article(article):
    journalist = article.author.id
    publisher = article.publisher

    users = CustomUser.objects.all()

    temp = []
    for user in users:
        temp_j = []
        temp_j = user.journalist_subscriptions.all()
        for j in temp_j:
            if journalist == j.id:
                temp.append(user)

        temp_p = []
        temp_p = user.publisher_subscriptions.all()
        for p in temp_p:
            if publisher == p:
                if user in temp:
                    pass
                else:
                    temp.append(user)

    users = temp

    emails = build_email(users, article)
    for email in emails:
        email.send()


def create_article(request):
    '''Creates a new article'''
    user = request.user
    if user.has_perms(["newsletter.add_article"]):

        if request.method == "POST":
            title = request.POST.get("title")
            content = request.POST.get("content")
            publisher = Publisher.objects.get(name=user.publisher)

            if not title or not content:
                return render(
                    request,
                    "newsletter/create_article.html",
                    {"error": "Title and Content are required."}
                    )

            article = Article.objects.create(
                title=title,
                content=content,
                author=user,
                created_at=datetime.now(),
                approved=False,
                publisher=publisher
            )

            return redirect(reverse("newsletter:list_articles"))

        # Show form when page is first loaded (GET request)
        return render(
            request, "newsletter/create_article.html"
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
    user_group = user.groups.first()
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

            if not new_title or not new_content:
                return render(
                    request,
                    "newsletter/edit_article.html",
                    {"error": "Title and Content are required."}
                    )

            article.title = new_title
            article.content = new_content
            if user_group.name != "Editor":
                article.save()
            else:
                if user_group.name == "Editor":
                    approve = request.POST.get("approve")
                    if article.approved:
                        article.save()
                    else:
                        if approve == "True":
                            article.approved = approve
                            article.save()
                            approve_article(article)
                        else:
                            article.save()

            return redirect(reverse("newsletter:list_articles"))

        # Show form when page is first loaded (GET request)
        return render(
            request, "newsletter/edit_article.html",
            {"article": article, "user_group": user_group}
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
    user_group = user.groups.first()

    # checks if user has permission to view articles
    if user.has_perms(["newsletter.view_article"]):
        temp = Article.objects.all()
        edit_perm = False

        # checks if user has permission to edit articles
        if user.has_perms(["newsletter.change_article"]):
            edit_perm = True

            # checks if user is a Journalist
            if user_group.name == "Journalist":
                articles = []
                for item in temp:
                    if item.author == user:
                        articles.append(item)
            else:
                articles = temp

        else:
            articles = []
            for item in temp:
                if item.approved:
                    articles.append(item)

        # checks if user can create articles
        if user.has_perms(["newsletter.add_article"]):
            create_perm = True
        else:
            create_perm = False

        return render(
            request, "newsletter/list_articles.html", {
                "articles": articles,
                "edit_perm": edit_perm,
                "create_perm": create_perm,
                "user_group": user_group}
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


def create_newsletter(request):
    '''Creates a new Newsletter'''
    user = request.user
    if user.has_perms(["newsletter.add_newsletter"]):

        if request.method == "POST":
            title = request.POST.get("title")
            content = request.POST.get("content")
            publisher = Publisher.objects.get(name=user.publisher)

            if not title or not content:
                return render(
                    request,
                    "newsletter/create_newsletter.html",
                    {"error": "Title and Content are required."}
                    )

            newsletter = Newsletter.objects.create(
                title=title,
                content=content,
                author=user,
                created_at=datetime.now(),
                approved=False,
                publisher=publisher
            )

            return redirect(reverse("newsletter:list_newsletters"))

        # Show form when page is first loaded (GET request)
        return render(
            request, "newsletter/create_newsletter.html"
        )

    else:
        return render(
            request,
            "newsletter/list_newsletters.html",
            {"error": "You do not have permission to create newsletters."}
        )


def delete_newsletter(request, newsletter_id):
    '''deletes requested newsletter'''
    user = request.user
    if user.has_perms(["newsletter.delete_newsletter"]):
        try:
            newsletter = Newsletter.objects.get(id=newsletter_id)
            newsletter.delete()
            return HttpResponseRedirect(reverse("newsletter:list_newsletters"))

        except Newsletter.DoesNotExist:
            return render(
                request,
                "newsletter/list_newsletters.html",
                {"error": "The newsletter does not exist."}
            )


def edit_newsletter(request, newsletter_id):
    '''Renders edit newsletter page with newsletter information'''
    user = request.user
    if user.has_perms(["newsletter.change_newsletter"]):
        try:
            newsletter = Newsletter.objects.get(id=newsletter_id)

        except Newsletter.DoesNotExist:
            return render(
                request,
                "newsletter/list_newsletters.html",
                {"error": "The newsletter does not exist."}
            )

        if request.method == "POST":
            new_title = request.POST.get("new_title")
            new_content = request.POST.get("new_content")
            approve = request.POST.get("approve")

            if not new_title or not new_content:
                return render(
                    request,
                    "newsletter/edit_newsletter.html",
                    {"error": "Title and Content are required."}
                    )

            newsletter.title = new_title
            newsletter.content = new_content
            if approve is None:
                approve = False
                newsletter.approved = approve
            else:
                newsletter.approved = approve
            newsletter.save()

            return redirect(reverse("newsletter:list_newsletters"))

        # Show form when page is first loaded (GET request)
        return render(
            request,
            "newsletter/edit_newsletter.html",
            {"newsletter": newsletter}
        )

    else:
        return render(
            request,
            "newsletter/list_newsletters.html",
            {"error": "You do not have permission to edit newsletters."}
        )


def list_newsletters(request):
    '''Renders list of all newsletters on the page'''
    user = request.user

    if user.has_perms(["newsletter.view_newsletter"]):
        temp = Newsletter.objects.all()
        edit_perm = False
        if user.has_perms(["newsletter.change_newsletter"]):
            edit_perm = True
            newsletters = temp
        else:
            newsletters = []
            for item in temp:
                if item.approved:
                    newsletters.append(item)
        if user.has_perms(["newsletter.add_article"]):
            create_perm = True
        else:
            create_perm = False
        return render(
            request, "newsletter/list_newsletters.html", {
                "newsletters": newsletters,
                "edit_perm": edit_perm,
                "create_perm": create_perm}
        )
    else:
        return render(
            request,
            "grabsomore/welcome.html",
            {"error": "You do not have permission to view newsletters."},
        )


def display_newsletter(request, newsletter_id):
    '''Renders a requested newsletter page with newsletter information'''
    newsletter = Newsletter.objects.get(id=newsletter_id)

    return render(
        request, "newsletter/newsletter.html", {"newsletter": newsletter}
    )
