from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from .models import OrderItem, Product, Store, Review, Order
from datetime import datetime
from .utils import build_email
from django.core.mail import send_mail


def leave_review(request, product_id):
    user = request.user  # Get the currently logged-in user

    if user.has_perm("eCommerce.add_review"):
        if request.method == "POST":
            rating = request.POST.get("rating")
            comment = request.POST.get("comment")

            if rating and comment:
                try:
                    product = Product.objects.get(id=product_id)
                    verified = False  # Set the review as unverified initially
                    temp = Order.objects.filter(user=user)
                    for order in temp:
                        if order.products.filter(id=product_id).exists():
                            verified = True
                            break

                    review = Review.objects.create(
                        user=user,
                        product=product,
                        rating=rating,
                        comment=comment,
                        verified=verified
                    )

                    
                    return redirect(reverse("eCommerce:product_page", args=[product_id]))
                except Product.DoesNotExist:
                    return render(
                        request,
                        "eCommerce/product_page.html",
                        {"error": "Product not found."},
                    )
            else:
                return render(
                    request,
                    "eCommerce/leave_review.html",
                    {"error": "Please provide both a rating and a comment."},
                )
        else:
            return render(
                request,
                "eCommerce/leave_review.html",
            )
    else:
        return render(
            request,
            "eCommerce/products_list.html",
            {"error": "You do not have permission to leave reviews."},
        )    


def product_page(request, product_id):
    try:
        product = Product.objects.get(id=product_id)  # Get the product with the specified ID
        reviews = Review.objects.filter(product=product)
    except Product.DoesNotExist:
        return render(
            request,
            "eCommerce/product_page.html",
            {"error": "Product not found."},
        )



    return render(request, "eCommerce/product_page.html", {"product": product, "reviews": reviews})


def change_store_name(request, store_id):
    user = request.user  # Get the currently logged-in user

    # Check if user has permission to change stores
    if user.has_perm("eCommerce.change_store"):
        try:
            store = Store.objects.get(id=store_id)  # Get the store with the specified ID
        except Store.DoesNotExist:
            return render(
                request,
                "eCommerce/change_store_name.html",
                {"error": "Store not found."},
            )

        if request.method == "POST":
            new_name = request.POST.get("store_name")  # Get new name from form submission

            # Validate that new name is provided
            if not new_name:
                return render(
                    request,
                    "eCommerce/change_store_name.html",
                    {"error": "Please provide a new name.", "store": store},
                )

            store.name = new_name  # Update the store's name
            store.save()  # Save changes to the database
            return redirect(reverse("eCommerce:edit_store"))  # Redirect to edit store page after change

        # Show form when page is first loaded (GET request)
        return render(request, "eCommerce/change_store_name.html", {"store": store})

    else:
        return render(
            request,
            "eCommerce/edit_store.html",
            {"error": "You do not have permission to change store names."},
        )


def delete_store(request, store_id):
    user = request.user  # Get the currently logged-in user

    # Check if user has permission to delete stores
    if user.has_perm("eCommerce.delete_store"):
        try:
            store = Store.objects.get(id=store_id)  # Get the store with the specified ID
            store.delete()  # Delete the store from the database
            return redirect(reverse("eCommerce:edit_store"))  # Redirect to edit store page after deletion
        except Store.DoesNotExist:
            return render(
                request,
                "eCommerce/edit_store.html",
                {"error": "Store not found."},
            )
    else:
        return render(
            request,
            "eCommerce/edit_store.html",
            {"error": "You do not have permission to delete stores."},
        )


def view_order_history(request):
    user = request.user  # Get the currently logged-in user

    # Check if user has permission to view orders
    if user.has_perm("eCommerce.view_order"):
        orders = Order.objects.filter(user=user.id)  # Get all orders for the user

        items = OrderItem.objects.filter(order__in=orders)  # Get all items for the user's orders

        return render(request, "eCommerce/order_history.html", {"orders": orders, "items": items})

    else:
        return render(
            request,
            "eCommerce/order_history.html",
            {"error": "You do not have permission to view order history."},
        )


def checkout(request):
    # Get the currently logged-in user
    user = request.user

    # Get the products in the user's cart
    cart_items = retrieve_products(request)

    # Calculate the total price of items in the cart
    subtotal = calculate_cart_total(request)

    # Get the current date and time
    current_datetime = datetime.now()

    order = Order.objects.create(
        user=user, total_price=subtotal, created_at=current_datetime)

    for item in cart_items:
        OrderItem.objects.create(
            order=order, product=item["product"], quantity=item["quantity"])
        Product.objects.filter(id=item["product"].id).update(stock=item["product"].stock - item["quantity"])

    email = build_email(user, order, cart_items)
    email.send()  # Send the order confirmation email

    clear_cart(request)  # Clear the cart after checkout

    # Render the checkout page with the current date and time
    return view_order_history(request)  # Redirect to order history after checkout


