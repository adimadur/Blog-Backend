# Django Blogging Platform

A complete, scalable Django backend for a blogging website with comprehensive features including user authentication, CRUD operations, and advanced security measures.

## Features

### 🔐 Authentication & Security
- Custom User model with extended profile fields
- JWT Token-based authentication
- Password validation and secure password change
- Rate limiting (100/hour for anonymous, 1000/hour for authenticated users)
- CORS protection with configurable origins
- Input validation and sanitization
- XSS protection and security headers

### 📝 Blog Management
- Full CRUD operations for blog posts
- Rich text content with image support
- Blog categories and tagging system
- Draft, published, and archived status
- SEO optimization with meta titles and descriptions
- Reading time calculation
- View and like tracking

### 💬 Social Features
- Comment system with nested replies
- Like/unlike functionality
- User profiles with bio and social links
- Public and private profile views

### 🔍 Advanced Features
- Advanced search with multiple filters
- Pagination and ordering
- Caching for improved performance
- Featured and popular blogs
- User-specific blog management

## Tech Stack

- **Backend**: Django 4.2.7 + Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: Django REST Framework Tokens
- **Caching**: Django's built-in caching
- **File Storage**: Local storage (configurable for S3)
- **Deployment**: Docker + Docker Compose + Nginx

## Project Structure

```
blog_backend/
├── blog_backend/          # Main Django project
│   ├── settings.py       # Django settings with security config
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── users/                # User management app
│   ├── models.py         # Custom User model
│   ├── serializers.py    # User serializers
│   ├── views.py          # Authentication views
│   └── urls.py           # User URLs
├── blogs/                # Blog management app
│   ├── models.py         # Blog, Category, Comment, Like models
│   ├── serializers.py    # Blog serializers
│   ├── views.py          # Blog CRUD views
│   ├── permissions.py    # Custom permissions
│   └── urls.py           # Blog URLs
├── management/           # Custom management commands
├── nginx/               # Nginx configuration
├── Dockerfile           # Production Docker image
├── docker-compose.yml   # Multi-container setup
├── requirements.txt     # Python dependencies
└── env.example          # Environment variables template
```

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL
- Docker & Docker Compose (for containerized deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd blog-backend
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb blog_db
   
   # Run migrations
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **For production deployment**
   ```bash
   docker-compose --profile production up --build
   ```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/logout/` - User logout
- `POST /api/v1/auth/change-password/` - Change password

### User Management
- `GET /api/v1/profile/` - Get user profile
- `PUT /api/v1/profile/` - Update user profile
- `GET /api/v1/users/` - List users (public)
- `GET /api/v1/users/{id}/` - Get user details (public)

### Blog Management
- `GET /api/v1/blogs/` - List published blogs
- `POST /api/v1/blogs/create/` - Create new blog
- `GET /api/v1/blogs/{slug}/` - Get blog details
- `PUT /api/v1/blogs/{slug}/update/` - Update blog
- `DELETE /api/v1/blogs/{slug}/delete/` - Delete blog
- `GET /api/v1/users/{user_id}/blogs/` - Get user's blogs

### Blog Interactions
- `POST /api/v1/blogs/{slug}/like/` - Like blog
- `DELETE /api/v1/blogs/{slug}/like/` - Unlike blog
- `GET /api/v1/blogs/{slug}/comments/` - Get blog comments
- `POST /api/v1/blogs/{slug}/comments/` - Add comment
- `PUT /api/v1/comments/{id}/` - Update comment
- `DELETE /api/v1/comments/{id}/` - Delete comment

### Categories & Search
- `GET /api/v1/categories/` - List categories
- `GET /api/v1/blogs/search/` - Search blogs
- `GET /api/v1/blogs/featured/` - Get featured blogs
- `GET /api/v1/blogs/popular/` - Get popular blogs

## Security Features

### Input Validation
- Comprehensive field validation
- SQL injection prevention
- XSS protection
- File upload validation

### Rate Limiting
- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour
- Configurable per endpoint

### CORS Protection
- Configurable allowed origins
- Secure cookie handling
- CSRF protection

### Authentication Security
- Strong password validation
- Token-based authentication
- Session security
- Secure password change

## Environment Variables

Copy `env.example` to `.env` and configure:

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DB_NAME=blog_db
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Deployment

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Generate secure `SECRET_KEY`
- [ ] Configure production database
- [ ] Set up SSL certificates
- [ ] Configure CORS origins
- [ ] Set up logging
- [ ] Configure static file serving
- [ ] Set up monitoring

### Docker Production
```bash
# Build production image
docker-compose --profile production up --build -d

# View logs
docker-compose logs -f

# Scale services
docker-compose up --scale web=3
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For support and questions, please open an issue on GitHub or contact me. 