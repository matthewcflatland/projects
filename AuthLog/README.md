# eCommerce Task

## A Example project to simulate a eCommerce website

Ecommerce task project for school. Can register as a vendor or shopper. Vendors can create stores and add products to the stores. Shoppers can add products to their carts and create purchase orders.


## Installation

1. Clone the repository(or download the ZIP and extract):
git clone https://github.com/MF26050020547/AthLog.git

cd AuthLog

2. Create and activate a virtual environment (recommended):
On Windows:
python -m venv venv
venv\Scripts\activate
On macOS/Linux:
python3 -m venv venv
source venv/bin/activate

3. Install the required Python packages:
pip install -r requirements.txt

4. Configure Email Settings:
For sending emails (like password resets), update your email credentials in AuthLog/settings.py under the email section:
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-email-password-or-app-password'
Note: For Gmail, you might need to create an App Password and enable "Less secure app access".


## Database Setup
Create MySQL database:
Login to your MySQL server and create the database:
CREATE DATABASE ecommerce_db;
Update database credentials in AuthLog/settings.py if your MySQL username or password differ:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ecommerce_db',
        'USER': 'root',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '',
    }
}
Install MySQL Python adapter if not already installed:
pip install mysqlclient

Apply migrations:
Run the following commands to create the necessary database tables:
python manage.py makemigrations
python manage.py migrate
Create a superuser (for admin access):
python manage.py createsuperuser
Follow the prompts to create a user with admin privileges.


## Usage

Run the development server:
python manage.py runserver
Access the application:
Open your browser and go to: http://127.0.0.1:8000/
You can login, register new users, browse products, and test password reset functionality.

Authentication (grabsomore app):
Login at / (root URL)
Register at /register/
Request password reset at /request-password-reset/
Reset password via emailed token link
eCommerce (eCommerce app):
View all products at / (root URL, depending on project URL setup)
View product details, add to cart, and view cart.
Manage stores(if authorized), add stores, edit stores, delete stores.
View stores(if authorized), add products, delete products, edit products.


## Password Reset Testing
If you want to test password reset functionality without sending real emails:
Change email backend in AuthLog/settings.py to console:
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
When you submit a password reset request, the reset link will print in your console/terminal.
Copy and paste the link into your browser to reset the password.


## Troubleshooting
MySQL Client Missing Error:
If you get ModuleNotFoundError: No module named 'mysqlclient', install it with:
pip install mysqlclient
SMTP Authentication Error:
Make sure you use correct email and password. For Gmail, you might need to use App Passwords instead of your regular password.
Static files not loading:
During development, Django serves static files automatically. For production, you need to configure static files properly.

