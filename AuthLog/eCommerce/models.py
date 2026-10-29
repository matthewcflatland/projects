from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    # The name of the product, like "T-shirt" or "Laptop"

    description = models.TextField(blank=True)
    # A longer description of the product; it’s optional (can be empty)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    # The price of the product, with up to 10 digits total and 2 decimal places for cents

    stock = models.PositiveIntegerField()
    # How many items are available in stock (only positive numbers allowed)

    store = models.ForeignKey(
        "Store", on_delete=models.CASCADE, related_name="products", null=True, blank=True
    )

    def __str__(self):
        # This makes it easier to see the product’s name when printing or in admin pages
        return self.name


class Store(models.Model):
    name = models.CharField(max_length=100)
    # The name of the store, like "My Online Shop"

    owner = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE
    )
    # The user who owns this store; if the user is deleted, the store is also deleted

    def __str__(self):
        # This makes it easier to see the store’s name when printing or in admin pages
        return self.name


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    # The product that this review is for; if the product is deleted, the review is also deleted

    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    # The user who wrote the review; if the user is deleted, the review is also deleted

    rating = models.PositiveSmallIntegerField()
    # The rating given by the user, usually from 1 to 5

    comment = models.TextField(blank=True)
    # An optional comment from the user about the product

    created_at = models.DateTimeField(auto_now_add=True)
    # The date and time when the review was created; set automatically when the review is first created

    def __str__(self):
        # This makes it easier to see a summary of the review when printing or in admin pages
        return (f"Review for {self.product.name} by {self.user.username}\n"
                f"Rating: {self.rating}\n"
                f"Comment: {self.comment}")


class Order(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    # The user who placed the order; if the user is deleted, the order is also deleted

    products = models.ManyToManyField(Product, through="OrderItem")
    # The products included in this order; uses a through model to store quantity

    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    # The total price of the order, with up to 10 digits total and 2 decimal places for cents

    created_at = models.DateTimeField(auto_now_add=True)
    # The date and time when the order was created; set automatically when the order is first created

    def __str__(self):
        # This makes it easier to see a summary of the order when printing or in admin pages
        return f"Order #{self.id} by {self.user.username} - Total: ${self.total_price}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('order', 'product')  # Prevent duplicate product in same order
