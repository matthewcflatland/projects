from django.urls import path
from . import views

app_name = "eCommerce"  # This helps Django know these URLs belong to the eCommerce app

urlpatterns = [
    # Home page: Shows the list of all products
    path("", views.list_products, name="products_list"),
    # Page to view details about a specific product (with a search form)
    path("product/", views.search_product_page, name="search_product"),
    #Page to view details about a sepcific product
    path("product/<int:product_id>/", views.product_page, name="product_page"),
    # Page to change the price of a product (for users with permission)
    path("change-price/<int:product_id>/", views.change_product_price, name="change_price"),
    # URL to add an item to the shopping cart (usually called by a form)
    path("add-to-cart/", views.add_item_to_cart, name="add_to_cart"),
    # Page showing all items currently in the user's cart with totals
    path("cart/", views.show_user_cart, name="main_cart_page"),
    # URL to clear all items from the user's cart
    path("clear-cart/", views.clear_cart, name="clear_cart"),
    # URL to show vendor store
    path("store/<int:store_id>/", views.show_vendor_store, name="vendor_store"),
    # URL to edit store
    path("edit-store/", views.edit_store, name="edit_store"),
    # URL to view product details
    path("product-details/<int:product_id>/", views.product_detail, name="product_detail"),
    # URL to delete a product
    path("delete-product/<int:product_id>/", views.delete_product, name="delete_product"),
    # URL to add a new product
    path("add-product/<int:store_id>/", views.add_product, name="add_product"),
    # URL to add a new store
    path("add-store/", views.add_store, name="add_store"),
    # URL to view the checkout page
    path("checkout/", views.checkout, name="checkout"),
    # URL to view the order history page
    path("order-history/", views.view_order_history, name="order_history"),
    # URL to delete store
    path("delete-store/<int:store_id>/", views.delete_store, name="delete_store"),
    # URL to change store name
    path("change-store-name/<int:store_id>/", views.change_store_name, name="change_store_name"),
    # URL to leave a review for a product
    path("leave-review/<int:product_id>/", views.leave_review, name="leave_review"),
]
