from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=200)
    # The title of the article

    content = models.TextField()
    # The main content of the article

    author = models.ForeignKey("Journalist", on_delete=models.CASCADE)
    # The user who wrote the article; if the user is deleted, the article is also deleted

    created_at = models.DateTimeField(auto_now_add=True)
    # The date and time when the article was created; set automatically when the article is first created

    approved = models.BooleanField(default=False)

    publisher = models.ForeignKey("Publisher", on_delete=models.CASCADE)

    def __str__(self):
        # This makes it easier to see the article’s title when printing or in admin pages
        return self.title


class Publisher(models.Model):
    name = models.CharField(max_length=100)
    # The name of the publisher, like "Tech News Daily"

    def __str__(self):
        # This makes it easier to see the publisher’s name when printing or in admin pages
        return self.name


class Newsletter(models.Model):
    title = models.CharField(max_length=200)
    # The title of the newsletter

    description = models.TextField()
    # A brief description of the newsletter

    created_at = models.DateTimeField(auto_now_add=True)
    # The date and time when the newsletter was created; set automatically when the newsletter is first created

    author = models.ForeignKey("Journalist", on_delete=models.CASCADE)
    # The user who created the newsletter; if the user is deleted, the newsletter is also deleted

    articles = models.ManyToManyField(Article, related_name="newsletters")

    def __str__(self):
        # This makes it easier to see the newsletter’s title when printing or in admin pages
        return self.title