def add_store(request):
    user = request.user  # Get the currently logged-in user

    # Check if user has permission to add stores
    if user.has_perm("eCommerce.add_store"):
        if request.method == "POST":
            store_name = request.POST.get("store_name")

            # Validate that store name is provided
            if not store_name:
                return render(
                    request,
                    "eCommerce/add_store.html",
                    {"error": "Store name is required."},
                )

            # Create a new store instance and save it to the database
            store = Store.objects.create(name=store_name, owner=user)
            return redirect(reverse("eCommerce:edit_store"))
        else:
            # Show form when page is first loaded (GET request)
            return render(request, "eCommerce/add_store.html")

    else:
        return render(
            request,
            "eCommerce/add_store.html",
            {"error": "You do not have permission to add stores."},
        )


def add_product(request, store_id):
    user = request.user  # Get the currently logged-in user
    store = Store.objects.get(id=store_id)  # Get the store with the specified ID

    # Check if user has permission to add products
    if user.has_perm("eCommerce.add_product"):
        if request.method == "POST":
            product_name = request.POST.get("product_name")
            description = request.POST.get("description")
            price = request.POST.get("price")
            stock = request.POST.get("stock")

            # Validate that all fields are provided
            if not all([product_name, description, price, stock]):
                return render(
                    request,
                    "eCommerce/add_product.html",
                    {"error": "All fields are required."},
                )

            try:
                # Create a new product instance and save it to the database
                product = Product.objects.create(
                    name=product_name,
                    description=description,
                    price=float(price),
                    stock=int(stock),
                    store=Store.objects.get(id=store_id),
                )
                return redirect(reverse("eCommerce:vendor_store", args=[store_id]))
            except ValueError:
                return render(
                    request,
                    "eCommerce/add_product.html",
                    {"error": "Invalid input for price or stock."},
                )

        # Show form when page is first loaded (GET request)
        return render(request, "eCommerce/add_product.html", {"store": store})

    else:
        return render(
            request,
            "eCommerce/add_product.html",
            {"error": "You do not have permission to add products."},
        )


def delete_product(request, product_id):
    user = request.user  # Get the currently logged-in user

    # Check if user has permission to delete products
    if user.has_perm("eCommerce.delete_product"):
        try:
            product = Product.objects.get(id=product_id)  # Get the product with the specified ID
            id = product.id  # Store the product ID for redirection
            product.delete()  # Delete the product from the database
            return redirect(reverse("eCommerce:vendor_store", kwargs={"store_id": id}))  # Redirect to vendor store after deletion
        except Product.DoesNotExist:
            return render(
                request,
                "eCommerce/product_detail.html",
                {"error": "Product not found."},
            )
    else:
        return render(
            request,
            "eCommerce/product_detail.html",
            {"error": "You do not have permission to delete products."},
        )


def show_vendor_store(request, store_id):

    store = Store.objects.get(id=store_id)  # Get the store with the specified ID
    products = store.products.all()  # Get all products in the store
    return render(request, "eCommerce/vendor_store.html", {"store": store, "products": products})


def edit_store(request):
    user = request.user  # Get the currently logged-in user

    if user.has_perm("eCommerce.change_store"):
        store = user.store_set.all()  # get all stores owned by the user
        return render(request, "eCommerce/edit_store.html", {"stores": store})

    else:
        return render(
            request,
            "grabsomore/welcome.html",
            {"error": "You do not have permission to edit stores."},
        )


def product_detail(request, product_id):
    user = request.user  # Get the currently logged-in user

    if user.has_perm("eCommerce.change_product"):
        try:
            product = Product.objects.get(id=product_id)  # Get the product with the specified ID
            reviews = Review.objects.filter(product=product)
        except Product.DoesNotExist:
            return render(
                request,
                "eCommerce/product_detail.html",
                {"error": "Product not found."},
            )

        return render(request, "eCommerce/product_detail.html", {"product": product, "reviews": reviews})

    else:
        return render(
            request,
            "eCommerce/product_detail.html",
            {"error": "You do not have permission to edit products."},
        )


def search_product_page(request):
    user = request.user  # Get the current logged-in user

    # Check if user has permission to view products
    if user.has_perm("eCommerce.view_product") or user.has_perm(
        "eCommerce.view_products"
    ):
        if request.method == "POST":
            product_name = request.POST.get(
                "product"
            )  # Get product name from form submission

            if not product_name:
                # If no product name given, show error on page
                return render(
                    request,
                    "eCommerce/search_product.html",
                    {"error": "No product name was given."},
                )

            try:
                # Try to find the product in the database by its name
                product = Product.objects.get(name=product_name)
                reviews = Review.objects.filter(product=product)
                # Show product details on the page
                return render(
                    request, "eCommerce/search_product.html", {"product": product, "reviews": reviews}
                )
            except ObjectDoesNotExist:
                # If product not found, show error on page
                return render(
                    request,
                    "eCommerce/search_product.html",
                    {"error": "Product not found."},
                )

        # If page is opened normally (GET request), just show empty form
        return render(request, "eCommerce/search_product.html")

    # If user does not have permission to view products, show error
    return render(
        request,
        "eCommerce/search_product.html",
        {"error": "You do not have permission to view this product."},
    )


