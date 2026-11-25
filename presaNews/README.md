# presaNews

## A Example project to simulate a newsletter website

Newsletter task project for school. Can register as a Reader, Editor, or Journalist. Journalist can create, edit, delete articles and newsletters. Editors can edit, delete, and approve articles and newsletters. Readers can view approved articles and newsletters and subscribe to publishers or journalists.

## Installation

1. Clone the repository(or download the ZIP and extract): git clone https://github.com/MF26050020547/presaNews.git

cd presaNews

2. Create and activate a virtual environment (recommended): On Windows: python -m venv venv venv\\Scripts\\activate On macOS/Linux: python3 -m venv venv source venv/bin/activate
3. Install the required Python packages: pip install -r requirements.txt
4. Configure Email Settings: For sending emails (like password resets), update your email credentials in presaNews/settings.py under the email section: EMAIL\_HOST\_USER = 'your-email@example.com' EMAIL\_HOST\_PASSWORD = 'your-email-password-or-app-password' Note: For Gmail, you might need to create an App Password and enable "Less secure app access".

## Database Setup

1. Create MySQL database: Login to your MySQL server and create the database: CREATE DATABASE presanews\_db;
2. Update database credentials in presaNews/settings.py if your MySQL username or password differ: DATABASES = { 'default': { 'ENGINE': 'django.db.backends.mysql', 'NAME': 'presanews\_db', 'USER': 'root', 'PASSWORD': 'your\_mysql\_password', 'HOST': 'localhost', 'PORT': '', } }
3. Install MySQL Python adapter if not already installed: pip install mysqlclient
4. Apply migrations: Run the following commands to create the necessary database tables: python manage.py makemigrations python manage.py migrate
5. Create a superuser (for admin access): python manage.py createsuperuser Follow the prompts to create a user with admin privileges.

## Usage

Run the development server: python manage.py runserver Access the application: Open your browser and go to: http://127.0.0.1:8000/ You can login, register new users, browse products, and test password reset functionality.

Authentication (grabsomore app): Login at / (root URL) Register at /register/ Request password reset at /request-password-reset/ Reset password via emailed token link presaNews (presaNews app): View all Articles and Newsletters at / (root URL, depending on project URL setup) View Articles. Edit Articles(if authorized), add articles, delete articles. View Newsletters(if authorized), add newsletters, delete newsletters, edit newsletters.

## Password Reset Testing

If you want to test password reset functionality without sending real emails:

1. Change email backend in presaNews/settings.py to console: EMAIL\_BACKEND = "django.core.mail.backends.console.EmailBackend"
2. When you submit a password reset request, the reset link will print in your console/terminal.
3. Copy and paste the link into your browser to reset the password.

## Troubleshooting

MySQL Client Missing Error: If you get ModuleNotFoundError: No module named 'mysqlclient', install it with: pip install mysqlclient SMTP Authentication Error: Make sure you use correct email and password. For Gmail, you might need to use App Passwords instead of your regular password. Static files not loading: During development, Django serves static files automatically. For production, you need to configure static files properly.
