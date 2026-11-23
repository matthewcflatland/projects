from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .models import Article, Newsletter, Publisher
from grabsomore.models import CustomUser
from .utils import build_email
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
    )
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import ArticleSerializer


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def api_view_subscriptions(request):
    '''API endpoint to retrieve user's subscriptions'''
    user = request.user

    # gets a qeury of users subscriptions
    journalists = user.journalist_subscriptions.all()
    publishers = user.publisher_subscriptions.all()
    articles = []

    # iterates through subscription list and put unique
    # articles in a new list
    for journalist in journalists:
        temp = Article.objects.filter(author=journalist)
        for item in temp:
            if item.approved:
                articles.append(item)

    for publisher in publishers:
        temp = Article.objects.filter(publisher=publisher)
        for item in temp:
            if item not in articles and item.approved:
                articles.append(item)

    serializer = ArticleSerializer(articles, many=True)

    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'Delete'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def api_retrieve_article(request, article_id):
    '''API endpoint for retriving an article,
    editing an article and deleting an article'''
    # get request for retriving an article
    if request.method == "GET":
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return Response(
                data="Article does not exist",
                status=status.HTTP_404_NOT_FOUND
                )

        serializer = ArticleSerializer(article)

        return Response(data=serializer.data)

    # put request to edit an article
    elif request.method == "PUT":
        user = request.user
        user_group = user.groups.first()
        if user.has_perms(["newsletter.change_article"]):
            try:
                article = Article.objects.get(id=article_id)

            except Article.DoesNotExist:
                return Response(
                    data="Article does not exist",
                    status=status.HTTP_404_NOT_FOUND,
                    )
            # retrieves data from request
            new_title = request.data.get("title")
            new_content = request.data.get("content")
            approve = request.data.get("approved")

            if not new_title or not new_content:
                error = "Title and Content are required."
                return Response(
                    data=error,
                    status=status.HTTP_400_BAD_REQUEST,
                    )
            # updates article with new information
            article.title = new_title
            article.content = new_content
            # verifies user is an Editor before approving article
            if approve is True:
                if user_group.name == "Editor":
                    article.approved = approve
                    article.save()
                    approve_article(article)
                else:
                    return Response(
                        data="Do not have authorization to approve articles.",
                        status=status.HTTP_403_FORBIDDEN
                    )
            else:
                article.save()

            serializer = ArticleSerializer(article)

            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK,
                )

        else:
            error = "You do not have permission to edit articles."
            return Response(data=error, status=status.HTTP_403_FORBIDDEN)
    # delete request deletes article
    elif request.method == "DELETE":
        user = request.user
        # checks if user has permission to delete articles
        if user.has_perms(["newsletter.delete_article"]):
            try:
                # if article exists then delete
                article = Article.objects.get(id=article_id)
                article.delete()
                return Response(
                    data="Deleted Successfully",
                    status=status.HTTP_204_NO_CONTENT,
                    )

            except Article.DoesNotExist:
                return Response(
                    data="Article does not exist",
                    status=status.HTTP_404_NOT_FOUND,
                    )
        else:
            return Response(
                data="You do not have permission to delete articles.",
                status=status.HTTP_403_FORBIDDEN,
            )

    else:
        return Response(
            data="Method Not Allowed.",
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )


@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def api_view_articles(request):
    '''API Endpoint for retriving all articles and creating a new article'''

    # get request to retrieve all articles
    if request.method == "GET":
        articles = Article.objects.filter(approved=True)

        serializer = ArticleSerializer(articles, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    # Post request to create a new article
    elif request.method == "POST":
        user = request.user
        # check if user has permission to create articles
        if user.has_perms(["newsletter.add_article"]):

            # get data from post request
            title = request.data.get("title")
            content = request.data.get("content")
            publisher = Publisher.objects.get(name=user.publisher)

            if not title or not content:
                error = "Title and Content are required."
                return Response(
                    data=error,
                    status=status.HTTP_400_BAD_REQUEST,
                    safe=False)

            # create new article with data given
            article = Article.objects.create(
                title=title,
                content=content,
                author=user,
                created_at=datetime.now(),
                approved=False,
                publisher=publisher
            )

            serializer = ArticleSerializer(article)

            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED)

        else:
            error = "You do not have permission to create articles."
            return Response(
                data=error,
                status=status.HTTP_403_FORBIDDEN,
                )
    else:
        return Response(
            data="Method Not Allowed.",
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            safe=False)