def add_item_to_cart(request):
    # Get item name and quantity from POST form submission
    item = request.POST.get("item")
    quantity = request.POST.get("quantity")

    # If either is missing, redirect to cart page without changing anything
    if not item or not quantity:
        return redirect("eCommerce:main_cart_page")

    try:
        # Convert quantity to integer, and set to 1 if invalid or less than 1
        quantity = int(quantity)
        if quantity < 1:
            quantity = 1
    except ValueError:
        quantity = 1

    # Get existing cart from session, or empty dictionary if none
    cart = request.session.get("cart", {})

    # If item already in cart, add to existing quantity, otherwise add new item
    if item in cart:
        cart[item] += quantity
    else:
        cart[item] = quantity

    # Save updated cart back into session so it persists
    request.session["cart"] = cart
    request.session.modified = True  # Mark session as changed

    # Redirect user to cart page after adding item
    return redirect(reverse("eCommerce:main_cart_page"))


def retrieve_products(request):
    products = []
    session = request.session

    # If cart exists in session, load products and their quantities
    if "cart" in session:
        for name, quantity in session["cart"].items():
            try:
                # Get product from database by name
                product = Product.objects.get(name=name)
                # Add product and quantity as a dictionary to list
                products.append({"product": product, "quantity": quantity})
            except Product.DoesNotExist:
                # Skip if product not found (may have been deleted)
                pass

    return products


def show_user_cart(request):
    # Get list of products and quantities from the session cart
    cart_items = retrieve_products(request)

    # Calculate total price of items in cart
    total_price = calculate_cart_total(request)

    # Render cart page, passing in items and total price
    return render(
        request,
        "eCommerce/main_cart_page.html",
        {
            "cart": cart_items,
            "total_price": total_price,
        },
    )


def list_products(request):
    # Get all products from database
    products = Product.objects.all()
    # Show products list page, passing products to template
    return render(request, "eCommerce/products_list.html", {"products": products})


def clear_cart(request):
    # Empty the cart by setting session cart to empty dictionary
    request.session["cart"] = {}
    request.session.modified = True  # Mark session as changed

    # Redirect to cart page after clearing
    return redirect("eCommerce:main_cart_page")


def change_product_price(request, product_id):
    user = request.user  # Get the currently logged-in user

    # Find the product in the database
    product = Product.objects.get(id=product_id)

    # Check if user has permission to change products
    if user.has_perm("eCommerce.change_product") or user.has_perm(
        "eCommerce.change_products"
    ):
        if request.method == "POST":
            new_name = request.POST.get("new_name")  # Get new name from form
            new_description = request.POST.get("new_description")  # Get new description from form
            new_price = request.POST.get("new_price")  # Get new price from form
            new_stock = request.POST.get("new_stock")  # Get new stock from form

            if not new_name:
                new_name = product.name  # If no new name provided, keep existing name
            if not new_description:
                new_description = product.description  # If no new description provided, keep existing description
            if not new_price:
                new_price = product.price  # If no new price provided, keep existing price
            if not new_stock:
                new_stock = product.stock  # If no new stock provided, keep existing stock

            try:

                # Convert new price to float (decimal number)
                product.price = float(new_price)
                product.name = new_name
                product.description = new_description
                product.stock = int(new_stock)
                product.save()  # Save updated product details to database

                # After success, redirect user to product page
                return HttpResponseRedirect(reverse("eCommerce:product_detail", args=[product_id]))
            except ValueError:
                # If new price isn't a valid number, show error
                return render(
                    request,
                    "eCommerce/change_price.html",
                    {"error": "Invalid price format."},
                )
            except ObjectDoesNotExist:
                # If product name does not exist in database, show error
                return render(
                    request,
                    "eCommerce/change_price.html",
                    {"error": "Product not found."},
                )

        # Show form when page is first loaded (GET request)
        return render(request, "eCommerce/change_price.html", {"product": product})

    # If user does not have permission, show error
    return render(
        request,
        "eCommerce/change_price.html",
        {"error": "You do not have permission to change prices."},
    )


def calculate_cart_total(request):
    cart_items = retrieve_products(request)  # Get the products in the user's cart

    total_price = 0  # Start total price at zero

    # Calculate subtotal for each cart item and total price for whole cart
    for item in cart_items:
        subtotal = item["product"].price * item["quantity"]
        item["subtotal"] = subtotal  # Add subtotal to item dictionary
        total_price += subtotal

    return total_price