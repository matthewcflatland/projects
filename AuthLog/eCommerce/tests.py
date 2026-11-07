from django.test import TestCase
from .models import Product, Store, Review, Order, OrderItem
from django.contrib.auth.models import User


# Create your tests here.
class ProductModelTest(TestCase):
    def setUp(self):
        # Create a Product object for testing
        user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        store = Store.objects.create(name="Test Store", owner=user)
        self.product = Product.objects.create(
            name="Test Product",
            description="This is a test product",
            price=9.99,
            stock=100,
            store=store,
        )

    def test_product_has_name(self):
        # Test that a Product object has the expected name
        self.assertEqual(self.product.name, "Test Product")

    def test_product_has_description(self):
        # Test that a Product object has the expected description
        self.assertEqual(self.product.description, "This is a test product")

    def test_product_has_price(self):
        # Test that a Product object has the expected price
        self.assertEqual(self.product.price, 9.99)

    def test_product_has_stock_quantity(self):
        # Test that a Product object has the expected stock quantity
        self.assertEqual(self.product.stock, 100)

    def test_product_create(self):
        # Test that a Product object can be created
        self.assertEqual(Product.objects.count(), 1)

    def test_product_delete(self):
        # Test that a Product object can be deleted
        self.product.delete()
        self.assertEqual(Product.objects.count(), 0)


class StoreModelTest(TestCase):
    def setUp(self):
        # Create a Store object for testing
        user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.store = Store.objects.create(name="Test Store", owner=user)

    def test_store_has_name(self):
        # Test that a Store object has the expected name
        self.assertEqual(self.store.name, "Test Store")

    def test_store_create(self):
        # Test that a Store object can be created
        self.assertEqual(Store.objects.count(), 1)

    def test_store_delete(self):
        # Test that a Store object can be deleted
        self.store.delete()
        self.assertEqual(Store.objects.count(), 0)


class ReviewModelTest(TestCase):
    def setUp(self):
        # Create a Product and User object for testing
        user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        store = Store.objects.create(name="Test Store", owner=user)
        product = Product.objects.create(
            name="Test Product",
            description="This is a test product",
            price=9.99,
            stock=100,
            store=store,
        )
        # Create a Review object for testing
        self.review = Review.objects.create(
            product=product, user=user, rating=5, comment="Great product!"
        )

    def test_review_has_rating(self):
        # Test that a Review object has the expected rating
        self.assertEqual(self.review.rating, 5)

    def test_review_has_comment(self):
        # Test that a Review object has the expected comment
        self.assertEqual(self.review.comment, "Great product!")

    def test_review_create(self):
        # Test that a Review object can be created
        self.assertEqual(Review.objects.count(), 1)

    def test_review_delete(self):
        # Test that a Review object can be deleted
        self.review.delete()
        self.assertEqual(Review.objects.count(), 0)


class OrderModelTest(TestCase):
    def setUp(self):
        # Create a User and Product object for testing
        user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        store = Store.objects.create(name="Test Store", owner=user)
        product = Product.objects.create(
            name="Test Product",
            description="This is a test product",
            price=9.99,
            stock=100,
            store=store,
        )
        # Create an Order object for testing
        self.order = Order.objects.create(user=user, total_price=9.99)
        OrderItem.objects.create(order=self.order, product=product, quantity=1)

    def test_order_has_total_price(self):
        # Test that an Order object has the expected total price
        self.assertEqual(self.order.total_price, 9.99)

    def test_order_create(self):
        # Test that an Order object can be created
        self.assertEqual(Order.objects.count(), 1)

    def test_order_delete(self):
        # Test that an Order object can be deleted
        self.order.delete()
        self.assertEqual(Order.objects.count(), 0)
