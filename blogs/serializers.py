from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Blog, Category, Comment, Like

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """
    Category serializer for blog categories.
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']


class UserMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal user serializer for blog author information.
    """
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'profile_picture']


class CommentSerializer(serializers.ModelSerializer):
    """
    Comment serializer with nested author information.
    """
    author = UserMinimalSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'parent', 'replies', 'is_approved', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'is_approved', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating comments.
    """
    class Meta:
        model = Comment
        fields = ['content', 'parent']
    
    def validate_parent(self, value):
        if value and value.blog != self.context['blog']:
            raise serializers.ValidationError("Parent comment must belong to the same blog.")
        return value


class BlogListSerializer(serializers.ModelSerializer):
    """
    Serializer for blog list view with minimal information.
    """
    author = UserMinimalSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    reading_time = serializers.ReadOnlyField()
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'slug', 'excerpt', 'featured_image', 'author', 'category',
            'status', 'is_featured', 'views_count', 'likes_count', 'reading_time',
            'comments_count', 'created_at', 'published_at'
        ]
        read_only_fields = fields
    
    def get_comments_count(self, obj):
        return obj.comments.filter(is_approved=True).count()


class BlogDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for blog detail view with full information.
    """
    author = UserMinimalSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    reading_time = serializers.ReadOnlyField()
    is_liked_by_user = serializers.SerializerMethodField()
    tags_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'featured_image', 'author', 'category',
            'status', 'is_featured', 'allow_comments', 'meta_title', 'meta_description',
            'tags', 'tags_list', 'views_count', 'likes_count', 'reading_time',
            'is_liked_by_user', 'comments', 'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = ['id', 'slug', 'author', 'views_count', 'likes_count', 'reading_time', 'created_at', 'updated_at', 'published_at']
    
    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_tags_list(self, obj):
        if obj.tags:
            return [tag.strip() for tag in obj.tags.split(',') if tag.strip()]
        return []


class BlogCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating blogs.
    """
    class Meta:
        model = Blog
        fields = [
            'title', 'content', 'excerpt', 'featured_image', 'category',
            'status', 'is_featured', 'allow_comments', 'meta_title', 'meta_description', 'tags'
        ]
    
    def validate_title(self, value):
        # Check for duplicate titles by the same author
        user = self.context['request'].user
        if Blog.objects.filter(author=user, title=value).exists():
            if self.instance and self.instance.title == value:
                return value
            raise serializers.ValidationError("You already have a blog post with this title.")
        return value
    
    def validate_content(self, value):
        # Basic content validation
        if len(value.strip()) < 100:
            raise serializers.ValidationError("Content must be at least 100 characters long.")
        return value
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer for blog likes.
    """
    user = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class BlogSearchSerializer(serializers.ModelSerializer):
    """
    Serializer for blog search results.
    """
    author = UserMinimalSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    reading_time = serializers.ReadOnlyField()
    
    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'slug', 'excerpt', 'author', 'category',
            'views_count', 'likes_count', 'reading_time', 'created_at'
        ]
        read_only_fields = fields 