# Trade-Hub: Multi-Vendor E-Commerce Platform

a simple multi-vendor marketplace built with django. vendors can sell stuff, buyers can buy stuff. pretty straightforward.

## what it does

### for buyers
- browse products by category or vendor
- search and filter products
- shopping cart functionality
- order tracking
- user accounts

### for vendors
- register your store easily
- add and manage products via web or api
- dashboard to track sales
- inventory management
- api endpoints for automated product creation
- twitter integration posts when you add stuff

### technical stuff
- rest api with authentication
- token-based api access
- automatic twitter posting
- responsive design
- admin panel
- secure auth system

## tech stack

- django 5.2.6
- tailwind css
- sqlite database
- django rest framework
- tweepy for twitter
- pillow for images

## setup

### what you need
- python 3.8+
- git

### installation

1. **get the code**
   ```bash
   git clone <repository-url>
   cd Ecommerce_take2
   ```

2. **set up virtual environment**
   ```bash
   python -m venv venv
   # windows
   venv\Scripts\activate
   # mac/linux
   source venv/bin/activate
   ```

3. **install stuff**
   ```bash
   pip install django tweepy Pillow djangorestframework python-dotenv
   ```

4. **set up environment variables**
   Create a `.env` file in the root directory with the following variables:
   ```env
   # Basic Django Settings
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Database Settings (optional - defaults to SQLite)
   DATABASE_TYPE=sqlite
   # For MariaDB/MySQL:
   # DATABASE_TYPE=mariadb
   # DB_NAME=tradehub_db
   # DB_USER=tradehub_user
   # DB_PASSWORD=your_password
   # DB_HOST=localhost
   # DB_PORT=3306
   
   # Email Settings
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=Trade-Hub <noreply@tradehub.com>
   SERVER_EMAIL=Trade-Hub <admin@tradehub.com>
   
   # Twitter API Settings (optional - for social media integration)
   TWITTER_API_KEY=your-twitter-api-key
   TWITTER_API_SECRET=your-twitter-api-secret
   TWITTER_ACCESS_TOKEN=your-twitter-access-token
   TWITTER_ACCESS_TOKEN_SECRET=your-twitter-access-token-secret
   
   # Security Settings (for production)
   # SECURE_SSL_REDIRECT=True
   # SECURE_HSTS_SECONDS=31536000
   ```

5. **run migrations**
   ```bash
   python manage.py migrate
   ```

6. **create categories**
   ```bash
   python manage.py create_default_categories
   ```
   
   this sets up basic categories like electronics, clothing, etc. so vendors can actually add products

7. **create admin user (optional)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Start development server**
   ```bash
   python manage.py runserver
   ```

9. **Visit the application**
   Open your browser and go to `http://127.0.0.1:8000/`

## Important Setup Notes

### Email Configuration
For email functionality (order confirmations, vendor notifications):
- **Gmail Users**: Use an App Password instead of your regular password
- **Development**: Set `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'` in settings.py to see emails in console
- **Production**: Configure proper SMTP settings in your `.env` file

### Twitter Integration (Optional)
- Create a Twitter Developer Account and get API keys
- Add the keys to your `.env` file to enable automatic tweeting for new products/vendors

### Database Options
- **SQLite (default)**: No setup required, perfect for development
- **MariaDB/MySQL**: Set `DATABASE_TYPE=mariadb` in `.env` and provide connection details

## Project Structure

```
tradehub/
├── core/                 # Main app (homepage, search, contact)
├── vendors/             # Vendor management
├── products/            # Product and category management
├── orders/              # Cart and order management
├── api/                 # REST API endpoints
├── templates/           # HTML templates
├── static/              # Static files (CSS, JS, images)
├── media/               # User uploads
└── tradehub/            # Django project settings
```

## API Endpoints

### Read-Only Endpoints
- `GET /api/v1/products/` - List all products
- `GET /api/v1/products/{id}/` - Get product details
- `GET /api/v1/categories/` - List all categories
- `GET /api/v1/categories/{id}/` - Get category details
- `GET /api/v1/vendors/` - List all vendors
- `GET /api/v1/vendors/{id}/` - Get vendor details
- `GET /api/v1/search/?q=<query>` - Search products

### Write-Capable Authenticated Endpoints
- `POST /api/v1/auth/token/` - Get API authentication token
- `POST /api/v1/vendors/` - Create a new vendor store (requires authentication)
- `POST /api/v1/products/` - Create a new product (requires vendor authentication)

### API Documentation
See `API_DOCUMENTATION.md` for complete API usage examples and authentication details.

### Twitter Integration
When vendors create stores or products via the API, the system automatically posts announcements to Twitter (requires Twitter API credentials).

## Configuration

### Additional Configuration Notes
The complete environment configuration is covered in the setup section above. All optional settings have sensible defaults for development.

### Customization

#### Site Settings
Update site information in the Django admin panel under "Site Settings" or modify the footer in `templates/base.html`.

#### Styling
- The project uses Tailwind CSS via CDN for styling
- Custom CSS can be added to `templates/base.html`
- Modify color schemes and branding as needed

#### Social Media Links
Update social media links in the footer section of `templates/base.html`.

## Development

### Adding New Features
1. Create new Django apps as needed
2. Add models to represent your data
3. Create views to handle business logic
4. Add templates for the user interface
5. Update URL configurations

### Database Migrations
After making model changes:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Testing
```bash
python manage.py test
```

## Deployment

### Production Checklist
1. Set `DEBUG = False` in settings
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving
4. Configure media file handling
5. Set up SSL/HTTPS
6. Configure environment variables
7. Set up backup systems

### Docker (Optional)
Create a `Dockerfile` for containerized deployment:

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

- **Documentation**: Check Django documentation for framework-specific questions
- **Issues**: Report bugs and request features via GitHub issues
- **Community**: Join Django community forums for general questions

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- Django team for the excellent web framework
- Tailwind CSS for the utility-first CSS framework
- Font Awesome for the icon library
- Contributors and the open-source community

---

**Get Started Today!** Clone the repository and start building your multi-vendor e-commerce platform with Trade-Hub.