@login_required(login_url=reverse_lazy("grabsomore:login"))
def view_subscriptions(request):
    '''renders view_subscription.html with articles
      that user is subscribed to'''
    user = request.user

    # creates lists of user's subscriptions
    journalists = user.journalist_subscriptions.all()
    publishers = user.publisher_subscriptions.all()
    j_articles = []
    p_articles = []

    # iteratis though the subscriptions to create a new list
    # with unique articles
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


@login_required(login_url=reverse_lazy("grabsomore:login"))
def subscribe_journalist(request, article_id):
    '''subscribes to journalist'''
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


@login_required(login_url=reverse_lazy("grabsomore:login"))
def subscribe_publisher(request, article_id):
    '''subscribes to publisher'''
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
    '''emails all subscribed users with newly approved article'''
    # get approved article's author and publisher
    journalist = article.author.id
    publisher = article.publisher

    users = CustomUser.objects.all()

    # iterates through each user subscriptions for author or publisher
    temp = []
    for user in users:
        temp_j = []
        temp_j = user.journalist_subscriptions.all()
        for j in temp_j:
            if journalist == j.id:
                temp.append(user)
                break

        temp_p = []
        temp_p = user.publisher_subscriptions.all()
        for p in temp_p:
            if publisher == p:
                if user in temp:
                    pass
                else:
                    temp.append(user)
                break

    # sends article in an email to each subscribed user
    users = temp
    emails = build_email(users, article)
    for email in emails:
        email.send()


@login_required(login_url=reverse_lazy("grabsomore:login"))
def create_article(request):
    '''Creates a new article'''
    user = request.user
    # checks if user has permission to create articles
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


@login_required(login_url=reverse_lazy("grabsomore:login"))
def delete_article(request, article_id):
    '''deletes requested article'''
    user = request.user
    # checks if user has permission to delete articles
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


@login_required(login_url=reverse_lazy("grabsomore:login"))
def edit_article(request, article_id):
    '''Renders edit article page with article information'''
    user = request.user
    user_group = user.groups.first()
    # checks if user has permission to edit articles
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

            # checks if user is an editor and if they can approve the article
            if user_group.name == "Editor":
                if article.approved:
                    article.save()
                else:
                    if approve == "True":
                        article.approved = approve
                        article.save()
                        approve_article(article)
                    else:
                        article.save()
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


@login_required(login_url=reverse_lazy("grabsomore:login"))
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


@login_required(login_url=reverse_lazy("grabsomore:login"))
def display_article(request, article_id):
    '''Renders a requested article page with article information'''
    article = Article.objects.get(id=article_id)

    return render(
        request, "newsletter/article.html", {"article": article}
    )


@login_required(login_url=reverse_lazy("grabsomore:login"))
def create_newsletter(request):
    '''Creates a new Newsletter'''
    user = request.user
    # checks if user has permission to create newsletters
    if user.has_perms(["newsletter.add_newsletter"]):

        if request.method == "POST":
            title = request.POST.get("title")
            description = request.POST.get("description")
            publisher = Publisher.objects.get(name=user.publisher)

            if not title or not description:
                return render(
                    request,
                    "newsletter/create_newsletter.html",
                    {"error": "Title and Description are required."}
                    )

            newsletter = Newsletter.objects.create(
                title=title,
                description=description,
                author=user,
                created_at=datetime.now()
            )

            return redirect(reverse("newsletter:list_newsletters"))

        # Show form when page is first loaded (GET request)
        return render(
            request,
            "newsletter/create_newsletter.html"
        )

    else:
        return render(
            request,
            "newsletter/list_newsletters.html",
            {"error": "You do not have permission to create newsletters."}
        )


