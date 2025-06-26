from django.contrib import admin
from .models import Blog, Category, Comment, Like


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'is_featured', 'views_count', 'likes_count', 'created_at')
    list_filter = ('status', 'is_featured', 'category', 'created_at', 'author')
    search_fields = ('title', 'content', 'excerpt', 'author__username', 'author__email')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views_count', 'likes_count', 'created_at', 'updated_at', 'published_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'content', 'excerpt', 'featured_image')
        }),
        ('Metadata', {
            'fields': ('author', 'category', 'status', 'is_featured', 'allow_comments')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'tags'),
            'classes': ('collapse',)
        }),
        ('Analytics', {
            'fields': ('views_count', 'likes_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'author', 'blog', 'parent', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at', 'blog')
    search_fields = ('content', 'author__username', 'blog__title')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    actions = ['approve_comments', 'disapprove_comments']
    
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} comments were successfully approved.')
    approve_comments.short_description = "Approve selected comments"
    
    def disapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} comments were successfully disapproved.')
    disapprove_comments.short_description = "Disapprove selected comments"


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'blog', 'created_at')
    list_filter = ('created_at', 'blog')
    search_fields = ('user__username', 'blog__title')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',) 