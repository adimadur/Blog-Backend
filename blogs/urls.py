from django.urls import path
from . import views

app_name = 'blogs'

urlpatterns = [
    # Category endpoints
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    
    # Blog CRUD endpoints
    path('blogs/', views.BlogListView.as_view(), name='blog-list'),
    path('blogs/create/', views.BlogCreateView.as_view(), name='blog-create'),
    path('blogs/<slug:slug>/', views.BlogDetailView.as_view(), name='blog-detail'),
    path('blogs/<slug:slug>/update/', views.BlogUpdateView.as_view(), name='blog-update'),
    path('blogs/<slug:slug>/delete/', views.BlogDeleteView.as_view(), name='blog-delete'),
    
    # User blogs
    path('users/<uuid:user_id>/blogs/', views.UserBlogListView.as_view(), name='user-blogs'),
    
    # Blog interactions
    path('blogs/<slug:blog_slug>/like/', views.toggle_like, name='toggle-like'),
    path('blogs/<slug:blog_slug>/comments/', views.CommentListView.as_view(), name='comment-list'),
    path('comments/<uuid:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),
    
    # Special blog endpoints
    path('blogs/featured/', views.featured_blogs, name='featured-blogs'),
    path('blogs/popular/', views.popular_blogs, name='popular-blogs'),
    path('blogs/search/', views.BlogSearchView.as_view(), name='blog-search'),
] 