@login_required(login_url=reverse_lazy("grabsomore:login"))
def delete_newsletter(request, newsletter_id):
    '''deletes requested newsletter'''
    user = request.user
    # checks if user has permission to delete newsletters
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
    else:
        return render(
            request,
            "newsletter/list_newsletters.html",
            {"error": "You do not have permission to delete newsletters"}
        )


@login_required(login_url=reverse_lazy("grabsomore:login"))
def edit_newsletter(request, newsletter_id):
    '''Renders edit newsletter page with newsletter information'''
    user = request.user
    # checks if user has permission to edit newsletters
    if user.has_perms(["newsletter.change_newsletter"]):
        try:
            newsletter = Newsletter.objects.get(id=newsletter_id)
            articles = newsletter.articles.all()

        except Newsletter.DoesNotExist:
            return render(
                request,
                "newsletter/list_newsletters.html",
                {"error": "The newsletter does not exist."}
            )

        if request.method == "POST":
            new_title = request.POST.get("new_title")
            new_description = request.POST.get("new_description")
            article = request.POST.get("articles")

            if not new_title or not new_description:
                return render(
                    request,
                    "newsletter/edit_newsletter.html",
                    {"error": "Title and Description are required."}
                    )

            newsletter.title = new_title
            newsletter.description = new_description
            newsletter.articles.remove(article)
            newsletter.save()

            return redirect(reverse("newsletter:list_newsletters"))

        # Show form when page is first loaded (GET request)

        return render(
            request,
            "newsletter/edit_newsletter.html",
            {"newsletter": newsletter,
             "articles": articles}
        )

    else:
        return render(
            request,
            "newsletter/list_newsletters.html",
            {"error": "You do not have permission to edit newsletters."}
        )


@login_required(login_url=reverse_lazy("grabsomore:login"))
def list_newsletters(request):
    '''Renders list of all newsletters on the page'''
    user = request.user

    if user.has_perms(["newsletter.view_newsletter"]):
        newsletters = Newsletter.objects.all()
        edit_perm = False
        if user.has_perms(["newsletter.change_newsletter"]):
            edit_perm = True
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


@login_required(login_url=reverse_lazy("grabsomore:login"))
def display_newsletter(request, newsletter_id):
    '''Renders a requested newsletter page with newsletter information'''
    newsletter = Newsletter.objects.get(id=newsletter_id)
    articles = newsletter.articles.all()

    return render(
        request,
        "newsletter/newsletter.html",
        {"newsletter": newsletter, "articles": articles}
    )


@login_required(login_url=reverse_lazy("grabsomore:login"))
def add_article(request, newsletter_id):
    '''Renders edit newsletter page with newsletter information'''
    user = request.user
    if user.has_perms(["newsletter.change_newsletter"]):
        try:
            newsletter = Newsletter.objects.get(id=newsletter_id)
            articles = list(newsletter.articles.all())

        except Newsletter.DoesNotExist:
            return render(
                request,
                "newsletter/add_article.html",
                {"error": "The newsletter does not exist."}
            )

        if request.method == "POST":
            temp_articles = request.POST.getlist("articles")
            new_articles = []
            for temp in temp_articles:
                temp_article = Article.objects.get(id=temp)
                new_articles.append(temp_article)

            for article in new_articles:
                if article in articles:
                    pass
                else:
                    newsletter.articles.add(article)

            return redirect(reverse("newsletter:list_newsletters"))

        # Show form when page is first loaded (GET request)
        all_articles = list(Article.objects.all())
        if articles is None:
            pass
        else:
            for article in all_articles:
                for a in articles:
                    if a == article:
                        all_articles.remove(a)
                        break
        return render(
            request,
            "newsletter/add_article.html",
            {"newsletter": newsletter,
             "all_articles": all_articles}
        )

    else:
        return render(
            request,
            "newsletter/add_article.html",
            {"error": "You do not have permission to edit newsletters."}
        )
