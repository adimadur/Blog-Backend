from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Blog, Category, Comment, Like
from .serializers import (
    BlogListSerializer, BlogDetailSerializer, BlogCreateUpdateSerializer,
    CategorySerializer, CommentSerializer, CommentCreateSerializer,
    LikeSerializer, BlogSearchSerializer
)
from .permissions import IsAuthorOrReadOnly, IsCommentAuthorOrReadOnly, BlogPermission

User = get_user_model()


class CategoryListView(generics.ListAPIView):
    """
    List all categories with caching.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

    @method_decorator(cache_page(60 * 60))  # Cache for 1 hour
    @method_decorator(vary_on_cookie)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class BlogListView(generics.ListAPIView):
    """
    List published blogs with filtering, search, and caching.
    """
    serializer_class = BlogListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'author', 'status', 'is_featured']
    search_fields = ['title', 'content', 'excerpt', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'views_count', 'likes_count', 'title']
    ordering = ['-created_at']
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        queryset = Blog.objects.filter(status='published').select_related('author', 'category')
        
        # Filter by author if specified
        author_id = self.request.query_params.get('author_id')
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        
        # Filter by tags
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            for tag in tag_list:
                queryset = queryset.filter(tags__icontains=tag)
        
        return queryset

    @method_decorator(cache_page(60 * 10))  # Cache for 10 minutes
    @method_decorator(vary_on_cookie)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class BlogDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific blog with view count increment.
    """
    queryset = Blog.objects.select_related('author', 'category').prefetch_related('comments', 'likes')
    serializer_class = BlogDetailSerializer
    permission_classes = [BlogPermission]
    lookup_field = 'slug'
    throttle_classes = [UserRateThrottle]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Increment view count for published blogs
        if instance.status == 'published':
            instance.increment_views()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class BlogCreateView(generics.CreateAPIView):
    """
    Create a new blog post.
    """
    serializer_class = BlogCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class BlogUpdateView(generics.UpdateAPIView):
    """
    Update a blog post (author only).
    """
    queryset = Blog.objects.all()
    serializer_class = BlogCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
    lookup_field = 'slug'
    throttle_classes = [UserRateThrottle]


class BlogDeleteView(generics.DestroyAPIView):
    """
    Delete a blog post (author only).
    """
    queryset = Blog.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
    lookup_field = 'slug'
    throttle_classes = [UserRateThrottle]

    def perform_destroy(self, instance):
        instance.delete()


class UserBlogListView(generics.ListAPIView):
    """
    List blogs by a specific user (including drafts for own blogs).
    """
    serializer_class = BlogListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'is_featured']
    ordering_fields = ['created_at', 'updated_at', 'views_count', 'likes_count']
    ordering = ['-created_at']

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        
        # If requesting own blogs, show all including drafts
        if self.request.user == user:
            return Blog.objects.filter(author=user).select_related('author', 'category')
        
        # Otherwise, show only published blogs
        return Blog.objects.filter(author=user, status='published').select_related('author', 'category')


class BlogSearchView(generics.ListAPIView):
    """
    Advanced search for blogs.
    """
    serializer_class = BlogSearchSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        queryset = Blog.objects.filter(status='published').select_related('author', 'category')
        
        # Get search parameters
        q = self.request.query_params.get('q', '')
        category = self.request.query_params.get('category', '')
        author = self.request.query_params.get('author', '')
        tags = self.request.query_params.get('tags', '')
        
        # Apply filters
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(content__icontains=q) |
                Q(excerpt__icontains=q) |
                Q(tags__icontains=q)
            )
        
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        
        if author:
            queryset = queryset.filter(
                Q(author__username__icontains=author) |
                Q(author__first_name__icontains=author) |
                Q(author__last_name__icontains=author)
            )
        
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            for tag in tag_list:
                queryset = queryset.filter(tags__icontains=tag)
        
        return queryset.distinct()


class CommentListView(generics.ListCreateAPIView):
    """
    List and create comments for a blog.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        blog_slug = self.kwargs.get('blog_slug')
        blog = get_object_or_404(Blog, slug=blog_slug)
        return Comment.objects.filter(blog=blog, is_approved=True, parent=None).select_related('author')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        blog_slug = self.kwargs.get('blog_slug')
        blog = get_object_or_404(Blog, slug=blog_slug)
        serializer.save(author=self.request.user, blog=blog)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a comment.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentAuthorOrReadOnly]
    throttle_classes = [UserRateThrottle]


@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def toggle_like(request, blog_slug):
    """
    Toggle like/unlike for a blog.
    """
    blog = get_object_or_404(Blog, slug=blog_slug)
    user = request.user
    
    if request.method == 'POST':
        like, created = Like.objects.get_or_create(blog=blog, user=user)
        if created:
            return Response({'message': 'Blog liked successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Blog already liked'}, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        try:
            like = Like.objects.get(blog=blog, user=user)
            like.delete()
            return Response({'message': 'Blog unliked successfully'}, status=status.HTTP_200_OK)
        except Like.DoesNotExist:
            return Response({'message': 'Blog not liked'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def featured_blogs(request):
    """
    Get featured blogs.
    """
    blogs = Blog.objects.filter(status='published', is_featured=True).select_related('author', 'category')
    serializer = BlogListSerializer(blogs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def popular_blogs(request):
    """
    Get popular blogs based on views and likes.
    """
    blogs = Blog.objects.filter(status='published').select_related('author', 'category').order_by('-views_count', '-likes_count')[:10]
    serializer = BlogListSerializer(blogs, many=True)
    return Response(serializer.data) 